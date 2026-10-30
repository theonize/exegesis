# Durable Bible-study podcasts

`scripts/bible_podcast.py` is a standalone Python 3.10+ stdlib CLI for Linux/macOS. It uses the installed `notebooklm` CLI (command shapes verified against 0.8.5), `ffprobe`, and `ffmpeg`. Google receives uploaded files: this is **not local inference**. The script never starts login or reads/prints cookies.

## Authentication

Authenticate the intended NotebookLM profile yourself, with permission to import the signed-in browser session:

```bash
notebooklm --profile default login --browser-cookies chrome
notebooklm --profile default auth check --test --json
```

If cookie support is absent, install the CLI's cookies extra (`notebooklm-py[cookies]`) using your existing installation method. Authentication can expire between generation and download; repair it manually and rerun. Do not share auth JSON or cookie files. `--profile` is always passed explicitly to NotebookLM; the script defaults to `default`, not the CLI's currently selected profile.

## Plan and run

From the repository root:

```bash
python scripts/bible_podcast.py content/Books/OT/PRO/01/PRO_01_1-7.md --dry-run
python scripts/bible_podcast.py content/Books/OT/PRO/01/PRO_01_1-7.md --allow-upload
# Exact paths may contain spaces; quote them normally.
python scripts/bible_podcast.py '/absolute/path/study one.md' --book PRO --allow-upload
python scripts/bible_podcast.py '/absolute/path/study one.md' '/absolute/path/study two.md' --topic 'Wisdom' --study 'Wisdom introduction' --allow-upload
```

- `--dry-run` is offline and read-only: validates and hashes exact files, prints routing/settings/job ID, never creates state or output directories. It does not inspect remote or cached progress.
- Only explicit regular files are accepted; no recursive directory upload. Symlinks and symlink ancestors are rejected. Files are rechecked and copied into private temporary snapshots before uploading.
- A book is inferred only when every input has the same `content/Books/OT|NT/BOOK/...` structure. Otherwise use an explicit uppercase three-character `--book` code or `--topic`. Mixed/conflicting inferred books require a topic. Use the repository's codes, including `JOL` and `JUD`.
- Each book/high-level topic gets a **collection**; each study gets its own **notebook** inside it, per profile. Collections are created lazily, or reused by saved UUID / a single exact matching name. Duplicate names require `--bind-collection UUID`; no arbitrary match is chosen. Book codes map to full names (`PRO` → `Proverbs`, `JOL` → `Joel`, `JUD` → `Jude`). Topics use `Topic: <exact topic>` collection names, so topic `Proverbs` cannot collide with the book collection. Spelling and case are significant.
- A single file defaults to a stable absolute-path study key, independent of file contents or generation settings. Its first Markdown H1 (or cleaned filename stem) supplies the notebook title. Editing it creates a new source/job in the **same notebook**, not a new notebook; existing notebooks are never renamed. Moving the file changes the implicit study identity. Use `--study 'Stable label'` from the first invocation when you need a location-independent identity.
- Multiple files require `--study 'Stable label'`, which is both an exact key and the notebook title. Reuse that label for subsequent versions of the same study. A label is scoped to the profile and book/topic; do not reuse it for unrelated studies. Files must precede options on the command line.
- `--allow-upload` explicitly authorizes Google upload of the supplied files. It is not needed for already-bound content or resuming an artifact. The command itself requests generation when no artifact exists. Source reuse does not mean notebook-wide generation: every generation receives explicit `-s` source IDs for this invocation only.
- Defaults: `--language en --format deep-dive --length long`. The default prompt requests patient source-grounded exposition, Scripture/interpretation distinctions, uncertainty, definitions, hypothetical practical examples, recaps and synthesis. `--prompt '...'` overrides it.
- Source hashes deduplicate identical bytes only within a study notebook, never across studies. The job ID includes profile, book/topic route, study key, sorted unique content hashes, and all generation settings. Within an explicit study, reordering/renaming identical files does not regenerate; changed content/settings creates a different job. Requested length is not a guaranteed duration.

## Durable state, waiting and outputs

