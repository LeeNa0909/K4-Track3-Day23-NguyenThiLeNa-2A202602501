"""research.py - STUDENT IMPLEMENTS.  The main script.   Guide: GUIDE.md, part 3.

Usage:  python research.py "survey about world model"
Result: reports/<slug>.md   reports/<slug>.sources.json   reports/<slug>.meta.json
"""
import json  # noqa: F401
import os  # noqa: F401
import re  # noqa: F401
import sys
import time  # noqa: F401
import threading
from collections import Counter  # noqa: F401
from pathlib import Path

from langchain_core.callbacks import BaseCallbackHandler
from agents import FINALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR, build_lead_agent  # noqa: F401
from check_citations import check
from model import make_model  # noqa: F401
from sandbox import download, open_sandbox, upload  # noqa: F401

ROOT = Path(__file__).parent
REPORTS = ROOT / "reports"
VALIDATOR_SOURCE = ROOT / "check_citations.py"
FINALIZER_SOURCE = ROOT / "finalize_citations.py"   # provided: uploaded next to your validator


class ProgressCallback(BaseCallbackHandler):
    """Print only tool names and periodic model counts; never print arguments or API keys."""

    def __init__(self):
        self.model_calls = 0
        self.lock = threading.Lock()

    def on_chat_model_start(self, serialized, messages, **kwargs):
        with self.lock:
            self.model_calls += 1
            if self.model_calls % 10 == 0:
                print(f"[progress] {self.model_calls} model calls", flush=True)

    def on_tool_start(self, serialized, input_str, **kwargs):
        name = serialized.get("name", "tool") if isinstance(serialized, dict) else "tool"
        if name in {"task", "execute", "write_file", "arxiv_search", "hf_search_papers",
                    "hf_daily_papers", "web_search", "web_fetch"}:
            print(f"[tool] {name}", flush=True)


# TODO 1 (completed): safe report slug.
def slugify(topic):
    """Turn a topic into a safe file name: lower case, runs of non-word characters become one "-", max 60 chars,
    never empty (fall back to "topic"). The topic is user input: "../../x" must not escape reports/."""
    slug = re.sub(r"[^\w]+", "-", str(topic).lower(), flags=re.UNICODE).strip("-_")[:60].rstrip("-_")
    return slug or "topic"


# TODO 2 (completed): lead task instructions.
def build_prompt(topic):
    """The user message sent to the lead agent."""
    return (f"Research topic: {topic.strip()}\n"
            "Produce a complete English survey following REPORT_TEMPLATE.md: TL;DR, Background, "
            "3-6 thematic sections, Trends and open problems, and generated References. "
            "Delegate at least three independent subquestions to researchers, use at least three "
            "source families, and verify all claims and citations. The report and sources must "
            "be written inside the sandbox before you finish.")


# TODO 3 (completed): lead run metadata.
def summarize(messages, elapsed, model_name):
    """Return {"model", "elapsed_s", "subagent_calls", "tool_calls": {name: count}, "tokens": {"input", "output"}}.

    PSEUDO-CODE: walk the lead's messages; for every message with tool_calls count call["name"] (subagent_calls = the
    count of "task"); add the input/output token counts from each message's usage_metadata when present.
    (Lead messages only: subagent tokens are not included, so this undercounts the real cost.)
    elapsed_s rounded to 0.1.
    """
    calls = Counter()
    tokens = {"input": 0, "output": 0}
    for message in messages:
        for call in getattr(message, "tool_calls", None) or []:
            if isinstance(call, dict) and call.get("name"):
                calls[call["name"]] += 1
        usage = getattr(message, "usage_metadata", None) or {}
        tokens["input"] += int(usage.get("input_tokens") or 0)
        tokens["output"] += int(usage.get("output_tokens") or 0)
    return {"model": model_name, "elapsed_s": round(elapsed, 1), "subagent_calls": calls["task"],
            "tool_calls": dict(calls), "tokens": tokens}


def template_problems(report):
    """Check the report sections that the citation validator intentionally does not cover."""
    problems = []
    if not re.search(r"(?m)^# [^#\n]+$", report):
        problems.append("report needs a level-one title")
    headings = re.findall(r"(?m)^## ([^\n]+)$", report)
    if len(headings) < 4 or headings[:2] != ["TL;DR", "Background"] or headings[-2:] != [
        "Trends and open problems", "References"
    ]:
        problems.append("report headings do not follow REPORT_TEMPLATE order")
        return problems
    if not 3 <= len(headings) - 4 <= 6:
        problems.append("report needs 3 to 6 thematic sections")
    sections = dict(re.findall(r"(?ms)^## ([^\n]+)\n(.*?)(?=^## |\Z)", report))
    bullets = re.findall(r"(?m)^\s*[-*]\s+(.+)$", sections.get("TL;DR", ""))
    if not 3 <= len(bullets) <= 5:
        problems.append("TL;DR needs 3 to 5 bullets")
    if any(not re.search(r"\[\d+\]", bullet) for bullet in bullets):
        problems.append("every TL;DR bullet needs a citation")
    for heading in ("Background", "Trends and open problems"):
        if not re.search(r"\[\d+\]", sections.get(heading, "")):
            problems.append(f"{heading} needs at least one supporting citation")
    return problems


