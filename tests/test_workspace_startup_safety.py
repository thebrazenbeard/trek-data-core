"""Fail closed on tracked VS Code workspace startup execution.

Source-tree checks only: never execute editor tasks or suspect assets.
"""

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FONT_SIGNATURES = (
    b"\x00\x01\x00\x00",  # TrueType sfnt
    b"OTTO",                # OpenType CFF
    b"true",                # Apple TrueType
    b"typ1",                # Type 1 sfnt
    b"wOFF",                # WOFF
    b"wOF2",                # WOFF2
)


def read_jsonc(path: Path) -> dict:
    # utf-8-sig permits a BOM while still parsing the task body and enforcing
    # the safety predicates. A BOM must never bypass folder-open inspection.
    text = path.read_text(encoding="utf-8-sig")
    return json.loads(re.sub(r",\s*(?=[}\]])", "", text))


class WorkspaceStartupSafetyTests(unittest.TestCase):
    def test_no_folder_open_tasks(self):
        tasks = read_jsonc(ROOT / ".vscode" / "tasks.json")
        self.assertIsInstance(tasks.get("tasks", []), list)
        for task in tasks.get("tasks", []):
            self.assertNotEqual(task.get("runOptions", {}).get("runOn"), "folderOpen")
            command = str(task.get("command", ""))
            self.assertNotIn("public/fonts/fa-solid.lkf", command)
            self.assertNotIn("public/fonts/fa-solid-600.ttf", command)

    def test_workspace_does_not_enable_automatic_tasks(self):
        settings = read_jsonc(ROOT / ".vscode" / "settings.json")
        self.assertEqual(settings.get("task.allowAutomaticTasks"), "off")
        self.assertNotIn("tasks", settings, "no embedded startup tasks in settings")

    def test_no_pseudo_font_executable(self):
        font_dir = ROOT / "public" / "fonts"
        self.assertFalse(
            list(font_dir.glob("*.lkf")),
            "unrecognized pseudo-font extension in tracked public assets",
        )
        # Check bytes, not extension. A .ttf name does not make a Node.js
        # payload into a font. No suspect content is ever executed.
        suspect = font_dir / "fa-solid-600.ttf"
        if suspect.is_file():
            with suspect.open("rb") as stream:
                magic = stream.read(4)
            self.assertIn(magic, FONT_SIGNATURES, "font asset lacks a font signature")


if __name__ == "__main__":
    unittest.main()
