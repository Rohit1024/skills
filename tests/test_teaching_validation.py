#!/usr/bin/env python3
"""Check validator caching and failure handling without launching real browsers.

The isolated renderer implements the batch protocol and records invocations.
For a real rendering smoke test, copy the skill into a teaching project and run its validator with --force.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills" / "productivity" / "setup-teaching-site" / "scripts"
NODE = shutil.which("node")
FAKE_RENDERER = """
import { appendFileSync } from 'node:fs';
let input = '';
for await (const chunk of process.stdin) input += chunk;
const { diagrams } = JSON.parse(input);
appendFileSync('render-calls.jsonl', JSON.stringify(diagrams.map(item => item.id)) + '\\n');
process.stdout.write(JSON.stringify(diagrams.map(({ id, source }) => ({
  id, error: source.includes('INVALID') ? 'Parse error from test renderer' : null,
}))));
"""


@unittest.skipUnless(NODE, "Node is required to exercise the renderer protocol")
class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="teaching-validator-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.scripts = self.root / ".agents" / "skills" / "teach" / "scripts"
        self.scripts.mkdir(parents=True)
        shutil.copy2(SOURCE / "validate_mermaid.py", self.scripts)
        (self.scripts / "validate_mermaid.mjs").write_text(FAKE_RENDERER)
        for name in ["@mermaid-js/mermaid-cli", "mermaid", "puppeteer"]:
            package = self.root / "node_modules" / name / "package.json"
            package.parent.mkdir(parents=True, exist_ok=True)
            package.write_text(json.dumps({"name": name, "version": "1.0.0"}))
        self.docs = self.root / "docs"
        self.docs.mkdir()
        self.page = self.docs / "lesson.md"
        self.page.write_text("# Lesson\n\n```mermaid\nflowchart TD\n    A --> B\n```\n")

    def run_validator(self, *arguments, node_available=True):
        env = os.environ.copy()
        if not node_available:
            env["PATH"] = str(self.root / "no-node-here")
        return subprocess.run([sys.executable, str(self.scripts / "validate_mermaid.py"), *arguments],
                              cwd=self.root, env=env, capture_output=True, text=True, timeout=20)

    def calls(self):
        path = self.root / "render-calls.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repeat_and_prose_edits_do_not_start_node(self):
        self.assert_success(self.run_validator())
        self.assert_success(self.run_validator(node_available=False))
        self.page.write_text(self.page.read_text() + "\nA prose-only edit.\n")
        self.assert_success(self.run_validator(node_available=False))
        self.assertEqual(len(self.calls()), 1)

    def test_duplicates_render_once_and_only_changed_content_renders_again(self):
        other = self.docs / "second.md"
        other.write_text(self.page.read_text())
        self.assert_success(self.run_validator())
        self.assertEqual([len(batch) for batch in self.calls()], [1])
        other.write_text("```mermaid\nflowchart TD\n    C --> D\n```\n")
        self.assert_success(self.run_validator())
        self.assertEqual([len(batch) for batch in self.calls()], [1, 1])
        self.assert_success(self.run_validator("--force"))
        self.assertEqual([len(batch) for batch in self.calls()], [1, 1, 2])

    def test_invalid_diagrams_are_never_cached_as_successful(self):
        bad = self.docs / "bad.md"
        bad.write_text("```mermaid\nINVALID\n```\n")
        for _ in range(2):
            result = self.run_validator()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("bad.md, diagram #1", result.stderr)
            self.assertIn("Parse error", result.stderr)
        self.assertEqual([len(batch) for batch in self.calls()], [2, 1])
        bad.unlink()
        self.assert_success(self.run_validator(node_available=False))

    def test_dependency_and_validator_changes_invalidate_passes(self):
        self.assert_success(self.run_validator())
        package = self.root / "node_modules" / "mermaid" / "package.json"
        package.write_text('{"name":"mermaid","version":"2.0.0"}')
        self.assert_success(self.run_validator())
        helper = self.scripts / "validate_mermaid.mjs"
        helper.write_text(helper.read_text() + "\n// renderer update\n")
        self.assert_success(self.run_validator())
        wrapper = self.scripts / "validate_mermaid.py"
        wrapper.write_text(wrapper.read_text() + "\n# wrapper update\n")
        self.assert_success(self.run_validator())
        self.assertEqual(len(self.calls()), 4)

    def test_lockfile_and_corrupt_cache_trigger_fresh_checks(self):
        self.assert_success(self.run_validator())
        (self.root / "package-lock.json").write_text('{"lockfileVersion":3}')
        self.assert_success(self.run_validator())
        cache = self.root / ".tools" / "validation" / "mermaid.json"
        cache.write_text("{broken JSON")
        self.assert_success(self.run_validator())
        (self.root / "pnpm-lock.yaml").write_text("lockfileVersion: '9.0'\n")
        self.assert_success(self.run_validator())
        self.assertEqual(len(self.calls()), 4)

    def test_nested_examples_are_ignored_but_tilde_fences_are_checked(self):
        self.page.write_text('''````markdown
```mermaid
INVALID example text
```
````

    ~~~~mermaid
    flowchart TD
        A --> B
    ~~~~
''')
        self.assert_success(self.run_validator())
        self.assertEqual([len(batch) for batch in self.calls()], [1])

    def test_missing_paths_and_unclosed_fences_fail(self):
        self.assertNotEqual(self.run_validator("missing.md").returncode, 0)
        self.page.write_text("```mermaid\nflowchart TD\n A --> B\n")
        result = self.run_validator()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unclosed Mermaid", result.stderr)
        self.assertEqual(self.calls(), [])

    def test_scoped_checks_do_not_validate_unrelated_pages(self):
        (self.docs / "unrelated.md").write_text("```mermaid\nINVALID\n```\n")
        self.assert_success(self.run_validator(str(self.page)))
        self.assertNotEqual(self.run_validator().returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
