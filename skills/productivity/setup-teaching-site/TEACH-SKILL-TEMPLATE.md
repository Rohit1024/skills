# Enhanced `/teach` Skill Specification & Templates

This document contains the exact files to scaffold into `.agents/skills/teach/` for the target teaching workspace.

---

## 1. `.agents/skills/teach/SKILL.md`

```markdown
---
name: teach
description: Teach a concept step-by-step within this workspace.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

# Teaching Workspace

Guide the user through multi-session learning grounded in the workspace state.

## Workspace State

- `docs/mission.md`: The guiding compass and user goals. Ground all teaching here. See [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `docs/lessons/`: Sequential lessons (`NNNN-<slug>.md`). Maintained in `docs/lessons/index.md`.
- `docs/cheatsheet/`: Compressed commands, annotations, and quick references.
- `docs/debugging/`: Diagnostic playbooks with failure sequence diagrams.
- `docs/interview/`: Senior technical and system design question bank.
- `docs/references/`: Official sources (`resources.md`), glossary (`glossary.md`), and reference index (`index.md`).
- `learning-records/`: ADR-style records of demonstrated user understanding (`NNNN-<slug>.md`). See [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `NOTES.md`: Scratchpad for learner profile and working notes.

## Core Rules

1. **Ground in Mission**: Align every lesson with `docs/mission.md`. If unclear, interview the user first.
2. **High-Trust Knowledge**: Source facts from `docs/references/resources.md`. Verify facts before explaining.
3. **Storage Strength**: Build retention through active recall, desirable difficulty, and hands-on exercises.

## Authoring Lessons

1. **File Location**: Save self-contained lessons to `docs/lessons/NNNN-<slug>.md`.
2. **Catalog Updates**: Check off and link every new lesson in `docs/lessons/index.md`.
3. **Sidebar Rule**: Expose only top-level section roots in `zensical.toml` `nav` (e.g. `{ "Lessons" = ["lessons/index.md"] }`). Keep individual lessons cataloged inside `docs/lessons/index.md`.
4. **Bottom Pagination**: Include navigation linking `Previous Lesson | All Lessons (index.md) | Next Lesson`. Update the previous lesson's "Next" link when adding a lesson.
5. **Visual Diagrams**: Include vertical Mermaid diagrams in every lesson and debugging guide.
6. **Zensical Styling**: Use admonitions (`!!! note`, `!!! tip`), code annotations, and copy buttons.

## Authoring Reference & Debugging Guides

- Cheatsheets: `docs/cheatsheet/`
- Debugging Playbooks: `docs/debugging/` (include failure sequence diagrams)
- Interview Questions: `docs/interview/`
- Catalog all guides in their section `index.md` with bottom pagination tables.

## Mermaid Standards & Verification

### Layout Standards
- **Orientation**: Default to `flowchart TD` (top-to-bottom).
- **Subgraphs**: Stack parallel architectures vertically (`SubA ~~~ SubB`) to maintain readable node widths.
- **Quoted Labels**: Quote node labels with special characters (e.g., `Node["Item (Details)"]`).

### Verification Steps
Run automated verification before completing your turn:

1. Validate diagrams with the local renderer (must report 0 errors):
   ```bash
   uv run python .agents/skills/teach/scripts/validate_mermaid.py
   ```
   Successful renders are cached by content and validator/dependency versions. Unchanged diagrams skip Node and browser startup. Append edited Markdown paths for a focused check; use `--force` to re-render all selected diagrams. Dependencies are installed once during setup; never use `npx` or install tools during validation.
2. Run a whole-site link checker when the project supplies one, so renamed or deleted targets still invalidate incoming links. Run example tests only if executable example code changed.
3. Validate the documentation build once after all edits, using the incremental command:
   ```bash
   uv run zensical build
   ```
4. Report completion summary:
   - Number of Mermaid diagrams checked, newly rendered, and reused from cache (0 errors).
   - Zensical build status.

Use a clean build for initial setup or publishing. Do not rebuild the entire site or rerun unrelated scripts after each individual edit.
```

---

## 2. `.agents/skills/teach/MISSION-FORMAT.md`

```markdown
# mission.md Format

`docs/mission.md` lives under the `docs/` directory. It captures the _reason_ the user is learning this topic. Every teaching decision — what to teach next, which resources to surface, which exercises to design — should trace back to this document.

## Template

```md
---
icon: lucide/compass
---

# Mission: {Topic}

## Why

{1-3 sentences. The concrete real-world goal the user is chasing. What changes in their life or work when they have this skill? Avoid abstract framings like "to understand X" — push for the underlying outcome.}

## Success looks like

- {A specific, observable thing the user will be able to do}
- {Another specific thing}
- {…}

