---
name: research
description: Run a complete exegetical analysis of a Bible passage. Orchestrates all six analysis skills in parallel, compiles the results, and writes the output file. Usage: /research <passage>
---

# Research Skill — Complete Exegetical Analysis

Given a passage reference (e.g., "HAG 02:20-23" or "Genesis 1:1-25"), perform a complete exegetical analysis.

## Step 0: Parse the Reference

Extract BOOK_CODE, CHAPTER, and VERSES from the input. Use the mapping below for full book names.

## Step 1: Claim the Passage

Open `TODO.md` and change `[ ]` to `[🔄]` for the matching entry.

## Step 2: Run All 6 Skills IN PARALLEL

Invoke all six analysis skills in a SINGLE message with the passage:

```
/historian {passage}
/linguist {passage}
/author {passage}
/theologian {passage}
/disciple {passage}
/shepherd {passage}
```

CRITICAL: These MUST be 6 parallel Skill tool calls in ONE response. Do NOT run them sequentially.

## Step 3: Compile the Document

Assemble the outputs into a single markdown document following the format in CLAUDE.md:

1. Title: `# Exegetical Analysis of {Full Book Name} {Chapter}:{Verses} - {Description}`
   - Get the description from the TODO.md entry or infer from the passage content
2. Scripture block: Look up the ESV text and format as:
   ```
   > **1** Verse text...
   >
   > **2** More verse text...
   >
   > — *English Standard Version (ESV)*
   ```
3. Horizontal rule: `---`
4. Six sections in order, each separated by `---`:
   - `## Historical & Cultural Analysis` (from /historian)
   - `## Linguistic Analysis` (from /linguist)
   - `## Literary Analysis` (from /author)
   - `## Theological Analysis` (from /theologian)
   - `## Hermeneutic` (from /disciple)
   - `## Application` (from /shepherd)

## Step 4: Write the Output

1. Create directory `content/<BOOK_CODE>/<CHAPTER>/` if it does not exist
   - CHAPTER is zero-padded: 01, 02, etc.
2. Write to `content/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`
   - Example: HAG 02:20-23 → `content/HAG/02/HAG_02_20-23.md`

## Step 5: Mark Complete

Change `[🔄]` to `[✅]` in `TODO.md` for the passage.

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
| HOS | Hosea | JOE | Joel | AMO | Amos |
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
| 3JN | 3 John | JDE | Jude | REV | Revelation |
