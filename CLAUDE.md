# Exegetical Analysis Project

This project produces comprehensive exegetical analyses of Biblical passages and documents the methodology. AI serves as a research assistant — treat output like a calculator: always verify claims, cross-reference sources, and probe answers critically.

## Workflow

To analyze a passage, use the `/research` skill:

```
/research <BOOK_CODE> <CHAPTER>:<VERSES>
```

Example: `/research HAG 02:20-23`

This orchestrates all six analysis skills in parallel, compiles the output, and writes the file.

## File Organization

- Content: `content/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`
- Example: `HAG 02:20-23` → `content/HAG/02/HAG_02_20-23.md`

**Book codes** (3-letter uppercase):
GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOE AMO OBA JON MIC NAH HAB ZEP HAG ZEC MAL MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JDE REV

**Chapters**: zero-padded two digits (01, 02, ...)
**Verses**: hyphenated ranges (1-25, 26-31)

**Progress tracking** in `TODO.md`:
- `[ ]` pending
- `[🔄]` in-progress
- `[✅]` complete

## Output Format Specification

### Document Structure

```
# Exegetical Analysis of {Full Book Name} {Chapter}:{Verses} - {Description}

> **1** First verse text...
>
> **2** Second verse text...
>
> — *English Standard Version (ESV)*

---

## Historical & Cultural Analysis
### [subsections per historian skill]

---

## Linguistic Analysis
### [subsections per linguist skill]

---

## Literary Analysis
### [subsections per author skill]

---

## Theological Analysis
### [subsections per theologian skill]

---

## Hermeneutic
### [subsections per disciple skill]

---

## Application
### [subsections per shepherd skill]
```

## Formatting Conventions

- **Hebrew/Greek/Aramaic terms**: `**term** (Hebrew: script, *transliteration*)`
  Example: **chotam** (Hebrew: חוֹתָם, *ḥôṯām*)
- **Biblical citations**: Book Chapter:Verses (e.g., Genesis 41:42)
- **Verse references within passage**: (v.1), (vv.1-5)
- **Strong's numbers**: H1234 or G5678 where relevant
- **Section separators**: `---` between each `## ` section
- **Subsections**: `### ` headings within each `## ` section
- **Tables**: markdown tables for comparisons, timelines, vocabulary, semantic ranges
- **Structural diagrams**: ASCII art for chiastic patterns, literary structures
- **Tone**: scholar addressing an amateur audience; confessional/evangelical, no particular tradition

## Exemplar

See `content/HAG/01/HAG_01_1-11.md` for a well-formed reference example.

## Resources

Study tools and references are listed in `RESOURCES.md`.
Permitted web domains: enduringword.com, www.thegospelcoalition.org
