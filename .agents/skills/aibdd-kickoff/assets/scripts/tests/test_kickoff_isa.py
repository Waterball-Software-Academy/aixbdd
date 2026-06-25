"""Regression tests for kickoff isa seed."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "kickoff_layout.py"

# Backend stacks both map to the web-service boundary preset (isa-template.yml).
# nextjs_playwright -> web-frontend has no isa template yet (out of scope).
SUPPORTED_STACKS = ("python_e2e", "java_e2e")


class KickoffIsaTest(unittest.TestCase):
    def _run_layout(self, stack: str, project_root: Path) -> dict:
        decisions = {
            "project_root": str(project_root),
            "boundary_codebase_subdir": "",
            "stack": stack,
        }
        decisions_file = project_root / "decisions.json"
        decisions_file.write_text(json.dumps(decisions))
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--decisions-file", str(decisions_file)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_each_supported_stack_seeds_isa(self) -> None:
        for stack in SUPPORTED_STACKS:
            with self.subTest(stack=stack):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    result = self._run_layout(stack, root)
                    self.assertTrue(result["ok"])
                    isa = Path(result["isa_path"])
                    self.assertTrue(isa.is_file())
                    self.assertEqual(isa.name, "isa.yml")
                    content = isa.read_text()
                    self.assertIn("instructions:", content)
                    self.assertIn("instruction_type: api_call", content)


if __name__ == "__main__":
    unittest.main()
