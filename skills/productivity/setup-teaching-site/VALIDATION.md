# Fast validation for teaching sites

Use the bundled [Python entrypoint](scripts/validate_mermaid.py) and [JavaScript renderer](scripts/validate_mermaid.mjs) together. They replace the older approach of running `npx` and a new browser for every diagram.

## Upgrade an existing site

1. Copy both files from this setup skill's `scripts/` directory into the other site's `.agents/skills/teach/scripts/` directory, replacing its old validator.
2. Preserve that project's dependency manager and existing packages. Add exact development dependencies `@mermaid-js/mermaid-cli@12.0.0` and `puppeteer@25.16.0`, and commit the lockfile. Install once, including Puppeteer's browser. On later checkouts use the dependency manager's locked install.
3. Ignore `.tools/` and `node_modules/`. The validation cache belongs under `.tools/validation/`; Zensical clears its own `.cache/` during clean builds.
4. Update the site's `/teach` verification instructions to run the validator once after edits, followed by a whole-site link check when available and `uv run zensical build`. Use `--clean` for initial setup, publishing, or cache troubleshooting. Run executable-example tests when their code changes.
5. Verify that a cold run renders diagrams, the next unchanged run reports cached passes, and `--force` deliberately re-renders them.

```bash
uv run python .agents/skills/teach/scripts/validate_mermaid.py
uv run python .agents/skills/teach/scripts/validate_mermaid.py --force
```

Append existing edited Markdown paths for a focused check. Do a whole-site pass before handoff; keep whole-site link checks to catch incoming links after a target is renamed or deleted.

## What the cache guarantees

- A pass is stored only after a real SVG render succeeds. Failed diagrams are retried and retain their file/block diagnostics.
- Diagram content determines reuse, so moving or duplicating a diagram does not require another render. Prose-only edits reuse existing passes.
- Validator code, renderer package versions, and dependency lockfiles invalidate previous passes when they change.
- Missing or corrupted caches trigger fresh rendering. Cache hits do not require starting Node or a browser.
- All pending unique diagrams run through one browser with bounded page concurrency. Validation never downloads tools or invokes `npx`.

New sites use this version when scaffolded from the updated setup skill. Existing sites contain independent skill copies and need the file/dependency upgrade above.
