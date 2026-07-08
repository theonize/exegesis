---
name: bibliographer
description: Verify references and facts in an exegetical analysis and compile its Sources section. Use when checking Strong's numbers, original-language forms, cross-references, quotations, dates, or scholarly claims against primary sources, or when a compiled study needs a bibliography.
---

# Bibliographer Skill — Reference & Fact Checking

> **Pi port:** This project-local Pi skill is based on `.claude/skills/bibliographer/SKILL.md`, but runs from `.pi/skills/bibliographer/SKILL.md`. When using it in Pi, read this `.pi` file and do not edit or depend on the `.claude` skill.

Given a compiled exegetical analysis (a file path, or a passage reference to resolve via the standard `content/Books/...` path rules), verify its checkable claims against primary sources, correct or hedge what fails, and compile its `## Sources` section.

This skill enforces the project's core posture: *verify claims, cross-check sources, and preserve only what survives scrutiny*. It performs no fresh exegesis — it audits what the analysis already says.

## Verification Checklist

Work through the document section by section. In Pi, verify from actual sources using whatever source-access tools are available in the session: first read `RESOURCES.md`, then use `bash` with `curl`/Python/PowerShell, browser or search extensions if loaded, local source files/databases, or an `underrow`/MCP service if one is available. Do **not** treat model memory as verification. If a claim cannot be checked against a source, hedge it, remove it, or flag it for human review according to the action rules below.

1. **Strong's numbers** — every `H####`/`G####` maps to the lemma actually named beside it, and the gloss given falls within the lexicon's semantic range.
2. **Original-language forms** — the script, the transliteration, and the English term in each `**term** (Hebrew/Greek/Aramaic: script, *transliteration*)` triple all agree.
3. **Cross-references** — every cited `Book Chapter:Verse` exists and says what the analysis claims it says. Flag citations that exist but do not support the point.
4. **Quotations and named authorities** — quoted scholars, ancient sources (Josephus, Talmud, ANE texts), and archaeological claims are verified against a source, or downgraded ("some scholars suggest"), or removed.
5. **Dates and numbers** — dates are internally consistent with the document's own timeline tables and with standard chronology; word counts and occurrence counts claimed in the text are spot-checked.
6. **Scripture quotations** — phrases quoted from the passage match the translation named in the attribution line.

## Action Rules

- **Mechanical errors** (a wrong Strong's digit, a transliteration typo, a miscited chapter): fix in place.
- **Unverifiable specifics**: hedge or delete. A specific claim (a name, a date, a quotation, a statistic) that cannot be verified must not remain stated as fact.
- **Conflicts between sections** (e.g., two sections give different composition dates): keep the better-evidenced position and note the alternative in one clause; never let the document silently disagree with itself.
- Log every change you make.

## Output

1. **The corrected document** — edit the file in place. Preserve its structure exactly: do not add, remove, renumber, or reorder sections; do not touch prose that passed verification.
2. **`## Sources`** — append as the final section (after `## Application`, preceded by `---`): a per-discipline list (`### Historical & Cultural` / `### Linguistic` / `### Literary` / `### Theological` / `### Hermeneutical` / `### Application` — one bucket per document section, omit a bucket only if truly empty) of the works and sites actually consulted during verification or genuinely relied on by the analysis. Never pad with unconsulted works; an invented citation is worse than none.
3. **Verification report** (returned, not written into the document): counts of claims checked, corrected, hedged, and removed, plus any unresolved flags a human should review.

## Formatting

- Original-language terms: `**term** (Hebrew/Greek/Aramaic: script, *transliteration*)`
- Strong's numbers: `H1234` / `G5678`
- Biblical citations: `Book Chapter:Verses`
- `## Sources` entries: author/site, work, and (for web sources) the specific page consulted
