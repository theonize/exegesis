---
name: author
description: Analyze literary features of Bible passages. Use when examining genre, literary structure, chiasm, voice, mood, style, rhetorical devices, imagery, characterization, or narrative techniques in Scripture.
---

# Author Skill

> **Pi port:** This project-local Pi skill is based on `.claude/skills/author/SKILL.md`, but runs from `.pi/skills/author/SKILL.md`. When using it in Pi, read this `.pi` file and do not edit or depend on the `.claude` skill.

Research and determine the context of a Biblical passage by answering the following questions:
* What is the genre (and sub-genres) of the passage? What rules of interpretation do those genres call for?
* What is the literary structure of the immediate and surrounding?
* What is the voice, mood and style of the passage?
* What rhetorical devices are used in the text?
* What literary devices are used in the text?
* What are the characters and images in use?  and their purpose in the passage?
* What numerology is in play here?
* What colors, items, et cetera have significance?
* What overt symbols are present and what is their significance?
* What word counts are of interest — words or ideas repeated a specific number of times?
* What numerical word values are important in the original language?
* What micro-patterns are established in the text?

Scope boundary: this skill owns literary patterning **within the passage and its book** (structure, repetition counts, chiasm). Canon-scale patterns (type-scenes, covenant echoes, Genesis-to-Revelation threads) belong to the disciple skill — note a handoff rather than developing them here.

## Output Format

Produce content under the heading `## Literary Analysis`.

Organize answers as `### ` subsections:

### 1. Genre and Sub-Genres
Primary genre classification, any sub-genre elements, and the rules of interpretation those genres call for.

### 2. Literary Structure
Immediate and surrounding structure. Use ASCII diagrams for chiastic and parallel structures:
```
A  - element
  B  - element
    C  - pivot
  B' - element
A' - element
```

### 3. Voice, Mood, and Style
Narrative voice, emotional tone, stylistic characteristics.

### 4. Rhetorical Devices
Identified devices with examples from the text.

### 5. Literary Devices
Identified devices with examples from the text.

### 6. Characters and Images
Who/what appears, their role and purpose in the passage.

### 7. Numerology and Symbolic Elements
Number significance, word counts, repeated patterns, numerical word values, and micro-patterns within the passage and book (canon-scale patterns are the disciple skill's territory).

### 8. Colors, Items, and Significance
Symbolic objects, colors, and their biblical precedent. Use catalog tables:
| Symbol | Meaning | Biblical Precedent |

### Formatting
- ASCII structural diagrams with indentation
- Chiastic notation: A/B/C/B'/A'
- Symbol catalog tables
- Hebrew/Greek terms: **term** (Hebrew: script, *transliteration*)
- Cross-references for pattern identification