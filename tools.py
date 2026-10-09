"""tools.py - STUDENT IMPLEMENTS.  Source tools for the research agents.   Guide: GUIDE.md, part 1.

Rules for every tool:
  * runs on the HOST (not in the sandbox): API keys must never enter the sandbox;
  * returns a STRING (JSON text of compact records) and NEVER raises:
        "NO RESULTS"  when the source answers with nothing,
        "ERROR: ..."  when the source keeps failing after the retries (the agent then tries another source);
  * the docstring is the tool description the LLM reads: keep it precise (what it does, what it returns, when to use it).
Try your tools without any agent:   python tools.py
"""
import json  # noqa: F401
import os  # noqa: F401
import time  # noqa: F401
import xml.etree.ElementTree  # noqa: F401  (arXiv answers with Atom XML)
import random
import re
import threading
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx  # noqa: F401
from langchain_core.tools import tool

# ---- constants (given) ----
ARXIV_URL = "https://export.arxiv.org/api/query"  # https only: http answers 301
HF_DAILY_URL = "https://huggingface.co/api/daily_papers"
HF_SEARCH_URL = "https://huggingface.co/api/papers/search"
EXA_URL = "https://mcp.exa.ai/mcp"
_ARXIV_LOCK = threading.Lock()
_LAST_ARXIV_CALL = 0.0
_RETRY_STATUSES = {429, 500, 502, 503, 504}


class RetryableError(Exception):
    """Given. Raise it inside a call to ask with_retry to wait and try again (retry_after in seconds, optional)."""

    def __init__(self, message, retry_after=None):
        super().__init__(message)
        self.retry_after = retry_after


# ---- TODO 1: retry helper ----
def with_retry(fn, *, attempts=5, base=1.0, cap=30.0):
    """Call fn(); when it raises RetryableError, wait and call it again.

    PSEUDO-CODE:
      for attempt in 0 .. attempts-1:
          try: return fn()
          except RetryableError as e:
              if this was the last attempt: raise
              delay = e.retry_after if the server told us, else exponential backoff base * 2**attempt
              cap the delay at `cap` seconds; add random jitter to the exponential case
              sleep(delay)
    Use it to wrap EVERY network call below. Also treat these as retryable: HTTP 429/500/502/503/504,
    httpx.TransportError (timeouts, connection resets). Read the Retry-After header when present.
    """
    for attempt in range(max(1, attempts)):
        try:
            return fn()
        except RetryableError as exc:
            if attempt == max(1, attempts) - 1:
                raise
            delay = exc.retry_after
            if delay is None:
                delay = min(cap, base * 2 ** attempt) + random.uniform(0, min(base, 1.0))
            time.sleep(min(cap, max(0.0, delay)))


def _clean(value, limit=None):
    text = " ".join(str(value or "").split())
    return text[:limit] if limit else text


def _retry_after(response):
    value = response.headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        try:
            return max(0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError):
            return None


def _request(method, url, **kwargs):
    try:
        response = httpx.request(method, url, timeout=30.0, **kwargs)
        if response.status_code in _RETRY_STATUSES:
            raise RetryableError(f"HTTP {response.status_code}", _retry_after(response))
        response.raise_for_status()
        return response
    except httpx.TransportError as exc:
        raise RetryableError(f"{type(exc).__name__}: {exc}") from exc


def _error(exc, secret=None):
    message = f"ERROR: {type(exc).__name__}: {exc}"
    return message.replace(secret, "[REDACTED]") if secret else message


def _paper_record(item, prefer_ai=False):
    paper = item.get("paper") if isinstance(item, dict) else None
    if isinstance(item, dict) and not isinstance(paper, dict):
        paper = item  # Search responses can be flat; Daily Papers wraps them in "paper".
    if not isinstance(paper, dict) or not paper.get("id"):
        return None
    paper_id = str(paper["id"])
    summary = (paper.get("ai_summary") if prefer_ai else None) or paper.get("summary") or item.get("summary")
    try:
        upvotes = int(paper.get("upvotes") or 0)
        stars = int(paper.get("githubStars") or 0)
    except (TypeError, ValueError):
        upvotes, stars = 0, 0
    return {
        "id": paper_id,
        "url": f"https://huggingface.co/papers/{paper_id}",
        "published": str(paper.get("publishedAt") or item.get("publishedAt") or "")[:10],
        "title": _clean(paper.get("title") or item.get("title")),
        "summary": _clean(summary, 600),
        "upvotes": upvotes,
        "github": paper.get("githubRepo") or "",
        "stars": stars,
    }


