---
name: revisit
description: Re-examine and improve an existing exegetical study. Use when a newer model, a new discovery, updated scholarship, or new resources should inform prior research, or when an older study needs bringing up to current section contracts. Accepts a passage ref, chapter, topic or character name, or file path, plus optional context after `--`. Usage: /revisit <passage|chapter|topic|path> [-- context]
---

# Revisit Skill — Review & Improve an Existing Study

Given a target that resolves to one or more **existing** study files, re-run the six analysis seats in review mode over each file: every seat examines the whole document, rewrites its own section to preserve what survives scrutiny and improve what does not, and the bibliographer re-verifies the result before it replaces the original.

This skill never creates a new study — a target with no existing file is an error (point the user to `/research`). It follows the same pipeline shape as the `research` skill, with review posture instead of fresh composition.

Failure rule (applies throughout): a run **fails** for a file when one or more seat subagents fail or return empty/garbage output after one retry, or when the bibliographer pass cannot complete. On failure, **leave the original file untouched**, discard the draft, and report which stage failed. Never write a partially revised document. `TODO.md` is never modified by this skill.

## Step 0: Parse the Arguments

If the argument string contains ` -- `, split once on it: the left side is the **target**, the right side is the **review context** — free text describing what prompted the revisit (a new discovery, updated scholarship, a newer model, a resource now available). Otherwise the whole string is the target and the context is empty. The context is passed verbatim to every seat and to the bibliographer.

Examples:

- `/revisit HAG 02:20-23`
- `/revisit JAS 01 -- re-examine with current scholarship on diaspora audience`
- `/revisit Holy Ground -- 2025 Mount Ebal tablet re-dating`
- `/revisit content/Topics/Chroma/Gold.md`

## Step 1: Resolve the Target to Existing File(s)

Resolve using the **same rules as `create-study` Step 0** (read `C:\writ\exegesis\.claude\skills\create-study\SKILL.md` — passage normalization with worked examples, cross-chapter ranges, range fallback glob, file paths, Topics/Characters branches, whole-argument-first splitting). Two extensions:

1. **Chapter target** — `BOOK CH` with no colon (e.g. `JAS 01`): resolve to **every** `.md` file in `content/Books/*/<BOOK_CODE>/<CHAPTER>/`.
2. **Directory target** — an argument naming an existing directory under `content/`: resolve to every `.md` file directly inside it.

Multiple files are processed **sequentially** — run Steps 2–7 to completion for one file before starting the next.

