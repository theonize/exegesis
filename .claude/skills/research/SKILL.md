---
name: research
description: Run a complete exegetical analysis of a Bible passage. Fetches the passage text, fans out six analysis subagents in parallel, compiles the draft, runs a critic reasoning audit and a bibliographer verification pass, writes the file, and updates TODO.md. Usage: /research <passage>
---

# Research Skill — Complete Exegetical Analysis

Given a passage reference (e.g., "HAG 02:20-23" or "Genesis 1:1-25"), perform a complete exegetical analysis.

Failure rule (applies throughout): a run **fails** when one or more analysis subagents fail or return empty/garbage output after one retry, when the passage text cannot be fetched, or when the critic or verification pass cannot complete. On failure, set the TODO.md entry to `[❌]` and report which stage failed. Never mark `[✅]` on a partial document.

## Step 0: Parse the Reference

Extract BOOK_CODE, CHAPTER, and VERSES from the input. Use the mapping below for full book names.

## Step 1: Claim the Passage

Open `TODO.md` and find the matching entry:

- `[ ]` — change to `[🔄]` and proceed.
- `[🔄]` — a stale claim from a dead session; note this in your report, keep it `[🔄]`, and proceed.
- `[✅]` — already complete. Stop and ask the user before redoing it.
- `[❌]` — a prior failed run; change to `[🔄]` and proceed.
- No entry — append one to the book's section in TODO.md with a short description, marked `[🔄]`.

Take the passage description from the TODO.md entry. If the entry had no description (or you created it), write the description you use for the document title back into the TODO.md entry so the queue and the file stay in sync.

## Step 2: Fetch the Passage Text

**Never reproduce Scripture from memory.** Fetch the passage text from an online source (see `RESOURCES.md` — Bible Gateway, Bible Hub, Step Bible, and Blue Letter Bible all serve passage text), or from the `underrow` MCP service if it exposes verse text.

