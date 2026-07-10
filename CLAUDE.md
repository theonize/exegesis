# Exegetical Analysis Project

This project produces exegetical studies of biblical passages and related topics. Claude is a research assistant, not an authority: verify claims, cross-check sources, and preserve only what survives scrutiny.

## Workflow

To analyze a passage, use the `/research` skill:

```text
/research <BOOK_CODE> <CHAPTER>:<VERSES>
```

Example: `/research HAG 02:20-23`

The skill fetches the passage text, fans out the six analysis skills as parallel subagents, compiles the output, runs the `bibliographer` skill as a verification pass, writes the file, and updates `TODO.md`.

To re-examine an **existing** study — after a model upgrade, a new discovery, or updated scholarship — use the `/revisit` skill:

```text
/revisit <passage|chapter|topic|path> [-- context]
```

Example: `/revisit HAG 02:20-23 -- updated Persian-period chronology`

The skill re-runs the six analysis seats in review mode over the existing file (preserve what survives scrutiny, correct and deepen the rest), re-verifies with the `bibliographer`, and replaces the file in place. It never creates new studies and never touches `TODO.md`.

Scripture text is always **fetched from a source** (see `RESOURCES.md`), never reproduced from memory. The translation is not fixed: choose the translation(s) best suited to the passage — prefer license-permissive translations for full-passage quotation — and name whatever is used in the attribution line.

## Research Posture

Begin with authorial intent in historical, cultural, linguistic, literary, and canonical context. Distinguish observation, inference, tradition, and application. Keep conclusions proportional to the evidence. Write for serious non-specialists in a clear confessional/evangelical voice without narrowing to one tradition.

## File Organization

- Passage studies: `content/Books/<TESTAMENT>/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`
- `TESTAMENT`: `OT` or `NT`.
- `BOOK_CODE`: uppercase code from `TODO.md`; use `JOL` for Joel and `JUD` for Jude.
- `CHAPTER`: zero-padded to match the existing tree (`01`, `02`, etc.; Psalms use `001` through `150`).
- `VERSES`: hyphenated range; preserve cross-chapter notation when present, e.g. `MRK_08_31-9_1.md`.
- Examples: `HAG 02:20-23` -> `content/Books/OT/HAG/02/HAG_02_20-23.md`; `COL 03:12-17` -> `content/Books/NT/COL/03/COL_03_12-17.md`.
- Topic studies: `content/Topics/<Topic>.md`; grouped topics may use subfolders, e.g. `content/Topics/Chroma/Gold.md`.
- Character studies: `content/Characters/<Name>.md`.

Use `TODO.md` for the active queue and passage descriptions. Preserve its existing status markers exactly.

## Book Codes

Use `TODO.md` as the source of truth.

OT: GEN EXO LEV NUM DEU JOS JDG RUT 1SA 2SA 1KI 2KI 1CH 2CH EZR NEH EST JOB PSA PRO ECC SNG ISA JER LAM EZK DAN HOS JOL AMO OBA JON MIC NAH HAB ZEP HAG ZEC MAL

NT: MAT MRK LUK JHN ACT ROM 1CO 2CO GAL EPH PHP COL 1TH 2TH 1TI 2TI TIT PHM HEB JAS 1PE 2PE 1JN 2JN 3JN JUD REV

## Output Format

```markdown
# Exegetical Analysis of {Full Book Name} {Chapter}:{Verses} - {Description}

> **1** First verse text...
>
> **2** Second verse text...
>
> — *Translation Name (ABBR)*

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

---

## Sources
[per-discipline bibliography, compiled by the bibliographer skill]
```

## Formatting

- Original-language terms: `**term** (Hebrew/Greek/Aramaic: original script, *transliteration*)`
- Biblical citations: `Book Chapter:Verses`, e.g. `Genesis 41:42`
- Verse references inside the target passage: `(v.1)`, `(vv.1-5)`
- Strong's numbers: `H1234` or `G5678` where useful
- Top-level sections: `##`; subsections: `###`
- Separators: `---` between each `##` section only — never inside a section
- Tables: comparisons, timelines, vocabulary, semantic ranges
- Diagrams: ASCII for chiastic patterns and literary structures
- Tone: scholar addressing an amateur audience; confessional/evangelical, no particular tradition

## Exemplar

See `content/Books/OT/PRO/11/PRO_11_1-15.md` for a well-formed passage study (full subsection contracts, Strong's numbers, ASCII diagrams, all table types) — except its Application section, which retains legacy extra headings (Summary/Conclusion) and intra-section `---`; the shepherd skill's contract (exactly subsections 1–4) wins there. Older files such as `content/Books/OT/HAG/01/HAG_01_1-11.md` retain a legacy shape throughout; do not imitate their extra unnumbered subsections or intra-section `---` rules.

## Resources

Study tools and references are listed in `RESOURCES.md`.
When `underrow` is running there will be an MCP service with semantic search tools available @ localhost:3740
