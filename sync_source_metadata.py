"""Apply verified source metadata inside the sandbox and download validated artifacts.

Usage: python sync_source_metadata.py <report-slug>
"""

import json
import sys
from pathlib import Path

from agents import FINALIZER_PATH, REPORT_PATH, SOURCES_PATH, VALIDATOR_PATH, WORKDIR
from check_citations import check
from research import FINALIZER_SOURCE, REPORTS, VALIDATOR_SOURCE
from sandbox import download, open_sandbox, upload

ROOT = Path(__file__).parent
METADATA = ROOT / "verified_source_metadata.json"
SYNC_PATH = f"{WORKDIR}/research/sync_metadata.py"
VERIFIED_PATH = f"{WORKDIR}/research/verified_metadata.json"
SYNC_CODE = b"""import json
from pathlib import Path
sources_path = Path('/tmp/work/research/sources.json')
fixes = json.loads(Path('/tmp/work/research/verified_metadata.json').read_text(encoding='utf-8'))
sources = json.loads(sources_path.read_text(encoding='utf-8'))
for item in sources:
    if item.get('url') in fixes:
        item.update(fixes[item['url']])
sources_path.write_text(json.dumps(sources, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
"""


def main(slug):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if not slug or Path(slug).name != slug or "." in slug:
        raise ValueError("provide a report slug without extension")
    report_path = REPORTS / f"{slug}.md"
    sources_path = REPORTS / f"{slug}.sources.json"
    previous_report = report_path.read_bytes()
    previous_sources = sources_path.read_bytes()
    with open_sandbox() as backend:
        prepared = backend.execute(f"mkdir -p {WORKDIR}/research {WORKDIR}/report")
        if prepared.exit_code:
            raise RuntimeError(prepared.output)
        upload(backend, {REPORT_PATH: previous_report, SOURCES_PATH: previous_sources,
                         VALIDATOR_PATH: VALIDATOR_SOURCE.read_bytes(),
                         FINALIZER_PATH: FINALIZER_SOURCE.read_bytes(),
                         SYNC_PATH: SYNC_CODE, VERIFIED_PATH: METADATA.read_bytes()})
        for command in (f"python3 {SYNC_PATH}", f"python3 {FINALIZER_PATH}",
                        f"python3 {VALIDATOR_PATH}"):
            outcome = backend.execute(command)
            if outcome.exit_code:
                raise RuntimeError(f"{command}: {outcome.output}")
        files = download(backend, [REPORT_PATH, SOURCES_PATH])
        report_bytes, sources_bytes = files[REPORT_PATH], files[SOURCES_PATH]
        if not report_bytes or not sources_bytes:
            raise RuntimeError("sandbox output is missing")
        if check(report_bytes.decode("utf-8"), json.loads(sources_bytes.decode("utf-8"))):
            raise RuntimeError("downloaded citations failed validation")
        report_path.write_bytes(report_bytes)
        sources_path.write_bytes(sources_bytes)
    print(f"Verified source metadata: {report_path}")


if __name__ == "__main__":
    try:
        main(sys.argv[1])
    except Exception as exc:
        print(f"FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
