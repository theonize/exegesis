Succinct Schema Doc — Hierarchical Texts & Notes

(drop-in reference for agents writing ETL / data-wrangling code)


---

1. Reference ID (id, ref)

volume.translation.book.chapter.verse

Dot-delimited, five segments, lower-case.

volume – corpus/author (e.g. plato)

translation – language/version code (eng, grc, heb, …)

book – work or sub-work (republic)

chapter – integer ≥ 1

verse – integer ≥ 1


May contain * in queries only (wildcard/glob).

Treat as an opaque string in storage; parse segments only when needed.



---

2. Top-Level JSON Shape

{
  "texts": [TextEntry, …],
  "notes": [NoteEntry, …]
}


---

3. TextEntry

{
  "id": "plato.eng.republic.3.4.3",   // required, unique
  "content": "string",                // required – full text of verse/passage
  "meta": {                           // optional, open-ended
    "source": "Loeb", 
    "date_added": "2025-06-26",
    "...": "..."
  }
}


---

4. NoteEntry

{
  "id": "N1",                         // required, unique across notes
  "ref": "plato.eng.republic.3.4.3",  // required – links to TextEntry.id
  "type": "historical | cultural | literary | application",  // required
  "content": "string",                // required – note text
  "meta": {                           // optional, open-ended
    "author": "Jane Scholar",
    "date_added": "2025-06-26",
    "...": "..."
  }
}


---

5. Minimal JSON-Schema Snippet (Draft-07)

{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "texts": {
      "type": "array",
      "items": { "$ref": "#/definitions/TextEntry" }
    },
    "notes": {
      "type": "array",
      "items": { "$ref": "#/definitions/NoteEntry" }
    }
  },
  "definitions": {
    "idPattern": {
      "type": "string",
      "pattern": "^[^.]+\\.[^.]+\\.[^.]+\\.[0-9]+\\.[0-9]+$"
    },
    "TextEntry": {
      "type": "object",
      "required": ["id", "content"],
      "properties": {
        "id": { "$ref": "#/definitions/idPattern" },
        "content": { "type": "string" },
        "meta": { "type": "object" }
      },
      "additionalProperties": false
    },
    "NoteEntry": {
      "type": "object",
      "required": ["id", "ref", "type", "content"],
      "properties": {
        "id": { "type": "string" },
        "ref": { "$ref": "#/definitions/idPattern" },
        "type": {
          "type": "string",
          "enum": ["historical", "cultural", "literary", "application"]
        },
        "content": { "type": "string" },
        "meta": { "type": "object" }
      },
      "additionalProperties": false
    }
  }
}


---

6. Query Conventions (for agent writers)

Use prefix or glob search on id / ref for range selection.

Example: plato.eng.republic.3.*.3 ⇒ every verse 3 of any chapter in Book 3.


Join notes to texts on ref == id after filtering.


That’s the whole spec—lean, hierarchical, and ready for piping through your data-wrangling pipeline.
