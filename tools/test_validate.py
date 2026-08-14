#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).with_name("validate.py")
spec = importlib.util.spec_from_file_location("trek_validate", MODULE_PATH)
validate = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(validate)


class ValidationTests(unittest.TestCase):
    def test_schema_invalid_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            research = root / "research"
            research.mkdir()
            (research / "records.jsonl").write_text(
                json.dumps({
                    "record_type": "source",
                    "source_id": "source-1",
                    "source_kind": "transcript"
                }) + "\n",
                encoding="utf-8",
            )
            old_roots = validate.DATA_ROOTS
            validate.DATA_ROOTS = [research]
            try:
                stdout = io.StringIO()
                with contextlib.redirect_stdout(stdout):
                    rc = validate.main()
            finally:
                validate.DATA_ROOTS = old_roots
            self.assertEqual(rc, 1)
            self.assertIn("locator", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
