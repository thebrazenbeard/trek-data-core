"""Standalone migration verification must not trust edited receipt identities."""

import copy
import json
import runpy
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "proposals/migration/tng-s01-b002-historical-20261103"
VALIDATE = runpy.run_path(str(DIR / "validate.py"))["validate"]


class HistoricalTngEnvelope(unittest.TestCase):
    def test_original_standalone_packet(self):
        VALIDATE(None)

    def test_historical_receipt_and_admission_envelope_tampering_rejected(self):
        original = json.loads((DIR / "records.json").read_text(encoding="utf-8"))
        cases = (
            lambda d: d["historical_artifacts"][0].update(git_blob_sha1="0" * 40),
            lambda d: d["historical_artifacts"][0].update(sha256="0" * 64),
            lambda d: d["historical_source"].update(reported_reading="PRIMARY_AV_VERIFIED"),
            lambda d: d.update(accepted_world_state=[{"assertion": "forged"}]),
            lambda d: d["episode_candidates"][0].update(accepted_world_state=True),
        )
        for mutate in cases:
            data = copy.deepcopy(original)
            mutate(data)
            with self.subTest(mutation=str(mutate)):
                with tempfile.TemporaryDirectory() as tmp:
                    candidate = Path(tmp)
                    (candidate / "records.json").write_text(json.dumps(data), encoding="utf-8")
                    VALIDATE.__globals__["HERE"] = candidate
                    try:
                        with self.assertRaises(ValueError):
                            VALIDATE(None)
                    finally:
                        VALIDATE.__globals__["HERE"] = DIR


if __name__ == "__main__":
    unittest.main()