If nothing resolves, **halt with a clear error**: list the nearest existing files (e.g. the chapter folder's contents) and suggest `/research` if the passage has never been studied. Never fabricate a target and never create a new file.

## Step 2: Read the Original in Full

Read the resolved file end-to-end and identify:

- The title (first H1) — carried into the revision **verbatim**.
- The scripture blockquote and its attribution line (translation name), if present.
- Each of the six standard sections (the table in Step 4), noting any that are missing.
- Any **non-standard `## ` sections** (e.g. `## Overview`, `## Curated Passage Index`, `## Key Passages Reference`) — these are carried over verbatim in their original positions; no seat owns them.
- `## Sources`, if present — it is **dropped** from the draft; the bibliographer rebuilds it in Step 6.
- Legacy shape (extra unnumbered subsections, `---` inside sections): note it — the seats normalize their own sections to current contracts.

Copy the original to the scratchpad as a snapshot before any other step touches it.

If the file has none of the six standard sections, it is not a study this skill can revise: halt for that file and report.

## Step 3: Verify the Scripture Block

If the original has a scripture blockquote: fetch the same passage in the **same translation named in the attribution line** from a source (`RESOURCES.md` — Bible Gateway, Bible Hub, Step Bible, Blue Letter Bible — or the `underrow` MCP service). Check verse count and wording.

- Matches: keep the block as is.
- Drifts from the fetched text: replace the block with the fetched text and log the correction.
- Cannot be fetched after reasonable attempts: keep the existing block **unchanged** and flag it in the report. **Never regenerate Scripture from memory.** This is not a fatal failure — the text already exists in the file.

If the original has no scripture blockquote (some topic studies), skip this step; do not add one.

## Step 4: Fan Out Six Review Subagents IN PARALLEL

Launch **six subagents with the Agent tool in a SINGLE message** (this is what makes them run concurrently — Skill-tool calls do not). Each seat reviews the whole document but rewrites only its own section.

Prompt template for each subagent (one per skill: historian, linguist, author, theologian, disciple, shepherd):

```
You are REVISING one section of an existing exegetical analysis — not writing it fresh.

Study file (read it in full for context): {original file path}
Your section: the one beginning `{expected ## heading}`.
Review context from the user (may be empty): {context}

1. Read C:\writ\exegesis\.claude\skills\{skill}\SKILL.md — its questions, its `## ` heading, its numbered `### ` subsections, and its Formatting rules define the CURRENT contract for your section.
2. Review posture — preserve what survives scrutiny:
   - Keep existing material that is accurate, well-supported, and on-contract. Do not paraphrase sound prose for the sake of change.
   - Correct what is wrong; hedge or cut what is unsupported, padded, or off-topic.
   - Update what newer discoveries, scholarship, or your own current knowledge supersede — weigh the review context above.
   - Deepen what is thin: answer contract questions the section skipped or shortchanged.
   - Restructure to the exact current contract (numbered `### ` subsections) if the section is missing, mis-ordered, or in legacy shape.
3. Follow the Formatting section of C:\writ\exegesis\CLAUDE.md. Do not emit `---` inside your section.
4. Write your COMPLETE revised section (starting with its `## ` heading) to {scratchpad}\{source-basename}_{skill}.md — a full replacement, not a diff. If the section needs no changes, write it verbatim.
5. Return the absolute path you wrote and a bullet-list change summary (or "no changes").
```

| Skill | Expected heading |
|-------|------------------|
| historian | `## Historical & Cultural Analysis` |
| linguist | `## Linguistic Analysis` |
| author | `## Literary Analysis` |
| theologian | `## Theological Analysis` |
| disciple | `## Hermeneutic` |
| shepherd | `## Application` |

A section missing from the original is still assigned: its seat writes it fresh from the study's passage/topic (note this in the report).

When a subagent returns, check its file exists, is non-trivial, and begins with the expected `## ` heading. If a subagent failed or its output is empty/garbage, retry that one subagent **once**. If it fails again, the run fails for this file: original untouched, report which section.

Collect every seat's change summary for the final report.

## Step 5: Compile the Draft (Mechanical — Never Regenerate)

Assemble a draft in the scratchpad by **concatenation only** — do not re-type, summarize, or "improve" section content:

1. The original title line, verbatim.
2. The scripture blockquote from Step 3 (if the original had one).
3. All `## ` sections **in the original document's order**, substituting each of the six standard sections with its seat's revised file and carrying every non-standard section over verbatim from the snapshot. Seats whose sections were missing from the original slot into the standard order (the table in Step 4, matching `AGENTS.md`). Omit the old `## Sources`.
4. `---` on its own line between the title/scripture block and each `## ` section — never inside one.

## Step 6: Bibliographer Verification Pass

Launch one subagent: "Read C:\writ\exegesis\.claude\skills\bibliographer\SKILL.md and apply it to {draft path}. Revision context (may be empty): {context}. Pay first attention to newly added or changed claims — compare against the snapshot at {snapshot path}. Edit the draft in place and return your verification report."

The bibliographer verifies Strong's numbers, original-language forms, cross-references, quotations, and dates; hedges or removes what cannot be verified; and appends a fresh `## Sources` section. If the pass cannot complete, the run fails for this file: original untouched.

## Step 7: Replace the Original (Gated)

Gate before writing: the draft must contain the original title, the scripture blockquote (when the original had one), all six exact `## ` headings from the table in Step 4, every non-standard section preserved from the original, and `## Sources`. If the gate fails, the run fails for this file: original untouched, report why.

Overwrite the original file with the draft in a single write. Git history preserves the prior version — no backup copies in `content/`.

Report per file:

- Path revised, and the review context applied.
- Scripture verification result (verified / corrected / source unreachable).
- Each seat's change summary ("no changes" included).
- The bibliographer's correction count and unresolved flags.
- If the file appears in `studies/INDEX.md`, note that its handout and leader's notes are now stale (regenerate via `/create-study`).

Do **not** modify `TODO.md` (revisited passages stay `[✅]`). Offer (do not perform unasked) a single commit covering the revised file(s).
