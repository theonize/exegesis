---
name: create-study
description: Produce a 2pp handout and detailed leader's notes from an existing exegetical research file. Accepts a passage ref, topic or character name, or file path. Usage: /create-study <passage|topic|path> [output-dir]
---

# Create-Study Skill — Handout + Leader's Notes

Transform a completed exegetical research file into two teaching deliverables:

1. **Handout** — ~900–1200 words, easily digestible, designed to prompt deeper study.
2. **Leader's notes** — bullet-dense, essentially line-by-line through the basis text, with a fuller overview and discussion-leader cues.

This skill **does not perform fresh exegesis**. Every claim in the outputs must trace back to the source research file. If the source omits something the study would need, note the gap rather than invent content.

Usage: `/create-study <passage|topic|path> [output-dir]`

Examples:
- `/create-study HAG 02:20-23`
- `/create-study Gold`
- `/create-study content/Topics/Chroma/Gold.md`
- `/create-study HAG 01:1-11 studies/winter-2026`

## Step 0 — Resolve the input to a source file

**Argument splitting rule** (topic names may contain spaces, and passage refs always do): first try the ENTIRE argument string as the source. Only if that fails AND the final whitespace-separated token contains `/` or `\` or names an existing directory, treat that final token as `[output-dir]` and retry the remainder as the source. Never split a topic name on spaces otherwise. Example: `/create-study Holy Ground` → topic `content/Topics/Holy Ground.md`; `/create-study HAG 01:1-11 studies/winter-2026` → source `HAG 01:1-11`, output-dir `studies/winter-2026`.

Resolve the source by trying these patterns in order:

1. **Passage reference** — normalize first: uppercase the book code; then match `^[1-3]?[A-Z]{2,3}\s+\d{1,3}:\S+$` (e.g. `HAG 02:20-23`, `MRK 08:31-9:1`, `1SA 17:1-58`, `PSA 023:1-6`).
   - Resolve to `content/Books/<TESTAMENT>/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`.
   - Use the OT/NT split from the book-code table below.
   - `CHAPTER` = the **starting** chapter, zero-padded to match the tree (2 digits for most books; 3 digits for Psalms).
   - `VERSES` = everything after the first colon, with any remaining colon replaced by an underscore (cross-chapter ranges). The second chapter in a cross-chapter range is NOT zero-padded. Verse numbers are NEVER zero-padded in filenames (strip leading zeros); only chapters are.
   - Worked examples: `HAG 02:20-23` → `content/Books/OT/HAG/02/HAG_02_20-23.md`; `MRK 08:31-9:1` → `content/Books/NT/MRK/08/MRK_08_31-9_1.md`; `ECC 09:13-10:4` → `content/Books/OT/ECC/09/ECC_09_13-10_4.md`; `PSA 23:1-6` → `content/Books/OT/PSA/023/PSA_023_1-6.md`.
   - **Range fallback**: if the constructed path does not exist, glob `content/Books/*/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_*.md`. If exactly one file's verse range contains or overlaps the requested verses, use it and say so in the report. If zero or several qualify, halt and list the chapter's available files so the user can pick.
2. **Existing file path** — argument contains `/` or `\` or ends in `.md`, and the file exists. Use directly.
3. **Topic or character name** — anything else. Try in order:
   - `content/Topics/<arg>.md`
   - `content/Characters/<arg>.md`
   - Glob `content/Topics/**/<arg>.md`. If the glob returns more than one match, halt and list the matches.

If no file is found after all branches, **halt with a clear error message**. Do not fabricate content.

## Step 1 — Read the source research file in full

Read the resolved file end-to-end. This is the **sole basis** for both outputs.

Identify these sections in the source (they may not all be present):
- Scripture block (the `> **1** ...` blockquote)
- `## Historical & Cultural Analysis`
- `## Linguistic Analysis`
- `## Literary Analysis`
- `## Theological Analysis`
- `## Hermeneutic`
- `## Application`

Note the **title** (first H1), and for passages, **identify each verse** (or for topics, each major section).

If the source has **no scripture blockquote**, omit the `## Verses` section from BOTH outputs — never reconstruct Scripture from memory (consistent with the no-fresh-exegesis rule).

## Step 2 — Generate the leader's notes (do this FIRST)

Leader's notes are the superset; the handout is a distillation. Generating in this order keeps the two documents consistent.

**Filename**: `<source-basename>_leader.md` (e.g. `HAG_01_1-11.md` → `HAG_01_1-11_leader.md`). For topics in subfolders, prefix the subfolder to keep output names unique in the flat output dir (e.g. `Chroma/Gold.md` → `Chroma_Gold_leader.md`).

**Structure** (top-level sections separated by `---`):

```markdown
# Leader's Notes — {source title without the leading "Exegetical Analysis of"}

## Verses

{reproduce the scripture blockquote from the source unchanged}

---

## Overview

{bullet-dense, ~300–500 words}

---

## Topics

- **{Topic}** — {one line: what the passage says about it, and where}
...

---

## Info

### v.1
- {bullet}
- {bullet}

### v.2
- {bullet}
...

---

## Discussion

1. {question}
   - **Leader's note:** {direction + key text/principle}
...
```

**Overview section** (300–500 words, mostly bullets):
- **Setting** — date, place, audience (from Historical & Cultural)
- **Author / speaker** and immediate context within the book (from Literary)
- **Genre and literary frame** (from Literary)
- **Big idea** — one sentence
- **Supporting movements** — 2–4 bullets

**Topics section** — **1–4 topics** the passage actually addresses (fewer is better than padded). Each is a short label (2–4 words) plus one line naming what the passage says about it and the verse(s) where it surfaces. Draw the labels from the source's Theological / Hermeneutic sections; do not invent topics the source never treats. These same topics carry into the handout unchanged.