Default registry: `$XDG_STATE_HOME/bible-podcast/registry.json`, or `~/.local/state/bible-podcast/registry.json`. Default output root: `~/Downloads/bible-podcasts`. Keep both outside Git; overrides are `--state-dir` and `--output-dir`. Outputs use `<profile-hash>/<full-job-hash>.m4a`; successful JSON prints the absolute output path, notebook URL, artifact/title, measured duration, byte count and SHA-256.

Output paths must not contain symlinks: the output root, its ancestors, and the profile-hash directory are checked before creating output directories or downloading. Verification also rejects symlinks anywhere in the audio path, including on resume. Use ordinary directories, not symlink aliases. These pathname checks are not a defense against another process maliciously replacing directories between checks; keep output directories under trusted control.

The version-2 registry is process-locked across the whole invocation and replaced atomically with fsync. Registry paths, ancestors, registry JSON and lock files must not be symlinks. Do not use different registry directories for the same workload: they cannot deduplicate each other's remote work. Back up the registry; deleting it discards knowledge of prior jobs. Keep it private because it contains local paths, prompts and remote IDs (not credentials). Concurrent invocations serialize.

Collection membership is read back by exact collection and notebook UUID before upload/generation or artifact resume. Missing membership is added and read back again. An interrupted add can be retried safely: the next run first checks current membership. A deleted saved collection/notebook is an error, never an excuse to silently create a replacement.

Each source/artifact wait is bounded by `--wait-seconds` (default 300; range 1–3600); subprocesses also have timeouts. Multiple sources can each consume this budget. Exit codes:

- **0**: verified download, successful bind-only operation, offline migration, or successful dry-run (distinguished in output).
- **2**: source/artifact not ready. Rerun the same command to continue; do not generate a new episode manually.
- **1**: validation, authentication, remote, or media error. Inspect the message and saved state.

Artifact IDs are saved **before** waiting. Resumes do not regenerate even after a failed wait, interrupted download, or auth expiry. A completed remote audio artifact plus positive-duration audio metadata and a full `ffmpeg -xerror` decode are required for download success. Existing unrelated outputs are never overwritten; download also passes `--no-clobber`. An interrupted file owned by this job is verified on resume; invalid files are retained. After inspecting a corrupt partial file, move it aside and rerun to download the same artifact. Changing the output directory of an already-started job is refused. Successful reruns verify the saved file and compare its hash without downloading again. These checks prove media integrity, **not theological accuracy or listening review**.

## Adopt existing work without a second episode

Binding operations validate full canonical UUIDs and read them back remotely. `--bind-collection`, `--bind-notebook` and `--bind-source` without `--adopt-artifact` are **bind-only**: they never create collections/notebooks, upload or generate. If both collection and notebook are bound, they may add that notebook to the collection and verify membership. Otherwise membership is established on the next execution. Bind each source separately with exactly one file (and the same explicit `--study` when appropriate). Source binding is your explicit assertion that the existing source represents those exact local bytes; ID existence does not prove matching remote contents.

`--adopt-artifact` associates an existing audio artifact with the job described by the current files/settings, then resumes/downloads it. This explicitly accepts a historical artifact whose original prompt/settings may differ. The registry records `adopted: true` and `historical_settings: "unknown; user explicitly adopted existing artifact"`; it does not claim the new defaults produced old audio. Subsequent invocations with the same current settings reuse this artifact. Do not change settings when resuming unless you intend a new job.

Existing Proverbs episode, **no upload or generation**:

```bash
python scripts/bible_podcast.py \
  content/Books/OT/PRO/01/PRO_01_1-7.md \
  --profile default --book PRO \
  --bind-notebook c04c1eb1-f6a5-4882-8234-292ea46b5cea \
  --bind-source 7fb2a481-6056-40af-9d25-5cca899611d3 \
  --adopt-artifact e49b179c-ff43-4e8c-9580-c6d05a251d3d

# Later, reuse the exact job:
python scripts/bible_podcast.py content/Books/OT/PRO/01/PRO_01_1-7.md --profile default --book PRO
```

