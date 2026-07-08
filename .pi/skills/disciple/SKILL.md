---
name: disciple
description: Apply hermeneutical methods to Bible passages. Use when tracing canonical themes, identifying wordplay and idioms, analyzing micro/macro structures, exploring image-bearer and wisdom elements, or discerning plenary authorial intent.
---

# Disciple Skill

> **Pi port:** This project-local Pi skill is based on `.claude/skills/disciple/SKILL.md`, but runs from `.pi/skills/disciple/SKILL.md`. When using it in Pi, read this `.pi` file and do not edit or depend on the `.claude` skill.

Research and determine the context of a Biblical passage by answering the following questions:
* How does this passage fit within over-arching canonical threads and themes?
* What wordplay and/or idioms or in use?
* What are some notable micro and macro-structures in the passage?
* What are the human image-bearer elements of the passage?  wisdom elements?
* What is the plenary authorship intent in composing this text? Why is this passage where it is?

Scope boundary: this skill owns canon-scale patterning (type-scenes, covenant echoes, Genesis-to-Revelation threads). Patterning within the passage and its book belongs to the author skill.

## Output Format

Produce content under the heading `## Hermeneutic`.

Organize answers as `### ` subsections:

### 1. Canonical Threads and Themes
How this passage fits within progressive revelation. Use thread tables:
| Stage | Passage | Development |
Show connections from Genesis through Revelation where applicable.

### 2. Wordplay and Idioms
Hebrew/Greek puns, double meanings, idiomatic expressions.

### 3. Micro and Macro Structures
Patterns within the passage (micro) and across the book/canon (macro).

### 4. Image-Bearer and Wisdom Elements
What the passage reveals about humanity as image-bearers; wisdom themes.

### 5. Plenary Authorship Intent
Distinguish the human author's intent from the Spirit's broader canonical purpose. Address why this passage sits where it does in the book and the canon.

### Formatting
- Canonical thread tables: `| Stage | Passage | Development |`
- Hebrew/Greek terms: **term** (Hebrew: script, *transliteration*)
- Cross-reference chains showing thematic development
- Distinguish human author intent from Spirit's canonical purpose