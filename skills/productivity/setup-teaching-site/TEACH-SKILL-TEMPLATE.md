# Enhanced `/teach` Skill Specification & Templates

This document contains the exact files to scaffold into `.agents/skills/teach/` for the target teaching workspace.

---

## 1. `.agents/skills/teach/SKILL.md`

```markdown
---
name: teach
description: Teach the user a new skill or concept, within this workspace.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## Teaching Workspace

Treat the current directory as a teaching workspace. The state of their learning is captured in this directory in several files:

- `docs/mission.md`: A document capturing the _reason_ the user is interested in the topic. This should be used to ground all teaching. Use the format in [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `docs/cheatsheet/`: A directory of cheatsheets (markdown files) and their `index.md`. These are compressed, command-focused, and visual learnings from the lessons designed for quick reference.
- `docs/debugging/`: A directory of diagnostic playbooks and error troubleshooting workflows with sequence diagrams.
- `docs/interview/`: A directory of technical and system design interview questions.
- `docs/references/resources.md`: A list of resources which can be explored to ground your teaching in contextual knowledge, or to acquire knowledge and wisdom. Use the format in [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `docs/references/index.md`: An index page for references and official external resource links.
- `docs/references/glossary.md`: Canonical terminology and standard nomenclature. Use the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).
- `./learning-records/*.md`: A directory of learning records, which capture what the user has learned (ADR-style). They are titled `0001-<dash-case-name>.md`, where the number increments each time. Use the format in [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `docs/lessons/*.md`: A directory of lessons. A **lesson** is a single, self-contained Markdown file that teaches one tightly-scoped thing tied to the mission. It is styled for Zensical. This is the primary unit of teaching in this workspace. The lessons list must be maintained in `docs/lessons/index.md`.
- `NOTES.md`: A scratchpad for you to jot down user preferences, learner profile, or working notes.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before `docs/references/resources.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust unverified parametric knowledge.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Design lessons which build long-term retention through desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice)

## Lessons

A lesson is the main artifact you produce — the unit in which knowledge and skills reach the user. Each lesson is one self-contained Markdown file, saved to `docs/lessons/` and titled `0001-<dash-case-name>.md` where the number increments each time.

**Navigation & Cataloging Rules**:
- **Do NOT add individual lessons to the sidebar in `zensical.toml`**. The `nav` section in `zensical.toml` must only expose top-level section roots (`{ "Lessons" = [ "lessons/index.md" ] }`).
- **Always update the folder catalog**: Every new lesson MUST be linked and documented with a checkmark in `docs/lessons/index.md`.
- **Always include Bottom Pagination**: Every lesson must have a bottom navigation block linking to the **Previous Lesson**, the catalog (`[All Lessons](index.md)`), and the **Next Lesson**.
- **Update Adjacent Predecessors**: Whenever a new lesson is authored, update the previous lesson's "Next" pagination link to point to the newly created lesson.
- Always verify with `uv run zensical build` to ensure all links resolve cleanly.

**Visual & Mermaid Requirement**:
- **Always include clear Mermaid diagrams** (flowcharts, sequence diagrams, state diagrams, or architecture maps) in every **Lesson** and **Debugging guide** to visualize runtime flows, lifecycles, and request paths.

A lesson should be styled beautifully based on Zensical's typography and structure (using `!!! note` or `!!! tip` admonitions, code annotations, copy buttons, and Mermaid blocks).

The lesson should be short and completable quickly within working memory. Each lesson should give the user a single tangible win directly tied to the mission within their zone of proximal development.

## The Mission

Every lesson should be tied into the mission in `docs/mission.md`. If unclear or unpopulated, interview the user to clarify concrete outcomes.

## Reference Documents, Debugging & Interview Question Playbooks

While creating lessons, also create and update:
- Cheatsheets (under `docs/cheatsheet/`)
- Reference files & glossary (under `docs/references/`)
- Debugging playbooks with failure sequence diagrams (under `docs/debugging/`)
- Interview question collections (under `docs/interview/`)

**Cataloging Rules for Reference Documents**:
1. Never add individual sub-files to the `zensical.toml` sidebar.
2. Catalog all files within their respective folder's `index.md`.
3. Include bottom pagination tables linking to the previous guide, folder index, and next guide.
4. Validate site generation using `uv run zensical build`.
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
