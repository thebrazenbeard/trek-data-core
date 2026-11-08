"""Hostile Windows reserved-device-name regression for held crosswalk auditor."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / "tools" / "audit_held_windows_crosswalk.py"
spec = importlib.util.spec_from_file_location("held_crosswalk_audit", MODULE)
auditor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auditor)


class WindowsDeviceNameTests(unittest.TestCase):
    def test_reserved_names_fail_closed(self):
        for name in (
            "CON", "PRN.txt", "AUX", "NUL", "COM1", "COM9.txt",
            "LPT1", "COM¹", "COM²", "COM³", "LPT¹", "LPT²", "LPT³",
            "CONIN$", "CONOUT$", "conin$.txt", "CONOUT$.log",
        ):
            with self.subTest(name=name), self.assertRaises(ValueError):
                auditor.validate_windows_path("held/" + name)

    def test_surrogateescape_git_names_fail_closed(self):
        # Git permits arbitrary filename bytes; surrogateescape cannot be a Windows path.
        for path in ("held/invalid\\udcff.txt", "held/\\udc80", "held/sub\\udcffile"):
            with self.subTest(path=repr(path)), self.assertRaises(ValueError):
                auditor.validate_windows_path(path)

    def test_non_device_controls(self):
        for name in ("CONIN", "CONOUT", "CONIN$extra", "COM10", "README.txt"):
            with self.subTest(name=name):
                auditor.validate_windows_path("held/" + name)


if __name__ == "__main__":
    unittest.main()
