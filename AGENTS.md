# Exegesis Project Instructions

This repository contains exegetical studies of biblical passages, books, topics, and characters. Use generated material as a research draft, never as finished authority.

## Research Posture

Begin with authorial intent in historical, cultural, linguistic, literary, and canonical context. Verify claims against Scripture, original-language evidence, historical sources, and credible scholarship. Distinguish observation, inference, tradition, and application; keep confidence proportional to the evidence. Write for serious non-specialists in a clear confessional/evangelical voice without narrowing to one tradition.

## Paths

- Passage studies: `content/Books/<TESTAMENT>/<BOOK_CODE>/<CHAPTER>/<BOOK_CODE>_<CHAPTER>_<VERSES>.md`
- `TESTAMENT`: `OT` or `NT`.
- `BOOK_CODE`: uppercase code from `TODO.md`; use `JOL` for Joel and `JUD` for Jude.
- `CHAPTER`: zero-padded to match the existing tree (`01`, `02`, etc.; Psalms use `001` through `150`).
- `VERSES`: hyphenated range; preserve cross-chapter notation when present, e.g. `MRK_08_31-9_1.md`.
- Examples: `content/Books/OT/HAG/02/HAG_02_20-23.md`, `content/Books/NT/COL/03/COL_03_12-17.md`.
- Topics: `content/Topics/<Topic>.md`; grouped topics may use subfolders, e.g. `content/Topics/Chroma/Gold.md`.
- Characters: `content/Characters/<Name>.md`.
- Progress lives in `TODO.md`; research resources live in `RESOURCES.md`.

## Passage Output

Use this section order:

1. Historical & Cultural Analysis
2. Linguistic Analysis
3. Literary Analysis
4. Theological Analysis
5. Hermeneutic
6. Application

Separate top-level sections with `---`. Prefer tables for comparisons, timelines, vocabulary, and semantic ranges. Use ASCII diagrams for structures. Cite biblical references as `Book Chapter:Verses`; cite verses inside the target passage as `(v.1)` or `(vv.1-5)`.

## Structured Data

For ETL and local-storage code, keep this compact schema:

```json
{
  "texts": [
    {
      "id": "volume.translation.book.chapter.verse",
      "content": "string",
      "meta": {}
    }
  ],
  "notes": [
    {
      "id": "N1",
      "ref": "volume.translation.book.chapter.verse",
      "type": "historical | cultural | literary | application",
      "content": "string",
      "meta": {}
    }
  ]
}
```

Reference IDs are lower-case, dot-delimited, five-segment strings: `volume.translation.book.chapter.verse`. Treat them as opaque in storage; parse only at import, export, or query boundaries. `*` is allowed in query patterns only. Join notes to texts on `ref == id`.