# TODO 4 (completed): validate and download sandbox artifacts.
def save_outputs(backend, topic, messages, elapsed, model_name, reports_dir=REPORTS):
    """Download the report from the sandbox and write the three files into reports_dir. Return the report path.

    PSEUDO-CODE:
      files = download(backend, [REPORT_PATH, SOURCES_PATH])
      if the report is missing/empty or sources.json is missing/invalid JSON: raise RuntimeError and WRITE NOTHING
          (a failed run must never leave an empty or half-written report behind)
      write <slug>.sources.json, <slug>.meta.json (topic + summarize(...) + n_sources + source_families: the sorted
      distinct "source" values of sources.json) and <slug>.md
    """
    files = download(backend, [REPORT_PATH, SOURCES_PATH])
    report_bytes, sources_bytes = files.get(REPORT_PATH), files.get(SOURCES_PATH)
    if not report_bytes or not sources_bytes:
        raise RuntimeError("sandbox did not produce a non-empty report and sources.json")
    try:
        report = report_bytes.decode("utf-8")
        sources = json.loads(sources_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise RuntimeError(f"invalid report or sources.json: {exc}") from exc
    if not report.strip() or not isinstance(sources, list) or not sources:
        raise RuntimeError("report is empty or sources.json has no sources")
    problems = check(report, sources)
    if problems:
        raise RuntimeError("citation validation failed: " + "; ".join(problems[:5]))
    for entry in sources:
        family, url, source_id = entry.get("source"), entry.get("url"), entry.get("id")
        if family == "arxiv" and url != f"https://arxiv.org/abs/{source_id}":
            raise RuntimeError(f"arxiv source [{entry['n']}] has a mismatched URL")
        if family in {"hf-daily", "hf-search"} and url != f"https://huggingface.co/papers/{source_id}":
            raise RuntimeError(f"Hugging Face source [{entry['n']}] has a mismatched URL")
    structure_errors = template_problems(report)
    if structure_errors:
        raise RuntimeError("report template validation failed: " + "; ".join(structure_errors))
    summary = summarize(messages, elapsed, model_name)
    families = sorted({entry.get("source") for entry in sources if isinstance(entry, dict) and
                       entry.get("source") in {"arxiv", "hf-daily", "hf-search", "web"}})
    if summary["subagent_calls"] < 3:
        raise RuntimeError("lead used fewer than three researcher task calls")
    if len(families) < 3:
        raise RuntimeError("report cites fewer than three source families")
    meta = {"topic": topic, **summary, "n_sources": len(sources), "source_families": families}
    reports_dir.mkdir(parents=True, exist_ok=True)
    stem = slugify(topic)
    path = reports_dir / f"{stem}.md"
    (reports_dir / f"{stem}.sources.json").write_bytes(sources_bytes)
    (reports_dir / f"{stem}.meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                                                  encoding="utf-8")
    path.write_bytes(report_bytes)
    return path


# TODO 5 (completed): full sandbox lifecycle.
def main(topic):
    """Return the process exit code (0 ok, 1 failed run, 2 no topic).

    PSEUDO-CODE:
      empty topic -> print usage to stderr, return 2
      model = make_model(); start = time.monotonic()
      with open_sandbox() as backend:                # the sandbox is always cleaned up, even on errors
          backend.execute("mkdir -p <WORKDIR>/research/notes <WORKDIR>/report")
          upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(), FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
          agent = build_lead_agent(backend, model)
          result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                config={"recursion_limit": 1000})
          save_outputs(...); on RuntimeError print "FAILED: ..." to stderr and return 1
      print where the report was saved; return 0
    """
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if not topic.strip():
        print('Usage: python research.py "<topic>"', file=sys.stderr)
        return 2
    start = time.monotonic()
    try:
        model = make_model()
        with open_sandbox() as backend:
            prepared = backend.execute(f"mkdir -p {WORKDIR}/research/notes {WORKDIR}/report")
            if prepared.exit_code != 0:
                raise RuntimeError(f"cannot prepare sandbox: {prepared.output}")
            upload(backend, {VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
                             FINALIZER_PATH: FINALIZER_SOURCE.read_bytes()})
            seeded = backend.execute(f"test -s {VALIDATOR_PATH} && test -s {FINALIZER_PATH}")
            if seeded.exit_code != 0:
                raise RuntimeError("could not upload citation scripts into sandbox")
            agent = build_lead_agent(backend, model)
            progress = ProgressCallback()
            result = agent.invoke({"messages": [{"role": "user", "content": build_prompt(topic)}]},
                                  config={"recursion_limit": 1000, "callbacks": [progress]})
            model_name = os.getenv("LAB_MODEL", getattr(model, "model_name", "unknown"))
            for repair in range(3):
                try:
                    path = save_outputs(backend, topic, result.get("messages", []),
                                        time.monotonic() - start, model_name)
                    break
                except RuntimeError as exc:
                    if repair == 2:
                        raise
                    print(f"Repair {repair + 1}/2: {exc}", file=sys.stderr)
                    correction = ("The sandbox artifacts failed host validation: " + str(exc) + ". "
                                  "Inspect and fix the report and sources INSIDE the sandbox. Keep all claims "
                                  "grounded in retrieved notes. Use the exact REPORT_TEMPLATE headings, at least "
                                  "three thematic sections, three source families, and at least three researcher "
                                  "task calls. Run the citation finalizer after editing the body, then run the "
                                  "citation validator until OK. Do not merely describe a fix; write the files.")
                    result = agent.invoke({"messages": [*result.get("messages", []),
                                                        {"role": "user", "content": correction}]},
                                          config={"recursion_limit": 1000, "callbacks": [progress]})
        print(f"Saved report: {path}")
        return 0
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(" ".join(sys.argv[1:])))
