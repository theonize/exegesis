---
name: linguist
description: Analyze Hebrew, Greek, and Aramaic linguistic features in Bible passages. Use when doing word studies, exploring etymology, examining grammar and syntax, comparing translations, or investigating textual variants and manuscript evidence.
---

# Linguist Skill

> **Pi port:** This project-local Pi skill is based on `.claude/skills/linguist/SKILL.md`, but runs from `.pi/skills/linguist/SKILL.md`. When using it in Pi, read this `.pi` file and do not edit or depend on the `.claude` skill.

Research and determine the context of a Biblical passage by answering the following questions:
* What was the original language of this writing?
* What are the lexical semantics and range of the passage?
* What are some notable morphological and grammatical features of the passage?
* What are the lexical-syntactical and discourse features of the passage?
* What is the etymology of key terms?
* What are some notable translation decisions associated with this passage?
* What notable textual variants are there? Do they change the teaching?

## Output Format

Produce content under the heading `## Linguistic Analysis`.

Organize answers as `### ` subsections:

### 1. Original Language
Language classification, period, distinctive features of this text's language.

### 2. Lexical Semantics
Key terms with Strong's numbers, roots, semantic ranges, and intertextual connections. Use vocabulary tables:
| Term | Strong's | Root | Meaning | Occurrences | Key Usage |

### 3. Morphological and Grammatical Features
Verb forms, construct chains, notable syntax, parsing of significant words.

### 4. Discourse Structure
Progression markers, rhetorical flow, discourse-level features.

### 5. Etymology of Key Terms
Word origins, development across biblical usage, cognates.

### 6. Translation Decisions
Compare major versions. Use a translation comparison table:
| Version | Rendering | Notes |

### 7. Textual Variants
Manuscript evidence, critical apparatus notes, impact on interpretation — state explicitly whether any variant changes the teaching.

### Formatting
- Hebrew/Greek: **term** (Hebrew: script, *transliteration*)
- Strong's numbers: H1234 / G5678
- Vocabulary tables for key terms with semantic ranges
- Morphological notation where relevant
- Translation comparison tables across major versions (e.g. ESV, NASB, NIV, KJV, WEB — pick what best illustrates the decision)