# ---- TODO 2: arXiv ----
@tool
def arxiv_search(query: str, max_results: int = 10) -> str:
    """Search arXiv papers by keywords, newest first. Returns a JSON list of {id, url, published, title, summary}."""
    # PSEUDO-CODE:
    #   keep only word characters of `query` -> terms; no terms -> "NO RESULTS" (do not call the network)
    #   respect arXiv etiquette: at least 3 seconds between two arXiv calls (remember the time of the last call)
    #   GET ARXIV_URL params: search_query="all:t1 AND all:t2 ...", sortBy=submittedDate, sortOrder=descending,
    #       max_results=clamp(max_results, 1, 30)           (wrap in with_retry)
    #   parse the Atom XML: each <entry> -> {id (last part of <id> after /abs/), url, published[:10], title, summary}
    #       collapse whitespace/newlines in title and summary; cut summary to ~600 chars
    #   no entries -> "NO RESULTS"; else json.dumps(records, ensure_ascii=False)
    #   any exception -> "ERROR: <type>: <message>"
    try:
        terms = [term for term in re.findall(r"[^\W_]+(?:-[^\W_]+)*", query, re.UNICODE)
                 if term.upper() not in {"AND", "OR", "NOT"}]
        if not terms:
            return "NO RESULTS"
        params = {"search_query": " AND ".join(f"all:{term}" for term in terms),
                  "sortBy": "submittedDate", "sortOrder": "descending",
                  "max_results": max(1, min(int(max_results), 30)), "start": 0}

        def fetch():
            global _LAST_ARXIV_CALL
            with _ARXIV_LOCK:
                remaining = 3.0 - (time.monotonic() - _LAST_ARXIV_CALL)
                if remaining > 0:
                    time.sleep(remaining)
                _LAST_ARXIV_CALL = time.monotonic()
            return _request("GET", ARXIV_URL, params=params)

        root = xml.etree.ElementTree.fromstring(with_retry(fetch, attempts=7, cap=60.0).text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        records = []
        for entry in root.findall("atom:entry", ns):
            raw_id = entry.findtext("atom:id", default="", namespaces=ns).split("/abs/")[-1]
            paper_id = re.sub(r"v\d+$", "", raw_id)
            if not paper_id:
                continue
            records.append({"id": paper_id, "url": f"https://arxiv.org/abs/{paper_id}",
                            "published": entry.findtext("atom:published", default="", namespaces=ns)[:10],
                            "title": _clean(entry.findtext("atom:title", default="", namespaces=ns)),
                            "summary": _clean(entry.findtext("atom:summary", default="", namespaces=ns), 600)})
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


# ---- TODO 3: Hugging Face ----
@tool
def hf_daily_papers(limit: int = 30, date: str = "", keyword: str = "") -> str:
    """Hugging Face Daily Papers = what is trending in AI research. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars} sorted by upvotes. `date` is YYYY-MM-DD (empty = latest).
    `keyword` filters title/summary; there is no topic search on this endpoint (use hf_search_papers for a topic)."""
    # PSEUDO-CODE:
    #   GET HF_DAILY_URL params: limit (clamp 1..100) and date (only when given)      (with_retry)
    #   response = list of items {"paper": {id, title, summary, upvotes, githubRepo, githubStars, publishedAt}, ...}
    #   map every item to the record shape above (skip items without paper.id); url = https://huggingface.co/papers/<id>
    #   keyword -> keep records whose title+summary contains it (case-insensitive); sort by upvotes descending
    try:
        params = {"limit": max(1, min(int(limit), 100))}
        if date:
            params["date"] = date
        items = with_retry(lambda: _request("GET", HF_DAILY_URL, params=params)).json()
        records = [record for item in items if (record := _paper_record(item))]
        if keyword:
            needle = keyword.casefold()
            records = [record for record in records if needle in
                       (record["title"] + " " + record["summary"]).casefold()]
        records.sort(key=lambda record: record["upvotes"], reverse=True)
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


@tool
def hf_search_papers(query: str, limit: int = 10) -> str:
    """Search Hugging Face papers by topic. Returns a JSON list of
    {id, url, published, title, summary, upvotes, github, stars}."""
    # PSEUDO-CODE:
    #   GET HF_SEARCH_URL params: q=query, limit (clamp 1..50)                         (with_retry)
    #   same item shape as the daily endpoint; prefer paper["ai_summary"] over paper["summary"] when present
    try:
        if not query.strip():
            return "NO RESULTS"
        params = {"q": query, "limit": max(1, min(int(limit), 50))}
        items = with_retry(lambda: _request("GET", HF_SEARCH_URL, params=params)).json()
        records = [record for item in items if (record := _paper_record(item, prefer_ai=True))]
        return json.dumps(records, ensure_ascii=False) if records else "NO RESULTS"
    except Exception as exc:
        return _error(exc)


def _exa_call(name, arguments):
    key = os.getenv("EXA_API_KEY", "").strip()
    # Exa's current MCP documentation uses x-api-key, avoiding keys in URLs and exception messages.
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if key:
        headers["x-api-key"] = key
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
               "params": {"name": name, "arguments": arguments}}

    def request():
        response = _request("POST", EXA_URL, headers=headers, json=payload)
        events = []
        for line in response.text.splitlines():
            if line.startswith("data:"):
                data = line[5:].strip()
                if data and data != "[DONE]":
                    events.append(json.loads(data))
        if not events:
            events = [response.json()]
        result = events[-1]
        if "error" in result:
            error_text = str(result["error"])
            if "ratelimit" in re.sub(r"[^a-z0-9]", "", error_text.lower()):
                raise RetryableError("Exa rate limited")
            raise RuntimeError(error_text)
        result = result.get("result", {})
        content = "\n".join(block.get("text", "") for block in result.get("content", [])
                            if block.get("type") == "text")
        meta = result.get("_meta") or {}
        meta_text = json.dumps(meta, ensure_ascii=False).lower()
        combined = re.sub(r"[^a-z0-9]", "", meta_text + " " + content.lower())
        if any(marker in combined for marker in
               ("ratelimit", "toomanyrequests", "quotaexceeded")):
            raise RetryableError("Exa rate limited", retry_after=20 if not key else None)
        if result.get("isError"):
            raise RuntimeError(content or "Exa tool error")
        return content

    try:
        content = with_retry(request, attempts=7 if key else 4, cap=60.0) or "NO RESULTS"
        return content.replace(key, "[REDACTED]") if key else content
    except Exception as exc:
        return _error(exc, key)