**Info section** — go line-by-line:
- For **passages**: one `### v.N` subsection per verse in the passage. For each verse, 4–8 short bullets pulling from across the source: key original-language terms, historical/cultural notes, literary observations, theological weight, cross-references. Keep bullets scannable — half a line each where possible.
- For **topics**: replace `### v.N` with `### {Subsection Heading}` mirroring the source's major sections.

**Discussion section** — **at most 4 questions**, a single numbered list (no Observation/Interpretation/Application subheadings). Fewer than 4 is fine when the passage is short or narrow; never exceed 4.
- Across the set, move from observation → interpretation → application, so the group works the text before applying it. Pull the applying question(s) from the source's `## Application`.
- Under each numbered question, one `**Leader's note:**` bullet summarizing the expected direction of discussion and the key text/principle to surface.
- These are the **same questions** that go in the handout, verbatim — the handout just drops the leader's notes.

**Gaps section** (leader's notes only, optional): this skill's rule is "note the gap rather than invent content" — gap notes live here. If the source lacked anything the study needed (a verse never analyzed, no application material, missing scripture block), add a final `## Gaps in the Source` section listing each gap in one bullet. Omit the section when there are no gaps. Keep the handout clean — no gaps section there.

## Step 3 — Generate the handout

Target **900–1200 words total**. Same sections as leader's notes, much terser, no leader cues.

**Filename**: `<source-basename>_handout.md` (e.g. `HAG_01_1-11.md` → `HAG_01_1-11_handout.md`), with the same subfolder prefix rule as the leader's notes.

**Structure**:

```markdown
# {source title without the leading "Exegetical Analysis of"} — Study Handout

## Verses

{same scripture blockquote as leader's notes}

---

## Overview

{120–200 words tight prose}

**Big idea:** {one sentence}

---

## Topics

- **{Topic}** — {one line}
...

---

## Info

### v.1
- {bullet}
- {bullet}
...

---

## Discussion

1. {question}
2. {question}
...
```

**Overview** — ~120–200 words. Tight prose paragraph(s) orienting the reader, ending with a `**Big idea:**` line.

**Topics** — the **1–4 topics** from the leader's notes, carried over unchanged: bolded label plus one line each. This is the at-a-glance highlight of what the passage addresses; keep it under ~60 words.

**Info** — ~400–600 words total. Terse bullets per verse/unit; prefer **2–4 bullets per verse** over 6–8. Designed to prompt deeper study, not exhaust the source.

**Discussion** — **at most 4** open-ended questions (fewer is fine), no leader notes. Same questions as the leader's notes, in the same order, verbatim. Suitable for a small group cold.

**Length discipline**: the handout MUST stay within ~1200 words. If the source is unusually rich, prune rather than overflow.

## Step 4 — Write both files

Default output directory: `studies/` at the project root.

If the user passed a second argument, use that as the output directory instead.

Create the output directory if it does not exist.

**Overwrite guard**: if either target file already exists, stop and ask the user before replacing it.

Before writing, run a word count on the handout; if it exceeds ~1,200 words, prune it first (the cap in Step 3 is a hard limit).

Write **both** files. Then append one row to `studies/INDEX.md` (create it with a header row if missing):

```markdown
| <source path> | <handout path> | <leader path> | <YYYY-MM-DD> |
```

Report the two paths, a one-line summary (word count) for each, and the number of gaps noted (0 if none).

Do **not** modify `TODO.md` — that file tracks research, not studies. `studies/INDEX.md` is the studies tracker; a source file newer than its INDEX row means the study is stale.

## Formatting (carry from CLAUDE.md)

- Original-language terms: `**term** (Hebrew/Greek/Aramaic: script, *transliteration*)`
- Biblical citations: `Book Chapter:Verses`
- Verse refs inside the target passage: `(v.1)`, `(vv.1-5)`
- Top-level sections: `##`; subsections: `###`
- Separators: `---` between each `##` section
- Tone: clear, confessional/evangelical, no narrow tradition; scholar addressing motivated amateurs

## Book Code → Testament + Full Name

OT books (TESTAMENT = `OT`):
GEN Genesis · EXO Exodus · LEV Leviticus · NUM Numbers · DEU Deuteronomy · JOS Joshua · JDG Judges · RUT Ruth · 1SA 1 Samuel · 2SA 2 Samuel · 1KI 1 Kings · 2KI 2 Kings · 1CH 1 Chronicles · 2CH 2 Chronicles · EZR Ezra · NEH Nehemiah · EST Esther · JOB Job · PSA Psalms · PRO Proverbs · ECC Ecclesiastes · SNG Song of Solomon · ISA Isaiah · JER Jeremiah · LAM Lamentations · EZK Ezekiel · DAN Daniel · HOS Hosea · JOL Joel · AMO Amos · OBA Obadiah · JON Jonah · MIC Micah · NAH Nahum · HAB Habakkuk · ZEP Zephaniah · HAG Haggai · ZEC Zechariah · MAL Malachi

NT books (TESTAMENT = `NT`):
MAT Matthew · MRK Mark · LUK Luke · JHN John · ACT Acts · ROM Romans · 1CO 1 Corinthians · 2CO 2 Corinthians · GAL Galatians · EPH Ephesians · PHP Philippians · COL Colossians · 1TH 1 Thessalonians · 2TH 2 Thessalonians · 1TI 1 Timothy · 2TI 2 Timothy · TIT Titus · PHM Philemon · HEB Hebrews · JAS James · 1PE 1 Peter · 2PE 2 Peter · 1JN 1 John · 2JN 2 John · 3JN 3 John · JUD Jude · REV Revelation

Psalms use 3-digit chapter padding (001–150). All other books use 2-digit chapter padding.
