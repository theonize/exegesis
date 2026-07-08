---
name: shepherd
description: Develop practical, real-life applications from Bible passages. Use when creating modern applications for contemporary audiences, exploring how to implement biblical principles, or bridging ancient meaning to current life situations.
---

# Shepherd Skill

> **Pi port:** This project-local Pi skill is based on `.claude/skills/shepherd/SKILL.md`, but runs from `.pi/skills/shepherd/SKILL.md`. When using it in Pi, read this `.pi` file and do not edit or depend on the `.claude` skill.

Research and determine the context of a Biblical passage by answering the following questions:
* Clarify the original meaning for a modern audience — what are the universal principles?
* What attributes or actions, of the modern audience, must change according to this Word?
* When, where and how might we implement these changes?
* Meaning versus method: how might I accomplish these things?

## Output Format

Produce content under the heading `## Application`.

Organize answers as `### ` subsections:

### 1. Clarifying the Original Meaning for a Modern Audience
Bridge the ancient context to contemporary life; name the universal principles. Use comparison tables:
| Ancient Reality | Modern Equivalent |

### 2. What Must Change
Attributes, attitudes, and actions the passage calls the modern audience to alter. Include diagnostic questions for self-examination.

### 3. When, Where, and How to Implement
Context-specific guidance. Use implementation tables:
| Context | When | Where | How |

### 4. Meaning Versus Method
The fixed theological principle versus flexible application methods. Distinguish what is timeless from what is culturally situated.

### Formatting
- Produce exactly subsections 1–4 — no extra unnumbered headings, no Summary, no Conclusion
- Never emit `---` inside the section; `---` is reserved for boundaries between the document's `##` sections
- Comparison tables: `| Ancient Reality | Modern Equivalent |`
- Implementation tables: `| Context | When | Where | How |`
- Self-examination questions
- Practical, specific, actionable content
- Bridge ancient meaning to contemporary life