# ---- TODO 4: web search / fetch through the Exa MCP endpoint ----
@tool
def web_search(query: str, objective: str = "", num_results: int = 5) -> str:
    """Search the web (Exa). Describe the ideal page in natural language. Returns clean text of the top results with URLs."""
    # PSEUDO-CODE:
    #   call the MCP tool "web_search_exa" with arguments {query, objective, numResults}
    #       (objective is REQUIRED by Exa: when empty, build one from the query)
    #   see GUIDE.md part 1.4 for how to call an MCP server over plain HTTP (JSON-RPC "tools/call") and read the answer
    #   read optional env EXA_API_KEY; when present it is sent to the Exa endpoint.
    #       (see GUIDE.md 1.4 for where it goes) => the key then appears in exception text: redact it before returning "ERROR: ..."
    #   WATCH OUT: read GUIDE.md 1.4 about how Exa signals "rate limited" on the free tier, and retry on it
    try:
        if not query.strip():
            return "NO RESULTS"
        return _exa_call("web_search_exa", {"query": query,
                                            "objective": objective or f"Find reliable sources about {query}",
                                            "numResults": max(1, min(int(num_results), 10))})
    except Exception as exc:
        return _error(exc, os.getenv("EXA_API_KEY", "").strip())


@tool
def web_fetch(url: str) -> str:
    """Read the full content of one web page (e.g. an arXiv abstract page) as markdown. Long pages are truncated."""
    # PSEUDO-CODE: MCP tool "web_fetch_exa" with arguments {"urls": [url]}; truncate the text to ~12000 chars
    try:
        if not url.startswith(("http://", "https://")):
            return "ERROR: invalid URL"
        return _exa_call("web_fetch_exa", {"urls": [url]})[:12000]
    except Exception as exc:
        return _error(exc, os.getenv("EXA_API_KEY", "").strip())


# ---- TODO 5: registry (the researcher subagent gets exactly these) ----
SOURCE_TOOLS = [arxiv_search, hf_daily_papers, hf_search_papers, web_search, web_fetch]


if __name__ == "__main__":
    for name, fn, args in [
        ("arxiv_search", arxiv_search, {"query": "world model", "max_results": 3}),
        ("hf_daily_papers", hf_daily_papers, {"limit": 20}),
        ("hf_search_papers", hf_search_papers, {"query": "world model", "limit": 3}),
        ("web_search", web_search, {"query": "survey paper on world models", "num_results": 2}),
        ("web_fetch", web_fetch, {"url": "https://arxiv.org/abs/1803.10122"}),
    ]:
        try:
            print(f"== {name}\n{fn.invoke(args)[:400]}\n")
        except NotImplementedError as exc:
            print(f"== {name}: not implemented yet ({exc})\n")