## Constraints

- {Time, budget, prior commitments, learning preferences, anything that bounds the approach}

## Out of scope

- {Adjacent topics the user explicitly does not want to chase right now — protects the zone of proximal development}
```

## Rules

- **One mission per workspace.**
- **Concrete over abstract.**
- **Push back on vagueness.**
- **Revise when reality shifts.** Update `docs/mission.md` and add a learning record.
- **Keep it short.**
```

---

## 3. `.agents/skills/teach/LEARNING-RECORD-FORMAT.md`

```markdown
# Learning Record Format

Learning records live in `./learning-records/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Create the directory lazily — only when the first record is written.

They are the teaching equivalent of ADRs: they capture non-obvious lessons, key insights, and stated prior knowledge that will steer future sessions. They are used to calculate the zone of proximal development.

## Template

```md
# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}
```

## Optional sections

- **Status** frontmatter (`active | superseded by LR-NNNN`)
- **Evidence** — how the user demonstrated the understanding.
- **Implications** — what this unlocks or rules out for future sessions.

## Numbering

Scan `./learning-records/` for the highest existing number and increment by one.

## When to write a learning record

1. **The user demonstrated genuine understanding of something non-trivial**.
2. **The user disclosed prior knowledge** — "I already know X."
3. **A misconception was corrected**.
4. **The mission shifted in response to learning**.
```

---

## 4. `.agents/skills/teach/RESOURCES-FORMAT.md`

```markdown
# resources.md Format

`docs/references/resources.md` is the curated set of trusted sources for this topic. Knowledge for explainers should be drawn from here, not from parametric guesses. Wisdom comes from the communities listed here.

## Structure

```md
# {Topic} Resources

## Knowledge

- [Book / Official Doc Name](https://example.com)
  Authoritative text. Use for: core syntax, internal mechanisms, and reference standards.

## Wisdom (Communities)

- [Community / Subreddit / Forum](https://example.com)
  High-signal community. Use for: real-world architectural feedback and troubleshooting.
```

## Rules

- **High-trust only.** Prefer primary sources and peer-reviewed materials.
- **Annotate every entry.** Add one line on what it covers and when to reach for it.
- **Group by Knowledge / Wisdom.**
- **Prune ruthlessly.**
```

---

## 5. `.agents/skills/teach/GLOSSARY-FORMAT.md`

```markdown
# glossary.md Format

`docs/references/glossary.md` is the canonical language for this teaching workspace. All explainers, exercises, and learning records should adhere to its terminology.

## Structure

```md
# {Topic} Glossary

{One or two sentence description of the topic this glossary covers.}

## Terms

**Term Name**:
Tight, 1–2 sentence definition of what the term IS.
_Avoid_: Ambiguous or misleading colloquial terms.
```

## Rules

- **Add a term only when the user understands it.**
- **Be opinionated.** Choose the best term and list aliases to avoid.
- **Keep definitions tight.** One or two sentences.
- **Use the glossary's own terms inside definitions.**
- **Group under subheadings** when natural clusters emerge.
```

---

## 6. `.agents/skills/teach/agents/openai.yaml`

```yaml
interface:
  display_name: "Teach"
  short_description: "Learn a concept in a guided workspace"
policy:
  allow_implicit_invocation: false
```

---

## 7–8. Mermaid validator pair

Copy the bundled files from the setup skill into the target project's teach skill:

| Setup skill source | Target path |
| --- | --- |
| `scripts/validate_mermaid.py` | `.agents/skills/teach/scripts/validate_mermaid.py` |
| `scripts/validate_mermaid.mjs` | `.agents/skills/teach/scripts/validate_mermaid.mjs` |

Keep these files together. The Python entrypoint scans Markdown, deduplicates diagrams, and caches successful checks by content and tool versions. The JavaScript helper renders all pending diagrams in one shared browser using the installed Mermaid CLI API. Copy the sources rather than embedding another version of their code in this template.

Install `@mermaid-js/mermaid-cli@12.0.0` and `puppeteer@25.16.0` as exact development dependencies using the project's package manager. Commit the lockfile. Keep `.tools/` and `node_modules/` ignored. On later checkouts, install dependencies from the lockfile once; neither validator downloads or installs anything.

```bash
uv run python .agents/skills/teach/scripts/validate_mermaid.py
uv run python .agents/skills/teach/scripts/validate_mermaid.py docs/lessons/0001-example.md
uv run python .agents/skills/teach/scripts/validate_mermaid.py --force
```

The example lesson path is illustrative; use an existing edited file. `--force` preserves full rendering verification when needed, and a corrupted cache triggers fresh validation. The cache lives in `.tools/validation/` so clean Zensical builds do not erase it.
