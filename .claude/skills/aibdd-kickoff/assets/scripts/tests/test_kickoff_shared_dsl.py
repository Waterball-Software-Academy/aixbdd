"""Regression tests for kickoff shared DSL seed."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "kickoff_layout.py"

STACK_EXPECTED_VARIANT = {
    "python_e2e": "python-e2e",
    "java_e2e": "java-e2e",
    "nextjs_playwright": "nextjs-playwright",
}


class KickoffSharedDslTest(unittest.TestCase):
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

    def test_each_supported_stack_seeds_shared_dsl(self) -> None:
        for stack, expected_variant in STACK_EXPECTED_VARIANT.items():
            with self.subTest(stack=stack):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    result = self._run_layout(stack, root)
                    self.assertTrue(result["ok"])
                    shared_dsl = Path(result["shared_dsl_path"])
                    self.assertTrue(shared_dsl.is_file())
                    content = shared_dsl.read_text()
                    self.assertIn("entries:", content)
                    self.assertIn(f'variant: "{expected_variant}"', content)
                    self.assertNotIn("<backend-variant-id>", content)
                    self.assertNotIn("<frontend-variant-id>", content)


if __name__ == "__main__":
    unittest.main()
