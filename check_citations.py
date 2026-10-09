"""check_citations.py - STUDENT IMPLEMENTS `check`.   Runs INSIDE the sandbox (standard library only).

research.py uploads this file to the sandbox and the lead agent runs it with the `execute` tool:
    python3 /tmp/work/research/check_citations.py [report.md] [sources.json]
It must exit 0 and print "OK: ..." when the report is consistent, else print each problem and exit 1.
"""
import json
import re
import sys

REPORT = "/tmp/work/report/report.md"
SOURCES = "/tmp/work/research/sources.json"


# TODO (completed): validate report citations and References.
def check(report_text, sources):
    """Return a list of problem strings (empty list = OK).

    PSEUDO-CODE:
      problems = []
      if sources is empty: return ["no sources in sources.json"]
      for each source entry:
          n must be an int                       -> problem if not
          url must start with http:// or https://-> problem if not
          the same url must not appear twice     -> problem if duplicated
      split report_text at the heading "## References":
          body = text before it; if the heading is missing -> problem
      cited = set of numbers found as [n] in the BODY only (not in the reference list; use a regex)
      every number in `cited` must exist in sources -> problem "[n] cited but missing from sources.json"
      every source number must be in `cited`        -> problem "source [n] never cited"
      the lines of the References section that start with "[n]" (regex) are the reference lines:
          every source needs exactly ONE reference line (none missing, no number twice, no number that is not a source)
          each reference line holds exactly ONE http(s) URL and it must equal that source's url
          (a line bundling several sources under one number is a problem)
      return problems
    """
    problems = []
    if not isinstance(sources, list) or not sources:
        return ["no sources in sources.json"]

    by_number, seen_urls = {}, set()
    for entry in sources:
        if not isinstance(entry, dict):
            problems.append("source entry must be an object")
            continue
        n, url = entry.get("n"), entry.get("url")
        if type(n) is not int:
            problems.append(f"source n={n!r} is not an integer")
        elif n in by_number:
            problems.append(f"duplicate source [{n}]")
        else:
            by_number[n] = entry
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            problems.append(f"source [{n}] has invalid URL")
        elif url in seen_urls:
            problems.append(f"duplicate URL: {url}")
        else:
            seen_urls.add(url)
        family, source_id = entry.get("source"), entry.get("id")
        if family == "arxiv" and url != f"https://arxiv.org/abs/{source_id}":
            problems.append(f"source [{n}] arxiv id and URL disagree")
        if family in {"hf-daily", "hf-search"} and url != f"https://huggingface.co/papers/{source_id}":
            problems.append(f"source [{n}] Hugging Face id and URL disagree")

    heading = re.search(r"(?m)^##[ \t]+References[ \t]*$", report_text)
    if heading is None:
        problems.append("missing ## References")
        body, references = report_text, ""
    else:
        body, references = report_text[:heading.start()], report_text[heading.end():]

    # Code and Markdown links are not prose citations.
    body = re.sub(r"```.*?```|`[^`\n]*`", "", body, flags=re.S)
    body = re.sub(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]\([^)]*\)", "", body)
    cited = set()
    for match in re.finditer(r"\[(\d+(?:\s*[,–-]\s*\d+)*)\]", body):
        for part in re.split(r"\s*,\s*", match.group(1)):
            span = re.fullmatch(r"(\d+)\s*[–-]\s*(\d+)", part)
            if span:
                first, last = map(int, span.groups())
                if last < first or last - first > 200:
                    problems.append(f"invalid citation range [{part}]")
                    continue
                cited.update(range(first, last + 1))
            else:
                cited.add(int(part))
    for n in sorted(cited - by_number.keys()):
        problems.append(f"[{n}] cited but missing from sources.json")
    for n in sorted(by_number.keys() - cited):
        problems.append(f"source [{n}] never cited")

    reference_lines = {}
    for line in references.splitlines():
        if not line.strip():
            continue
        match = re.match(r"^\s*\[(\d+)\]\s+(.+)$", line)
        if not match:
            problems.append("References contains a line without a [n] source number")
            continue
        n = int(match.group(1))
        reference_lines.setdefault(n, []).append(match.group(2))
    for n in sorted(reference_lines.keys() - by_number.keys()):
        problems.append(f"reference [{n}] missing from sources.json")
    for n, source in sorted(by_number.items()):
        lines = reference_lines.get(n, [])
        if len(lines) != 1:
            problems.append(f"source [{n}] has {len(lines)} reference lines (need exactly one)")
            continue
        urls = re.findall(r"https?://[^\s<>]+", lines[0])
        urls = [url.rstrip(".,;") for url in urls]
        if len(urls) != 1 or urls[0] != source.get("url"):
            problems.append(f"reference [{n}] must contain exactly its source URL")
    return problems


def main(argv):
    report_path = argv[1] if len(argv) > 1 else REPORT
    sources_path = argv[2] if len(argv) > 2 else SOURCES
    try:
        with open(report_path, encoding="utf-8") as f:
            report = f.read()
        with open(sources_path, encoding="utf-8") as f:
            sources = json.load(f)
    except (OSError, ValueError) as exc:
        print(f"cannot read inputs: {exc}")
        return 1
    problems = check(report, sources)
    if problems:
        print("\n".join(problems))
        return 1
    print(f"OK: {len(sources)} sources, all citations resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
