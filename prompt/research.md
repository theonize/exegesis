For the selected passage perform the following steps:

**Step 0: Claim the passage (FIRST)**

Mark the passage as in-progress in `/TODO.md`:
- Change `[ ] GEN 01:26-31` to `[🔄] GEN 01:26-31`

This prevents other agents from duplicating work.

**Step 1: Run all 6 skills IN PARALLEL**

Invoke all skills in a SINGLE message (do NOT wait between them):

```
/historian {passage}
/linguist {passage}
/author {passage}
/theologian {passage}
/disciple {passage}
/shepherd {passage}
```

CRITICAL: These must be 6 parallel Skill tool calls in ONE message, not sequential calls.

**Step 2: Compile outputs**

Once ALL skills complete, organize into a single markdown document with sections:
1. `## Historical & Cultural Analysis` (from /historian)
2. `## Linguistic Analysis` (from /linguist)
3. `## Literary Analysis` (from /author)
4. `## Theological Analysis` (from /theologian)
5. `## Hermeneutic` (from /disciple)
6. `## Application` (from /shepherd)

Add a title: `# Exegetical Analysis of {Book} {Chapter}:{Verses} - {Description}`

**Step 3: Create output directory**

Create `/content/<BOOK>/<CHAPTER>/` if it doesn't exist.

**Step 4: Write the file**

Write compiled markdown to: `/content/<BOOK>/<CHAPTER>/<BOOK>_<CHAPTER>_<VERSES>.md`

Example: `GEN 01:26-31` → `/content/GEN/01/GEN_01_26-31.md`

**Step 5: Mark complete**

Change 🔄 to ✅ for the passage in `/TODO.md`
