# Analysis Process

> Derived from `.claude/skills/*/SKILL.md` — do not edit here. Change the skill files, then regenerate this summary.

## Orchestration

The `/research <BOOK_CODE> <CHAPTER>:<VERSES>` skill runs the pipeline:

1. **Parse & claim** — normalize the reference, resolve the target path, set the `TODO.md` entry to `[🔄]` (with pre-flight checks for stale, done, or missing entries).
2. **Fetch the text** — always from a source in `RESOURCES.md` (or the underrow MCP service), never from memory. The translation is chosen per passage — multiple allowed, prefer license-permissive translations for full quotes — and named in the attribution line.
3. **Analyze in parallel** — six subagents, one per analysis skill below; each reads its own SKILL.md and writes its `##` section. A subagent that fails or returns empty/garbage output is retried once; a second failure fails the run (`[❌]`).
4. **Compile** — mechanical concatenation: title, scripture blockquote, then the six sections separated by `---`. Never regenerated.
5. **Verify** — the bibliographer skill checks references and facts, corrects or hedges, and appends `## Sources`.
6. **Write & complete** — overwrite guard, completion gates (blockquote + six section headings + Sources present), then `[✅]`.

---

## Analysis Skills

Each skill produces one top-level `##` section with numbered `###` subsections.

### Historian → `## Historical & Cultural Analysis`

Questions: author; original audience; date of composition and of the events; notable practices of the day; archaeology and external histories; political-socio-economic milieu and social structures; circumstantial social norms and issues; geography; worldview and cosmology; family structure; iconography; intercultural issues.

Subsections:
1. Author
2. Original Audience
3. Date of Composition and Events — timeline table `| Event | Date | Significance |`
4. Notable Practices of the Day
5. Archaeology and External History
6. Political-Socio-Economic Context
7. Social Norms and Issues
8. Geography

### Linguist → `## Linguistic Analysis`

Questions: original language; lexical semantics and range; morphological and grammatical features; lexical-syntactical and discourse features; etymology of key terms; notable translation decisions; textual variants and whether they change the teaching.

Subsections:
1. Original Language
2. Lexical Semantics — vocabulary table `| Term | Strong's | Root | Meaning | Occurrences | Key Usage |`
3. Morphological and Grammatical Features
4. Discourse Structure
5. Etymology of Key Terms
6. Translation Decisions — comparison table `| Version | Rendering | Notes |`
7. Textual Variants — state explicitly whether any variant changes the teaching

### Author → `## Literary Analysis`

Questions: genre and sub-genres, with the rules of interpretation they call for; literary structure of the immediate and surrounding text; voice, mood, and style; rhetorical devices; literary devices; characters and images and their purpose; numerology; significant colors and items; overt symbols; word counts and repeated ideas; numerical word values; micro-patterns.

Scope: patterning **within the passage and its book**. Canon-scale patterns belong to the disciple skill.

Subsections:
1. Genre and Sub-Genres
2. Literary Structure — ASCII chiasm/parallel diagrams (A/B/C/B'/A')
3. Voice, Mood, and Style
4. Rhetorical Devices
5. Literary Devices
6. Characters and Images
7. Numerology and Symbolic Elements
8. Colors, Items, and Significance — catalog table `| Symbol | Meaning | Biblical Precedent |`

### Theologian → `## Theological Analysis`

Questions: who God — Father, Christ, Spirit — is in this passage (attributes, actions, promises); what the original audience would have drawn from it; spiritual disciplines in play; timeless principles and how the passage progresses revelation.

Subsections:
1. What the Original Audience Would Have Understood
2. Spiritual Disciplines in View
3. Timeless Theological Principles
4. Key Theological Themes — begins with who God is in the passage; cross-reference tables `| Theme | OT Foundation | NT Development |`

### Disciple → `## Hermeneutic`

Questions: how the passage fits over-arching canonical threads and themes; wordplay and idioms; micro and macro structures; image-bearer and wisdom elements; plenary authorship intent and why the passage sits where it does.

Scope: canon-scale patterning (type-scenes, covenant echoes, Genesis-to-Revelation threads). Intra-book patterning belongs to the author skill.

Subsections:
1. Canonical Threads and Themes — thread table `| Stage | Passage | Development |`
2. Wordplay and Idioms
3. Micro and Macro Structures
4. Image-Bearer and Wisdom Elements
5. Plenary Authorship Intent

### Shepherd → `## Application`

Questions: the original meaning clarified for a modern audience and its universal principles; what attributes or actions must change; when, where, and how to implement; meaning versus method.

Produces exactly subsections 1–4 — no extra headings, no `---` inside the section.

Subsections:
1. Clarifying the Original Meaning for a Modern Audience — table `| Ancient Reality | Modern Equivalent |`
2. What Must Change
3. When, Where, and How to Implement — table `| Context | When | Where | How |`
4. Meaning Versus Method

### Bibliographer → `## Sources` (verification pass)

Runs after compilation, over the whole draft. Checks: Strong's numbers against lemma and gloss; script/transliteration/term agreement; cross-references exist and support their claims; quotations and named authorities verified, hedged, or removed; date consistency; scripture quotes match the named translation. Fixes mechanical errors in place, hedges or deletes unverifiable specifics, then appends `## Sources` — a per-discipline bibliography of works actually consulted.

---

## Shared Formatting

- Original-language terms: `**term** (Hebrew/Greek/Aramaic: original script, *transliteration*)`
- Strong's numbers: `H1234` / `G5678`
- Biblical citations: `Book Chapter:Verses`; in-passage references: `(v.1)`, `(vv.1-5)`
- `---` between `##` sections only — never inside a section
- Tone: scholarly content for an amateur audience
