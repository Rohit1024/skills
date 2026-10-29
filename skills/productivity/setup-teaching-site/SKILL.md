---
name: setup-teaching-site
description: Scaffold a Zensical teaching workspace with the /teach skill.
disable-model-invocation: true
argument-hint: "<topic> [site_name] [site_url]"
---

# Setup Teaching Site

Scaffold an interactive [Zensical](https://zensical.org) teaching workspace configured with the `/teach` skill, curriculum modules, visual Mermaid diagrams, and GitHub Pages deployment.

## Execution Sequence

Execute these steps in order. Each step ends on a completion criterion that must be satisfied before proceeding.

### Step 1: Collect Inputs & Initialize Python Project

1. Resolve parameters from user arguments or prompt if missing:
   - **Topic**: e.g., `Kubernetes`, `Rust`, `Kafka`, `Spring Boot`
   - **Site Name**: e.g., `Learn Kubernetes Architecture`
   - **Author / GitHub Handle**: e.g., `rohit1024`
   - **Site URL**: e.g., `https://<github-handle>.github.io/<repo-name>`
2. Initialize project with `uv`:
   ```bash
   uv init --no-pin-python --python ">=3.14" .
   uv add --dev "zensical>=0.0.55"
   ```
3. Create `.gitignore`:
   ```gitignore
   .venv/
   site/
   .cache/
   .tools/
   node_modules/
   __pycache__/
   *.pyc
   .DS_Store
   ```

> **Completion Criterion**: `pyproject.toml` lists `zensical` in `dev` dependencies, `.venv` exists, and `uv run zensical --version` exits 0.

---

### Step 2: Retrieve Branding & SVG Logo

Fetch the topic's SVG logo from [SVGL](https://svgl.app) or generate a clean SVG badge per [SVGL-INTEGRATION.md](SVGL-INTEGRATION.md):

1. Create target directories:
   ```bash
   mkdir -p overrides/.icons/custom overrides/.icons/svgl docs/assets
   ```
2. Download the logo (e.g. `SLUG="kubernetes"`):
   ```bash
   curl -sSL "https://raw.githubusercontent.com/pheralb/svgl/main/static/library/${SLUG}.svg" -o "overrides/.icons/custom/${SLUG}.svg"
   cp "overrides/.icons/custom/${SLUG}.svg" "overrides/.icons/svgl/${SLUG}.svg"
   cp "overrides/.icons/custom/${SLUG}.svg" "docs/assets/${SLUG}-logo.svg"
   ```
3. Fallback: If download fails or offline, generate a clean high-contrast SVG badge matching the format in [SVGL-INTEGRATION.md](SVGL-INTEGRATION.md).

> **Completion Criterion**: `overrides/.icons/custom/<slug>.svg` and `docs/assets/<slug>-logo.svg` exist and contain valid `<svg>` XML markup.

---

### Step 3: Configure `zensical.toml` & GitHub Actions CI

1. Write `zensical.toml` at the project root using [ZENSICAL-CONFIG-TEMPLATE.md](ZENSICAL-CONFIG-TEMPLATE.md):
   - Substitute `{SITE_NAME}`, `{SITE_DESCRIPTION}`, `{SITE_AUTHOR}`, `{SITE_URL}`, `{TOPIC_SLUG}`, and `{YEAR}`.
   - Maintain top-level section roots in `nav` (never add individual lessons to `nav`).
2. Write `.github/workflows/docs.yml` using the workflow template in [ZENSICAL-CONFIG-TEMPLATE.md](ZENSICAL-CONFIG-TEMPLATE.md).

> **Completion Criterion**: `zensical.toml` and `.github/workflows/docs.yml` exist with all topic variables substituted.

---

### Step 4: Scaffold Documentation Portal Hierarchy

Create the documentation files using the templates in [CURRICULUM-TEMPLATES.md](CURRICULUM-TEMPLATES.md), populating all content with `<topic>`-specific modules, lessons, and Mermaid diagrams:

```text
docs/
├── assets/<topic-slug>-logo.svg
├── cheatsheet/index.md
├── debugging/index.md
├── interview/index.md
├── lessons/index.md
├── references/
│   ├── index.md
│   ├── resources.md
│   └── glossary.md
├── index.md
└── mission.md
learning-records/
NOTES.md
```

1. **`docs/index.md`**: Master portal home with quick navigation cards and Mermaid roadmap.
2. **`docs/mission.md`**: Mission compass (Why, Success looks like, Constraints, Out of scope).
3. **`docs/lessons/index.md`**: 6–9 progressive curriculum modules with 30–60 sequential lesson trackers.
4. **`docs/cheatsheet/index.md`**: Fast syntax, annotation, and command reference catalog.
5. **`docs/debugging/index.md`**: Diagnostic guide catalog for common runtime failures.
6. **`docs/interview/index.md`**: Senior technical and system design question bank.
7. **`docs/references/`**: Hub index (`index.md`), curated resources (`resources.md`), and living glossary (`glossary.md`).
8. **`learning-records/`**: Directory for ADR-style decision records.
9. **`NOTES.md`**: Learner profile, pedagogical preferences, and active module state.

> **Completion Criterion**: All 10 documentation files exist, contain `<topic>`-tailored content with valid Mermaid diagrams, and resolve all relative markdown links without broken references.

---

### Step 5: Install `/teach` Skill & Companion Files

Scaffold the `/teach` skill and verification tooling into `.agents/skills/teach/` from [TEACH-SKILL-TEMPLATE.md](TEACH-SKILL-TEMPLATE.md):

1. Create target directories:
   ```bash
   mkdir -p .agents/skills/teach/agents .agents/skills/teach/scripts
   ```
2. Write the six Markdown/YAML skill components from [TEACH-SKILL-TEMPLATE.md](TEACH-SKILL-TEMPLATE.md):
   - `.agents/skills/teach/SKILL.md`
   - `.agents/skills/teach/MISSION-FORMAT.md`
   - `.agents/skills/teach/LEARNING-RECORD-FORMAT.md`
   - `.agents/skills/teach/RESOURCES-FORMAT.md`
   - `.agents/skills/teach/GLOSSARY-FORMAT.md`
   - `.agents/skills/teach/agents/openai.yaml`
3. Copy the bundled validator pair from this setup skill's `scripts/` directory into the target skill. Use the bundled files as the source; do not recreate an older validator from memory:
   - `scripts/validate_mermaid.py` → `.agents/skills/teach/scripts/validate_mermaid.py`
   - `scripts/validate_mermaid.mjs` → `.agents/skills/teach/scripts/validate_mermaid.mjs`
4. Use Node.js 22.13 or newer and install locked local rendering dependencies once, preserving existing project dependencies and its package manager. For an npm project:
   ```bash
   npm install --save-dev --save-exact @mermaid-js/mermaid-cli@12.0.0 puppeteer@25.16.0
   ```
   Commit the package manifest and lockfile. If npm reports a blocked Puppeteer install script, use its package-specific approval command and rerun `npm ci` so its browser is installed. Validation must not run `npx`, install packages, or download tools.
5. Make the Python validation script executable:
   ```bash
   chmod +x .agents/skills/teach/scripts/validate_mermaid.py
   ```

> **Completion Criterion**: All eight skill components exist, the Python validator is executable, and the locked local Mermaid/Puppeteer dependencies are available.

---

### Step 6: Validate & Build Site

1. Validate diagrams with the installed validator:
   ```bash
   uv run python .agents/skills/teach/scripts/validate_mermaid.py
   ```
   It renders unique uncached diagrams in one browser and saves successful checks under `.tools/validation/`, outside Zensical's disposable `.cache/`. Cache keys include diagram content, validator code, renderer versions, and the lockfile. Failures are never cached as passes. A warm run must skip browser startup; `--force` deliberately re-renders all selected diagrams. Prefer explicit file paths while iterating on a lesson, followed by a whole-site pass at handoff.
2. Run one clean Zensical build for initial setup to verify configuration and asset links:
   ```bash
   uv run zensical build --clean
   ```
3. Verify exit status is 0 and `site/index.html` is generated without warnings or broken links.
4. Present summary to the user and prompt them to begin learning with `/teach`.

For later teaching edits, use `uv run zensical build` once after all edits. Reserve `--clean` for initial setup, publishing, or cache troubleshooting. Keep whole-site link checks when available, and run executable-example tests only when those examples change. Do not run every script after every individual page edit.

> **Completion Criterion**: `uv run zensical build --clean` exits with returncode 0 and produces `site/`.

---

## Disclosed Reference

- [VALIDATION.md](VALIDATION.md): Fast validator design and upgrade steps for existing teaching sites.
- [SVGL-INTEGRATION.md](SVGL-INTEGRATION.md): SVGL logo URLs, download commands, and fallback SVG generator.
- [ZENSICAL-CONFIG-TEMPLATE.md](ZENSICAL-CONFIG-TEMPLATE.md): Canonical `zensical.toml` and `.github/workflows/docs.yml` templates.
- [CURRICULUM-TEMPLATES.md](CURRICULUM-TEMPLATES.md): Portal templates for `docs/`, `learning-records/`, and `NOTES.md`.
- [TEACH-SKILL-TEMPLATE.md](TEACH-SKILL-TEMPLATE.md): Full `/teach` skill specifications and validation scripts.
