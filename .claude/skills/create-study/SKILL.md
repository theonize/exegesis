---
name: create-study
description: Produce a 2pp handout and detailed leader's notes from an existing exegetical research file. Accepts a passage ref, topic name, or file path. Usage: /create-study <passage|topic|path> [output-dir]
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

Parse the argument. Try these patterns in order:

1. **Passage reference** — matches `^[1-3]?[A-Z]{2,3}\s+\d{1,3}:\S+$` (e.g. `HAG 02:20-23`, `MRK 08:31-9:1`, `1SA 17:1-58`, `PSA 023:1-6`).
   - Resolve to `content/Books/<TESTAMENT>/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`.
   - Use the OT/NT split from the book-code table below.
   - Chapter is zero-padded to match the existing tree (2 digits for most books; 3 digits for Psalms).
2. **Existing file path** — argument contains `/` or `\` or ends in `.md`, and the file exists. Use directly.
3. **Topic name** — anything else. Try in order:
   - `content/Topics/<arg>.md`
   - Glob `content/Topics/**/<arg>.md` and take the first hit.

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

## Step 2 — Generate the leader's notes (do this FIRST)

Leader's notes are the superset; the handout is a distillation. Generating in this order keeps the two documents consistent.

**Filename**: `<source-basename>_leader.md` (e.g. `HAG_01_1-11.md` → `HAG_01_1-11_leader.md`).

**Structure** (top-level sections separated by `---`):

```markdown
# Leader's Notes — {source title without the leading "Exegetical Analysis of"}

## Verses

{reproduce the scripture blockquote from the source unchanged}

---

## Overview

{bullet-dense, ~300–500 words}

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

### Observation
1. {question}
   - **Leader's note:** {direction + key text/principle}
...

### Interpretation
...

### Application
...
```

**Overview section** (300–500 words, mostly bullets):
- **Setting** — date, place, audience (from Historical & Cultural)
- **Author / speaker** and immediate context within the book (from Literary)
- **Genre and literary frame** (from Literary)
- **Big idea** — one sentence
- **Supporting movements** — 2–4 bullets

**Info section** — go line-by-line:
- For **passages**: one `### v.N` subsection per verse in the passage. For each verse, 4–8 short bullets pulling from across the source: key original-language terms, historical/cultural notes, literary observations, theological weight, cross-references. Keep bullets scannable — half a line each where possible.
- For **topics**: replace `### v.N` with `### {Subsection Heading}` mirroring the source's major sections.

**Discussion section** — 8–12 total questions, grouped:
- **Observation** (3–4) — what the text says
- **Interpretation** (3–4) — what it means
- **Application** (3–4) — what it asks of us; pull from the source's `## Application`
- Under each numbered question, one `**Leader's note:**` bullet summarizing the expected direction of discussion and the key text/principle to surface.

## Step 3 — Generate the handout

Target **900–1200 words total**. Same four sections as leader's notes, much terser, no leader cues.

**Filename**: `<source-basename>_handout.md` (e.g. `HAG_01_1-11.md` → `HAG_01_1-11_handout.md`).

**Structure**:

```markdown
# {source title} — Study Handout

## Verses

{same scripture blockquote as leader's notes}

---

## Overview

{120–200 words tight prose}

**Big idea:** {one sentence}

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

**Info** — ~400–600 words total. Terse bullets per verse/unit; prefer **2–4 bullets per verse** over 6–8. Designed to prompt deeper study, not exhaust the source.

**Discussion** — 5–7 open-ended questions only (no leader notes), mixing observation / interpretation / application. Suitable for a small group cold.

**Length discipline**: the handout MUST stay within ~1200 words. If the source is unusually rich, prune rather than overflow.

## Step 4 — Write both files

Default output directory: `studies/` at the project root.

If the user passed a second argument, use that as the output directory instead.

Create the output directory if it does not exist.

Write **both** files. Report the two paths and a one-line summary (word count) for each.

Do **not** modify `TODO.md` — that file tracks research, not studies.

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