- **Translation choice is yours**: pick the translation best suited to the passage, and use more than one where comparison illuminates (the linguist's translation-comparison table is the natural home for alternates). Prefer translations whose licenses permit full-passage quotation (e.g., public-domain WEB, KJV, BSB); when quoting a restricted translation (ESV, NIV, NASB), keep within its quotation policy.
- Sanity check: the fetched text must contain exactly the verses in the requested range — count them.
- Format as a blockquote; the attribution line must name the translation actually used:

```
> **1** Verse text...
>
> **2** More verse text...
>
> — *Translation Name (ABBR)*
```

If the text cannot be fetched after reasonable attempts, this is a failed run: set `[❌]` and stop.

## Step 3: Fan Out Six Analysis Subagents IN PARALLEL

Launch **six subagents with the Agent tool in a SINGLE message** (this is what makes them run concurrently — Skill-tool calls do not). Each subagent gets a fresh context window, which keeps every section at full depth.

Prompt template for each subagent (one per skill: historian, linguist, author, theologian, disciple, shepherd):

```
You are producing one section of an exegetical analysis of {Full Book Name} {Chapter}:{Verses}.

Passage text ({Translation}):
{fetched blockquote}

1. Read C:\writ\exegesis\.claude\skills\{skill}\SKILL.md and follow it exactly — its questions, its `## ` heading, its numbered `### ` subsections, and its Formatting rules.
2. Also follow the Formatting section of C:\writ\exegesis\CLAUDE.md. Do not emit `---` inside your section.
3. Write ONLY your section (starting with its `## ` heading) to {scratchpad}\{BOOK}_{CHAPTER}_{VERSES}_{skill}.md.
4. Return the absolute path you wrote and a one-line status.
```

When a subagent returns, check its file exists, is non-trivial, and begins with the expected `## ` heading:

| Skill | Expected heading |
|-------|------------------|
| historian | `## Historical & Cultural Analysis` |
| linguist | `## Linguistic Analysis` |
| author | `## Literary Analysis` |
| theologian | `## Theological Analysis` |
| disciple | `## Hermeneutic` |
| shepherd | `## Application` |

If a subagent failed or its output is empty/garbage, retry that one subagent **once**. If it fails again, the run fails: `[❌]`, report which section.

## Step 4: Compile the Draft (Mechanical — Never Regenerate)

Assemble a draft in the scratchpad by **concatenation only** — do not re-type, summarize, or "improve" section content:

1. Title: `# Exegetical Analysis of {Full Book Name} {Chapter}:{Verses} - {Description}`
2. The fetched scripture blockquote
3. The six section files, in the order of the table above, with `---` on its own line between the title/scripture block and each `## ` section

## Step 5: Critic Reasoning Audit

The six seats wrote in isolation and never saw each other's work. This is the first pass over the whole document, and the only one that can catch what falls between sections.

Launch one subagent: "Read C:\writ\exegesis\.claude\skills\critic\SKILL.md and apply it to {draft path}. Edit the draft in place and return your critique report."

The critic audits reasoning, not citations: cross-section contradictions, confidence language outstripping its evidence, exegetical fallacies, inference gaps, cruxes presented as settled, and applications not grounded in the exegesis. It edits surgically within the constraints in its skill — it never re-drafts a section, changes headings, or touches the scripture blockquote. A report of zero findings is a valid outcome, not a failed pass; the run fails only if the pass cannot complete or the draft comes back structurally damaged (a missing or renamed `## ` heading).

The critic runs **before** the bibliographer so any hedge or counter-reading it introduces is itself fact-checked, and so `## Sources` is compiled against the final text.

## Step 6: Bibliographer Verification Pass

Launch one subagent: "Read C:\writ\exegesis\.claude\skills\bibliographer\SKILL.md and apply it to {draft path}. Edit the draft in place and return your verification report."

The bibliographer verifies Strong's numbers, original-language forms, cross-references, quotations, and dates; hedges or removes what cannot be verified; and appends the `## Sources` section. If the pass cannot complete, the run fails: `[❌]`.

## Step 7: Write the Output

1. Determine the testament folder: `OT` for Genesis through Malachi, `NT` for Matthew through Revelation.
2. Create directory `content/Books/<TESTAMENT>/<BOOK_CODE>/<CHAPTER>/` if it does not exist.
   - CHAPTER is zero-padded to match the existing tree: 01, 02, etc.; Psalms use three digits (001–150).
3. Target: `content/Books/<TESTAMENT>/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`
   - Example: HAG 02:20-23 -> `content/Books/OT/HAG/02/HAG_02_20-23.md`
4. **Overwrite guard**: if the target already exists, stop and ask the user before replacing it (it may be hand-edited). An existing file alongside a `[ ]` TODO entry is an inconsistency — surface it.
5. Copy the verified draft to the target.

## Step 8: Mark Complete

Gate before flipping the status: the written file must contain the scripture blockquote, all six exact `## ` headings from the table in Step 3, and `## Sources`. Only then change `[🔄]` to `[✅]` in `TODO.md`.

Report: the output path, the TODO.md change, the critic's fixed/flagged counts (surface every flagged item — those are for you, not the file), the bibliographer's correction count, and offer (do not perform unasked) a single commit covering both changed files.

## Book Code ↔ Full Name

| Code | Name | Code | Name | Code | Name |
|------|------|------|------|------|------|
| GEN | Genesis | JOS | Joshua | PSA | Psalms |
| EXO | Exodus | JDG | Judges | PRO | Proverbs |
| LEV | Leviticus | RUT | Ruth | ECC | Ecclesiastes |
| NUM | Numbers | 1SA | 1 Samuel | SNG | Song of Solomon |
| DEU | Deuteronomy | 2SA | 2 Samuel | ISA | Isaiah |
| JOB | Job | 1KI | 1 Kings | JER | Jeremiah |
| EST | Esther | 2KI | 2 Kings | LAM | Lamentations |
| EZR | Ezra | 1CH | 1 Chronicles | EZK | Ezekiel |
| NEH | Nehemiah | 2CH | 2 Chronicles | DAN | Daniel |
| HOS | Hosea | JOL | Joel | AMO | Amos |
| OBA | Obadiah | JON | Jonah | MIC | Micah |
| NAH | Nahum | HAB | Habakkuk | ZEP | Zephaniah |
| HAG | Haggai | ZEC | Zechariah | MAL | Malachi |
| MAT | Matthew | MRK | Mark | LUK | Luke |
| JHN | John | ACT | Acts | ROM | Romans |
| 1CO | 1 Corinthians | 2CO | 2 Corinthians | GAL | Galatians |
| EPH | Ephesians | PHP | Philippians | COL | Colossians |
| 1TH | 1 Thessalonians | 2TH | 2 Thessalonians | 1TI | 1 Timothy |
| 2TI | 2 Timothy | TIT | Titus | PHM | Philemon |
| HEB | Hebrews | JAS | James | 1PE | 1 Peter |
| 2PE | 2 Peter | 1JN | 1 John | 2JN | 2 John |
| 3JN | 3 John | JUD | Jude | REV | Revelation |