This downloads to the new managed output path; it does not overwrite the previous `~/Downloads/PRO_01_1-7-long-instructive.m4a`.

## Migrate the previous route-level registry

Normal execution refuses legacy route-level notebooks until you explicitly migrate. Migration is **offline** and local-only; it does not create, rename, delete, upload, add membership, generate or download remotely. Run with the original study file and route:

```bash
python scripts/bible_podcast.py content/Books/OT/PRO/01/PRO_01_1-7.md --profile default --book PRO --migrate-state
# Existing Proverbs collection: bind it, then resume the original artifact/output.
python scripts/bible_podcast.py content/Books/OT/PRO/01/PRO_01_1-7.md --profile default --book PRO --bind-collection 1ad9f4d6-2e1c-4ab3-9a90-730c1919a9bd
python scripts/bible_podcast.py content/Books/OT/PRO/01/PRO_01_1-7.md --profile default --book PRO
```

The migrator validates **all** legacy routes before writing, keeps the original bytes in exclusive `registry.v1.backup.json` beside the registry, then atomically writes version 2. An existing backup is never overwritten. A crash after backup creation but before registry replacement requires inspecting both files and deliberately moving the backup aside before retrying; do not discard it. Already-migrated state is a no-op.

For a legacy route whose jobs all refer to one absolute file path, its notebook, sources, complete job records, artifact IDs, adoption metadata, uncertainty markers and output paths are preserved in that study. New job identities alias to old job keys, so the original managed audio filename is retained. `--dry-run` remains an offline plan only: its new identity may resolve to a legacy alias at execution time. Current content/settings must match a historical job to resume it; do not change them during migration/resume.

If all legacy jobs represent the same intentional multi-file study, pass all those exact files plus an explicit `--study 'Stable label'` to migration and every subsequent run. If a legacy notebook contains several unrelated studies, differing file sets, unaccounted source hashes, no usable job plans, or conflicting job identities, migration stops without changing registry/backup or remote state. It does **not** fan out notebooks or discard unknown/pending state. Recovery requires an explicit reviewed mapping: retain the old registry and notebook; inventory source/artifact IDs and pending mutations; decide which study owns each job/output; resolve uncertainty through readback; then deliberately construct a v2 mapping or use a separate registry with explicit bindings/adoption. Never copy a source/artifact UUID into a different notebook, and never delete the old shared notebook to make migration pass.

## Ambiguous mutation recovery

Before collection-create/notebook-create/upload/generate, an `uncertain` intent is atomically written. Any exception, invalid response, or process death before saving a returned ID leaves that intent in place. The script **will not blindly retry** that operation, even if the failure might have happened before the server received it. Even a newly visible exact-name collection does not clear an uncertain create: explicitly bind its verified UUID.

1. Inspect the intended profile/notebook using `notebooklm --profile PROFILE collection list --json`, `collection notebooks COLLECTION_UUID --json`, `list --json`, `source list -n UUID --json`, or `artifact list -n UUID --json` (always pass the intended profile).
2. If the operation succeeded, use `--bind-collection`, `--bind-notebook`, `--bind-source` (one exact file), or `--adopt-artifact` with the recovered UUID and original study/job arguments. Readback succeeds before the corresponding uncertainty is cleared. Existing conflicting bindings cannot be replaced.
3. If you positively establish that no remote object was created, stop all script instances, back up the registry, and deliberately remove only that failed entry's `uncertain` field before retrying. This is a manual recovery decision, not an automated retry facility. Do not discard the registry or change job settings to evade an uncertain generation.

## Tests

```bash
uv run --extra dev pytest -o asyncio_default_fixture_loop_scope=function tests/test_bible_podcast.py -q
uv run --extra dev pytest -o asyncio_default_fixture_loop_scope=function -q
```

Cloud tests replace only the subprocess runner and exercise the real routing/registry/resume logic. They perform no remote writes or credential access. A local integration test creates a short sine-wave audio fixture using real ffmpeg and checks real ffprobe/full decode, then rejects corruption. Tests also exercise process locking in a separate Python process.
