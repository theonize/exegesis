---
name: critic
description: Audit the reasoning of a compiled exegetical analysis — cross-section coherence, evidentiary proportion, exegetical fallacies, unstated counter-readings, and application groundedness. Use when a draft study needs its arguments tested before publication, or when checking whether conclusions are proportional to the evidence offered.
---

# Critic Skill — Argument & Reasoning Audit

Given a compiled exegetical analysis (a file path, or a passage reference to resolve via the standard `content/Books/...` path rules), audit the **quality of its reasoning**, correct what can be corrected surgically, and flag what cannot.

This skill enforces the project's core posture: *distinguish observation, inference, tradition, and application; keep conclusions proportional to the evidence*. It performs no fresh exegesis and writes no new argument — it tests what the analysis already claims.

## Division of Labor

The critic is the counterpart of the `bibliographer`, not a duplicate of it:

| | bibliographer | critic |
|---|---|---|
| Asks | "Is this citation true?" | "Does this conclusion follow?" |
| Checks | Strong's numbers, forms, dates, quotations, cross-reference existence | inference chains, confidence calibration, coherence, fallacies |
| Method | verify against an external source | reason against the document itself |
| Output | corrected facts + `## Sources` | corrected reasoning + critique report |

A claim can pass the bibliographer completely — every number right, every citation real — and still fail the critic, because a true fact was made to carry a conclusion it cannot bear. That is the gap this skill covers.

Run the critic **before** the bibliographer so the bibliographer gets the last word on the document and its `## Sources` reflects the final text.

## Audit Checklist

Read the whole document first. The critic is the only pass that sees all six sections at once — cross-section work is its distinctive contribution and comes first.

1. **Cross-section coherence** — six seats wrote in isolation. Do any two sections contradict each other on the meaning of a key term, the identity of a referent, the date or setting, or the passage's main point? Do later sections silently depend on a reading an earlier section rejected?
2. **Evidentiary proportion** — is the confidence language matched to the support offered? Flag *clearly*, *obviously*, *certainly*, *must mean*, *proves*, *undoubtedly*, *the only possible reading* wherever the document has given one line of evidence or none.
3. **Exegetical fallacies** — the standard failure modes of word study and inference:
   - **Root fallacy** — meaning derived from a word's components or root rather than its usage.
   - **Etymological fallacy** — an older or original sense imposed on the author's usage.
   - **Illegitimate totality transfer** — the whole semantic range imported into a single occurrence.
   - **Semantic anachronism** — a later sense (often the New Testament's, or a modern one) read back into an earlier text.
   - **Selective range** — one gloss chosen from a lexicon with no argument for why the others do not fit.
   - **Numerology and false parallel** — occurrence counts, gematria, or "the same word appears in X" carrying weight without a demonstrated link.
4. **Inference validity** — does each conclusion follow from its stated premises? Flag non sequiturs, assumed conclusions, arguments from silence presented as positive evidence, and appeals to parallels that are not actually parallel.
5. **Category discipline** — observation, inference, tradition, and application must remain distinguishable. Flag inference stated as observation ("the text says" when the text implies), tradition stated as text (a received reading presented as what the passage states), and application smuggled into exegesis.
6. **Unstated counter-readings** — where the passage has a genuine interpretive crux, a settled-sounding presentation is a defect. The document should name the main alternative in at least one clause and say why the chosen reading is preferred. Reserve this for real cruxes; do not manufacture controversy over a consensus reading.
7. **Application groundedness** — does each application in `## Application` trace to something the exegesis actually established? Flag moralizing, allegorizing, and generic advice that would follow equally from any passage.
8. **Anachronism and eisegesis** — modern categories, institutions, or debates imposed on the ancient text without a bridge.
9. **Tone and audience** — confessional/evangelical without narrowing to one tradition, scholar addressing a serious non-specialist. Flag polemic against other traditions, and jargon left unexplained.

Some overlap between sections is by design — six disciplines on one passage will touch the same evidence. Only flag repetition that is near-verbatim or that adds no new angle.

## Action Rules

- **Fix in place** (surgical, minimal): downgrade overreaching confidence language; insert a one-clause counter-reading or hedge; cut a fallacious inference step while leaving the surrounding prose intact; correct a cross-section contradiction by keeping the better-evidenced position and noting the alternative in one clause.
- **Flag only, do not rewrite**: anything requiring fresh research, a new argument, or a substantive re-draft. Report it for a human or for a targeted re-run of the owning seat.
- **Preserve the voice.** Each section was written by a different discipline and reads differently on purpose. Do not paraphrase sound prose, harmonize style, or "tighten" writing that is merely not yours.
- **Never**: re-draft a section wholesale; add, remove, renumber, or reorder `## ` or `### ` sections; alter headings; touch the scripture blockquote or its attribution line; delete a whole subsection (that breaks the seat's contract — hollow it to its defensible core instead); introduce a citation, statistic, date, or original-language form the document did not already contain.
- **A clean run is a valid result.** Do not manufacture findings to look thorough. Report zero where zero is true. A weak flag raised to pad a report costs more than it saves.
- Log every change you make, with the section it lands in.

## Output

1. **The corrected document** — edit the file in place, within the constraints above.
2. **Critique report** (returned, not written into the document):
   - Counts: claims audited, edits made in place, issues flagged without edit.
   - **Fixed** — each in-place edit, one line: section, what was wrong, what it now says.
   - **Flagged** — each unedited issue, one line: section, checklist item, why it needs a human or a seat re-run. Ordered most-serious first.
   - **Cross-section notes** — coherence findings, called out separately since no single seat owns them.

## Formatting

Anything the critic writes into the document follows the Formatting section of `CLAUDE.md`:

- Original-language terms: `**term** (Hebrew/Greek/Aramaic: script, *transliteration*)`
- Strong's numbers: `H1234` / `G5678`
- Biblical citations: `Book Chapter:Verses`
- Never emit `---` inside a `## ` section
