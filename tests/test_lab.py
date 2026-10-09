"""Offline checks for the highest-risk rubric requirements (no keys or network)."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import research
import tools
from agents import REPORT_PATH, SOURCES_PATH
from check_citations import check
from finalize_citations import finalize


SOURCES = [
    {"n": 1, "id": "2501.00001", "url": "https://arxiv.org/abs/2501.00001",
     "title": "A", "date": "2025-01-01", "source": "arxiv"},
    {"n": 2, "id": "2501.00002", "url": "https://huggingface.co/papers/2501.00002",
     "title": "B", "date": "2025-01-02", "source": "hf-search"},
    {"n": 3, "id": "https://example.org/c", "url": "https://example.org/c",
     "title": "C", "date": "2025-01-03", "source": "web"},
]
BODY = ("# Survey\n\n## TL;DR\n- A [1].\n- B [2].\n- C [3].\n\n"
        "## Background\nContext [1].\n\n## Theme one\nEvidence [1][2].\n\n"
        "## Theme two\nEvidence [2][3].\n\n## Theme three\nEvidence [1][3].\n\n"
        "## Trends and open problems\nOpen issue [3].\n")


class LabChecks(unittest.TestCase):
    def test_retry_stops_after_last_attempt_and_honors_retry_after(self):
        calls = []

        def fail():
            calls.append(1)
            raise tools.RetryableError("busy", retry_after=2)

        with patch.object(tools.time, "sleep") as sleep:
            with self.assertRaises(tools.RetryableError):
                tools.with_retry(fail, attempts=3)
        self.assertEqual(len(calls), 3)
        self.assertEqual(sleep.call_count, 2)
        self.assertEqual([call.args[0] for call in sleep.call_args_list], [2, 2])

    def test_finalizer_and_validator_agree_on_grouped_citations(self):
        report, sources, problems = finalize(BODY.replace("[1][2]", "[1, 2]"), SOURCES)
        self.assertEqual(problems, [])
        self.assertEqual(check(report, sources), [])
        self.assertIn("[1][2]", report)
        broken = report.replace("https://example.org/c (2025", "https://example.org/c https://other.org (2025")
        self.assertTrue(any("exactly its source URL" in p for p in check(broken, sources)))

    def test_hugging_face_flat_and_nested_responses(self):
        flat = {"id": "2501.00002", "title": "B", "ai_summary": "Short", "upvotes": 5}
        nested = {"paper": {"id": "2501.00002", "title": "B", "summary": "Long", "upvotes": 5}}
        self.assertEqual(tools._paper_record(flat, prefer_ai=True)["summary"], "Short")
        self.assertEqual(tools._paper_record(nested)["summary"], "Long")

    def test_failed_download_writes_nothing_and_valid_download_is_exact(self):
        messages = [SimpleNamespace(tool_calls=[{"name": "task"}] * 3, usage_metadata={})]
        report, sources, problems = finalize(BODY, SOURCES)
        self.assertEqual(problems, [])
        source_bytes = json.dumps(sources).encode()
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            with patch.object(research, "download", return_value={REPORT_PATH: b"", SOURCES_PATH: source_bytes}):
                with self.assertRaises(RuntimeError):
                    research.save_outputs(object(), "topic", messages, 1, "model", output)
            self.assertEqual(list(output.iterdir()), [])
            with patch.object(research, "download", return_value={REPORT_PATH: report.encode(),
                                                                   SOURCES_PATH: source_bytes}):
                path = research.save_outputs(object(), "topic", messages, 1, "model", output)
            self.assertEqual(path.read_bytes(), report.encode())
            self.assertEqual((output / "topic.sources.json").read_bytes(), source_bytes)


if __name__ == "__main__":
    unittest.main()
