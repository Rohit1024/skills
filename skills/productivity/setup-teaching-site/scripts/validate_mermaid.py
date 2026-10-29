#!/usr/bin/env python3
"""Render new or changed Mermaid blocks, reusing successful checks by content."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HELPER = Path(__file__).with_suffix(".mjs")


def mermaid_blocks(text):
    """Ignore examples inside other fences; support nested blocks and tilde fences."""
    fence = None
    lines = []
    for line in text.splitlines():
        match = re.match(r"^[ \t]*(`{3,}|~{3,})(.*)$", line)
        if fence is None:
            if match:
                marker, info = match.groups()
                fence = (marker[0], len(marker), info.split(maxsplit=1)[:1] == ["mermaid"])
                lines = []
        elif match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
            if fence[2]:
                yield "\n".join(lines).strip()
            fence = None
        else:
            lines.append(line)
    if fence and fence[2]:
        raise ValueError("Unclosed Mermaid code fence")


def package_file(name, start):
    # Follow Node's ancestor lookup, including pnpm's real dependency directories.
    for directory in (start, *start.parents):
        path = directory / "node_modules" / name / "package.json"
        if path.is_file():
            return path.resolve()
    raise FileNotFoundError(f"Local package {name} is not installed")


def fingerprint():
    # Versions and both scripts invalidate cached passes when the validator changes.
    paths = [Path(__file__), HELPER]
    cli = package_file("@mermaid-js/mermaid-cli", ROOT)
    paths.extend([cli, package_file("mermaid", cli.parent), package_file("puppeteer", ROOT)])
    paths.extend(ROOT / name for name in [
        "package-lock.json", "npm-shrinkwrap.json", "pnpm-lock.yaml", "yarn.lock", "bun.lock", "bun.lockb",
    ] if (ROOT / name).is_file())
    digest = hashlib.sha256()
    for path in paths:
        content = path.read_bytes()
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def load_cache(path, signature):
    try:
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved["fingerprint"] == signature and isinstance(saved["passed"], list):
            return {key for key in saved["passed"] if isinstance(key, str)}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return set()


def save_cache(path, signature, passed):
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", dir=path.parent, encoding="utf-8", delete=False) as output:
            temporary = Path(output.name)
            json.dump({"fingerprint": signature, "passed": sorted(passed)}, output)
        os.replace(temporary, path)
    except OSError as error:
        print(f"Cache could not be saved: {error}", file=sys.stderr)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path, help="Markdown files or directories; default: docs/")
    parser.add_argument("--workers", type=int, default=4, help="Concurrent pages in one browser (1–8)")
    parser.add_argument("--force", action="store_true", help="Re-render all selected diagrams, ignoring previous passes")
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".tools" / "validation", help="Cache outside Zensical's .cache directory")
    args = parser.parse_args()
    files = set()
    for path in args.paths or [ROOT / "docs"]:
        if not path.exists():
            print(f"Missing input path: {path}", file=sys.stderr)
            return 1
        files.update(path.rglob("*.md") if path.is_dir() else [path])
    items = []
    for path in sorted(files):
        try:
            for number, block in enumerate(mermaid_blocks(path.read_text(encoding="utf-8")), 1):
                items.append((path, number, block, hashlib.sha256(block.encode()).hexdigest()))
        except (OSError, ValueError) as error:
            print(f"ERROR: {path}: {error}", file=sys.stderr)
            return 1
    if not items:
        print(f"Scanned {len(files)} Markdown files; no Mermaid diagrams found.")
        return 0
    try:
        signature = fingerprint()
    except OSError as error:
        print(f"Validator or Mermaid dependencies missing: {error}. Run npm ci first.", file=sys.stderr)
        return 1
    cache_path = args.cache_dir / "mermaid.json"
    passed = load_cache(cache_path, signature)
    pending = {key: block for _, _, block, key in items if args.force or key not in passed}
    cached = sum(key not in pending for _, _, _, key in items)
    print(f"Scanned {len(files)} Markdown files; {len(items)} diagrams, {cached} cached; rendering {len(pending)} unique diagrams...", flush=True)
    errors = []
    if pending:
        workers = max(1, min(args.workers, 8))
        try:
            result = subprocess.run(["node", str(HELPER)], cwd=ROOT, input=json.dumps({
                "workers": workers,
                "diagrams": [{"id": key, "source": source} for key, source in pending.items()],
            }), capture_output=True, text=True, timeout=60 + 120 * ((len(pending) + workers - 1) // workers))
            if result.returncode:
                print(result.stderr.strip() or result.stdout.strip(), file=sys.stderr)
                return 1
            results = json.loads(result.stdout)
            if not isinstance(results, list) or len(results) != len(pending) or {item["id"] for item in results} != pending.keys():
                raise ValueError("The batch renderer returned incomplete results.")
            failures = {}
            for item in results:
                if item["error"] is None:
                    passed.add(item["id"])
                elif isinstance(item["error"], str) and item["error"]:
                    failures[item["id"]] = item["error"]
                    passed.discard(item["id"])
                else:
                    raise ValueError("The batch renderer returned an invalid result.")
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError) as error:
            print(f"Could not validate Mermaid diagrams: {error}", file=sys.stderr)
            return 1
        for path, number, _, key in items:
            if key in failures:
                print(f"ERROR: {path}, diagram #{number}\n{failures[key]}", file=sys.stderr)
                errors.append(key)
        save_cache(cache_path, signature, passed)
    print(f"Total diagrams validated: {len(items)} ({cached} cached, {len(pending)} rendered); total errors: {len(errors)}", flush=True)
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
