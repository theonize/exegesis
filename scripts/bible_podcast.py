#!/usr/bin/env python3
"""Durable, explicitly scoped NotebookLM audio jobs (stdlib; Linux/macOS)."""
import argparse
import hashlib
import json
import os
import sys
import subprocess
import tempfile
import fcntl
import uuid
import re
import copy
from pathlib import Path

RUN = subprocess.run
BOOKS = {code: name for code, name in (line.split('=', 1) for line in '''GEN=Genesis
EXO=Exodus
LEV=Leviticus
NUM=Numbers
DEU=Deuteronomy
JOS=Joshua
JDG=Judges
RUT=Ruth
1SA=1 Samuel
2SA=2 Samuel
1KI=1 Kings
2KI=2 Kings
1CH=1 Chronicles
2CH=2 Chronicles
EZR=Ezra
NEH=Nehemiah
EST=Esther
JOB=Job
PSA=Psalms
PRO=Proverbs
ECC=Ecclesiastes
SNG=Song of Solomon
ISA=Isaiah
JER=Jeremiah
LAM=Lamentations
EZK=Ezekiel
DAN=Daniel
HOS=Hosea
JOL=Joel
AMO=Amos
OBA=Obadiah
JON=Jonah
MIC=Micah
NAH=Nahum
HAB=Habakkuk
ZEP=Zephaniah
HAG=Haggai
ZEC=Zechariah
MAL=Malachi
MAT=Matthew
MRK=Mark
LUK=Luke
JHN=John
ACT=Acts
ROM=Romans
1CO=1 Corinthians
2CO=2 Corinthians
GAL=Galatians
EPH=Ephesians
PHP=Philippians
COL=Colossians
1TH=1 Thessalonians
2TH=2 Thessalonians
1TI=1 Timothy
2TI=2 Timothy
TIT=Titus
PHM=Philemon
HEB=Hebrews
JAS=James
1PE=1 Peter
2PE=2 Peter
1JN=1 John
2JN=2 John
3JN=3 John
JUD=Jude
REV=Revelation'''.splitlines())}


def remote_id(value):
    if not isinstance(value, str) or str(uuid.UUID(value)) != value:
        raise ValueError('Expected a full canonical UUID, not a partial ID')
    return value


class Registry:
    def __init__(self, root):
        self.root = root.expanduser().absolute()

    def __enter__(self):
        if any(p.is_symlink() for p in (self.root, *self.root.parents,
                                       self.root / 'registry.lock', self.root / 'registry.json')):
            raise ValueError('Registry must not contain symlinks or symlink ancestors')
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = (self.root / 'registry.lock').open('a')
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        self.path = self.root / 'registry.json'
        self.data = json.loads(self.path.read_text()) if self.path.exists() else {'version': 2, 'profiles': {}}
        return self

    def save(self):
        fd, name = tempfile.mkstemp(dir=self.root, prefix='.registry-')
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(self.data, stream, indent=2)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.path)
            fd = os.open(self.root, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def __exit__(self, *exc):
        self.lock.close()


class Client:
    def __init__(self, profile):
        self.prefix = ['notebooklm', '--profile', profile]

    def call(self, *args, timeout=120, allow_failure=False):
        result = RUN(self.prefix + list(args) + ['--json'], capture_output=True, text=True, timeout=timeout)
        if result.returncode and not allow_failure:
            raise RuntimeError('NotebookLM command failed; check authentication manually and inspect remote state')
        try:
            return json.loads(result.stdout)
        except ValueError:
            raise RuntimeError('NotebookLM did not return valid JSON') from None


def mutate(registry, target, key, action):
    if target.get('uncertain'):
        raise RuntimeError('Uncertain prior mutation: inspect NotebookLM and bind/adopt its ID; never retry blindly')
    target['uncertain'] = key
    registry.save()  # Write intent before the remote side effect, including process death.
    value = remote_id(action())
    target[key] = value
    del target['uncertain']
    registry.save()
    return value


def bind(target, key, value):
    if key in target and target[key] != value:
        raise ValueError(f'Refusing to replace existing {key} binding')
    target[key] = value
    target.pop('uncertain', None)


def artifact(client, nb, aid):
    result = client.call('artifact', 'get', aid, '-n', nb)
    if result.get('found') is False or result.get('id') != aid or result.get('type_id') != 'audio':
        raise ValueError('Artifact readback must match exact ID and audio type')
    return result


def verify_audio(path):
    path = path.absolute()
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file() or not path.stat().st_size:
        raise ValueError('Missing or unsafe audio output')
    result = RUN(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, timeout=120)
    if result.returncode:
        raise ValueError('ffprobe failed')
    metadata = json.loads(result.stdout)
    duration = float(metadata['format']['duration'])
    if not 0 < duration < float('inf') or not any(s.get('codec_type') == 'audio' for s in metadata['streams']):
        raise ValueError('Output has no valid audio duration/stream')
    result = RUN(['ffmpeg', '-nostdin', '-v', 'error', '-xerror', '-i', str(path), '-map', '0:a:0', '-f', 'null', '-'], capture_output=True, text=True, timeout=1800)
    if result.returncode:
        raise ValueError('Full audio decode failed; output retained for inspection')
    return {'duration_seconds': duration, 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def download(args, data, registry, client, nb, job, art):
    folder = args.output_dir.expanduser().absolute() / digest(args.profile)[:16]
    if any(p.is_symlink() for p in (folder, *folder.parents)):
        raise ValueError('Output must not have symlink ancestors')
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / (data['job'] + '.m4a')
    if 'output' in job and job['output'] != str(output):
        raise ValueError('Job already has an output path; reuse its original --output-dir')
    if output.exists() or output.is_symlink():
        if not job.get('download_started') or job.get('output') != str(output):
            raise ValueError('Refusing to clobber an existing output')
    else:
        job['output'] = str(output)
        job['download_started'] = True
        registry.save()
        # The CLI also enforces no-clobber if another process creates the file.
        client.call('download', 'audio', str(output), '-n', nb, '-a', job['artifact'], '--no-clobber', timeout=600)
    metrics = verify_audio(output)
    if job.get('verified') and metrics['sha256'] != job['verified']['sha256']:
        raise ValueError('Previously verified output has changed')
    job['verified'] = metrics
    registry.save()
    print(json.dumps({'job': data['job'], 'artifact': job['artifact'], 'title': art.get('title'), 'notebook_url': f'https://notebooklm.google.com/notebook/{nb}', 'output': str(output), **metrics}, indent=2))
    return 0


def upload(client, nb, item):
    path = Path(item['path'])
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('Input became unsafe before upload')
    content = path.read_bytes()
    if hashlib.sha256(content).hexdigest() != item['sha256']:
        raise ValueError('Input changed since planning; rerun with the intended content')
    # Upload a private snapshot, not a mutable original pathname.
    with tempfile.TemporaryDirectory(prefix='bible-podcast-') as folder:
        snapshot = Path(folder) / path.name
        snapshot.write_bytes(content)
        return client.call('source', 'add', str(snapshot), '--type', 'file', '-n', nb)['source']['id']


def ensure_collection(registry, client, group, name):
    collections = client.call('collection', 'list')['collections']
    if 'collection' not in group:
        if group.get('uncertain'):
            raise RuntimeError('Uncertain collection create; inspect and --bind-collection before retrying')
        matches = [c for c in collections if c.get('name') == name]
        if len(matches) > 1:
            raise ValueError('Ambiguous collection name; use --bind-collection with an exact UUID')
        if matches:
            group['collection'] = remote_id(matches[0]['id'])
            registry.save()
        else:
            mutate(registry, group, 'collection', lambda: client.call('collection', 'create', name)['id'])
            collections = client.call('collection', 'list')['collections']
    cid = remote_id(group['collection'])
    if not any(c.get('id') == cid for c in collections):
        raise ValueError('Bound collection no longer exists; refusing replacement')
    return cid


def ensure_membership(client, cid, nb):
    def contains():
        result = client.call('collection', 'notebooks', cid)
        if result.get('collection_id') != cid:
            raise ValueError('Collection membership readback has wrong collection ID')
        return any(n.get('id') == nb for n in result['notebooks'])
    if not contains():
        client.call('collection', 'add', cid, nb)
        if not contains():
            raise ValueError('Collection membership readback missing exact notebook ID')


def legacy_routes(data):
    return [(profile, key, route) for profile, entry in data['profiles'].items()
            for key, route in entry['routes'].items() if 'studies' not in route]


def migrate(registry, args, data):
    """Offline, all-or-nothing conversion; never split a shared legacy notebook."""
    converted = copy.deepcopy(registry.data)
    legacy = legacy_routes(converted)
    if not legacy:
        print('Registry already uses study notebooks; no migration needed.')
        return
    for profile, key, route in legacy:
        guidance = (f'Migration blocked for {profile}/{key}: cannot prove one study. '
                    'Keep the registry intact; back it up, inventory notebook/source/artifact IDs, '
                    'and explicitly reconcile each study and pending mutation before manual migration. '
                    'Never fan out or delete the shared notebook. See docs/notebooklm-podcasts.md.')
        jobs = route.get('jobs', {})
        paths = {tuple(sorted({f['path'] for f in j['plan']['files']})) for j in jobs.values()}
        if len(paths) != 1:
            raise ValueError(guidance)
        study_paths = next(iter(paths))
        if not study_paths:
            raise ValueError(guidance)
        if any(not Path(p).is_absolute() for p in study_paths):
            raise ValueError(guidance)
        selected = (profile == args.profile and key == data['route'] and
                    study_paths == tuple(sorted({f['path'] for f in data['files']})))
        if len(study_paths) > 1 and not (selected and args.study):
            raise ValueError(guidance + ' For one intentional multi-file study, rerun with its exact files and --study label.')
        study = data['study'] if selected and args.study else 'path:' + study_paths[0]
        known_hashes = {h for j in jobs.values() for h in j['plan']['hashes']}
        if set(route.get('sources', {})) - known_hashes:
            raise ValueError(guidance)
        aliases = {}
        for old_key, job in jobs.items():
            plan = job['plan']
            if plan['profile'] != profile or plan['route'] != key:
                raise ValueError(guidance)
            identity = {k: plan[k] for k in ('profile', 'route', 'hashes', 'settings')}
            identity['study'] = study
            alias = digest(identity)
            if alias in aliases and aliases[alias] != old_key:
                raise ValueError(guidance)
            aliases[alias] = old_key
        route['job_aliases'] = aliases
        converted['profiles'][profile]['routes'][key] = {'studies': {study: route}}
    converted['version'] = 2
    backup = registry.root / 'registry.v1.backup.json'
    # Exclusive creation: an old backup is evidence, never overwrite it.
    with backup.open('xb') as stream:
        os.chmod(backup, 0o600)
        stream.write(registry.path.read_bytes())
        stream.flush()
        os.fsync(stream.fileno())
    registry.data = converted
    registry.save()
    print(f'Migrated registry to version 2; original retained at {backup}. No network operations.')


def workflow(args, data):
    with Registry(args.state_dir) as registry:
        if registry.data.get('version', 1) not in (1, 2):
            raise ValueError('Unsupported registry version')
        if args.migrate_state:
            migrate(registry, args, data)
            return 0
        if legacy_routes(registry.data):
            raise ValueError('Legacy registry requires explicit offline --migrate-state; see migration documentation')
        registry.data['version'] = 2
        profile = registry.data['profiles'].setdefault(args.profile, {'routes': {}})
        group = profile['routes'].setdefault(data['route'], {'studies': {}})
        route = group['studies'].setdefault(data['study'], {'sources': {}, 'jobs': {}})
        data = dict(data, job=route.get('job_aliases', {}).get(data['job'], data['job']))
        job = route['jobs'].setdefault(data['job'], {'plan': data})
        client = Client(args.profile)
        if args.bind_collection:
            cid = remote_id(args.bind_collection)
            if not any(c.get('id') == cid for c in client.call('collection', 'list')['collections']):
                raise ValueError('Collection binding not found')
            bind(group, 'collection', cid)
            registry.save()
        if args.bind_notebook:
            nb = remote_id(args.bind_notebook)
            if not any(n['id'] == nb for n in client.call('list')['notebooks']):
                raise ValueError('Notebook binding not found')
            bind(route, 'notebook', nb)
            registry.save()
        if args.bind_source or args.adopt_artifact:
            if 'notebook' not in route:
                raise ValueError('Bind notebook first')
            nb = route['notebook']
            if args.bind_source:
                if len(data['files']) != 1:
                    raise ValueError('--bind-source requires exactly one input file')
                sid = remote_id(args.bind_source)
                source = client.call('source', 'get', sid, '-n', nb)
                if source.get('found') is False or source.get('source', {}).get('id') != sid:
                    raise ValueError('Source binding readback failed')
                bind(route['sources'].setdefault(data['files'][0]['sha256'], {}), 'id', sid)
            if args.adopt_artifact:
                aid = remote_id(args.adopt_artifact)
                artifact(client, nb, aid)
                bind(job, 'artifact', aid)
                job['adopted'] = True
                job['historical_settings'] = 'unknown; user explicitly adopted existing artifact'
            registry.save()
        # Bind-only operations never create, upload or generate.
        if (args.bind_collection or args.bind_notebook or args.bind_source) and not args.adopt_artifact:
            if 'collection' in group and 'notebook' in route:
                cid = ensure_collection(registry, client, group, data['collection_name'])
                ensure_membership(client, cid, route['notebook'])
            print('Binding saved; rerun without binding flags to execute the job.')
            return 0
        missing = [f for f in data['files'] if not route['sources'].get(f['sha256'], {}).get('id')]
        if missing and not args.allow_upload and 'artifact' not in job:
            raise ValueError('Uploading to Google requires --allow-upload (exact files only)')
        cid = ensure_collection(registry, client, group, data['collection_name'])
        if 'notebook' not in route:
            mutate(registry, route, 'notebook', lambda: client.call('create', data['notebook_title'])['notebook']['id'])
        nb = route['notebook']
        notebooks = client.call('list')['notebooks']
        if not any(n['id'] == nb for n in notebooks):
            raise ValueError('Bound notebook no longer exists; refusing to create a replacement')
        ensure_membership(client, cid, nb)
        source_ids = []
        for item in ([] if 'artifact' in job else data['files']):
            entry = route['sources'].setdefault(item['sha256'], {})
            if 'id' not in entry:
                mutate(registry, entry, 'id', lambda: upload(client, nb, item))
            sid = entry['id']
            source = client.call('source', 'get', sid, '-n', nb)
            if source.get('found') is False or source.get('source', {}).get('id') != sid:
                raise ValueError('Source readback does not match the saved ID')
            result = client.call('source', 'wait', sid, '-n', nb, '--timeout', str(args.wait_seconds), timeout=args.wait_seconds + 30, allow_failure=True)
            if result.get('source', result).get('status') != 'ready':
                print('Source pending or failed; rerun to inspect/resume.', file=sys.stderr)
                return 2
            if sid not in source_ids:
                source_ids.append(sid)
        if 'artifact' not in job:
            command = ['generate', 'audio', args.prompt, '-n', nb]
            for sid in source_ids:
                command += ['-s', sid]
            command += ['--language', args.language, '--format', args.format, '--length', args.length]
            mutate(registry, job, 'artifact', lambda: client.call(*command)['task_id'])
        art = artifact(client, nb, job['artifact'])
        if art.get('status') != 'completed':
            client.call('artifact', 'wait', job['artifact'], '-n', nb, '--timeout', str(args.wait_seconds), '--interval', '15', timeout=args.wait_seconds + 30, allow_failure=True)
            art = artifact(client, nb, job['artifact'])
        if art.get('status') != 'completed':
            print(json.dumps({'job': data['job'], 'artifact': job['artifact'], 'status': art.get('status'), 'resume': 'Rerun the same command; no regeneration.'}))
            return 2
        return download(args, data, registry, client, nb, job, art)

PROMPT = '''Create a patient, substantive, instructive conversation for serious non-specialists.
Use only the selected sources. Explain the passage in its historical, literary,
linguistic and canonical context. Distinguish Scripture from the study author's
interpretation, tradition, inference and application. Flag uncertain or disputed
scholarly claims; do not invent evidence or citations. Define unfamiliar terms.
Work through the argument rather than rushing to a summary. Give practical examples
explicitly labeled hypothetical, avoid promising outcomes the text does not promise,
and include brief recaps and a thoughtful final synthesis.'''


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('files', nargs='+', help='Exact regular files; never directories')
    route = p.add_mutually_exclusive_group()
    route.add_argument('--book')
    route.add_argument('--topic')
    p.add_argument('--study', help='Stable, exact study key and title (required for multiple files)')
    p.add_argument('--profile', default='default')
    p.add_argument('--state-dir', type=Path, default=Path(os.environ.get('XDG_STATE_HOME', str(Path.home() / '.local/state'))) / 'bible-podcast')
    p.add_argument('--output-dir', type=Path, default=Path.home() / 'Downloads/bible-podcasts')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--migrate-state', action='store_true', help='Offline v1-to-v2 migration with exclusive backup; no remote calls')
    p.add_argument('--allow-upload', action='store_true')
    p.add_argument('--wait-seconds', type=int, default=300)
    p.add_argument('--bind-notebook', help='Read-validate and bind an existing notebook UUID')
    p.add_argument('--bind-collection', help='Bind an existing collection UUID; ensure membership if notebook is bound')
    p.add_argument('--bind-source', help='Bind existing source UUID to the single supplied file hash')
    p.add_argument('--adopt-artifact', help='Adopt an existing audio UUID, regardless of historic prompt')
    p.add_argument('--language', default='en')
    p.add_argument('--format', choices=['deep-dive', 'brief', 'critique', 'debate'], default='deep-dive')
    p.add_argument('--length', choices=['short', 'default', 'long'], default='long')
    p.add_argument('--prompt', default=PROMPT)
    return p


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def plan(args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', args.profile):
        raise ValueError('Unsafe profile name')
    if args.book and not re.fullmatch(r'[1-3A-Z][A-Z]{2}', args.book):
        raise ValueError('Use the exact uppercase three-character book code')
    if not 1 <= args.wait_seconds <= 3600:
        raise ValueError('--wait-seconds must be between 1 and 3600')
    for value in (args.bind_collection, args.bind_notebook, args.bind_source, args.adopt_artifact):
        if value is not None:
            remote_id(value)
    files = []
    books = set()
    inferred_count = 0
    for name in args.files:
        path = Path(name).expanduser().absolute()
        if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
            raise ValueError(f'Input must be a regular file without symlink ancestors: {path}')
        files.append({'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        parts = path.parts
        for i in range(len(parts) - 3):
            if parts[i:i+2] == ('content', 'Books') and parts[i+2] in ('OT', 'NT'):
                books.add(parts[i+3])
                inferred_count += 1
                break
    if not args.topic and (len(books) > 1 or (args.book and books and books != {args.book})):
        raise ValueError('Mixed or conflicting books require --topic')
    if not args.topic and not args.book and (len(books) != 1 or inferred_count != len(files)):
        raise ValueError('Cannot infer a single book; supply --book or --topic')
    if args.topic is not None and not args.topic.strip():
        raise ValueError('Topic cannot be empty')
    route = 'topic:' + args.topic if args.topic else 'book:' + (args.book or next(iter(books)))
    settings = {'language': args.language, 'format': args.format, 'length': args.length, 'prompt': args.prompt}
    if not args.topic and route[5:] not in BOOKS:
        raise ValueError('Unknown repository book code')
    if args.study is not None and not args.study.strip():
        raise ValueError('Study cannot be empty')
    if len(files) != 1 and not args.study:
        raise ValueError('Multiple files require an explicit --study key/label')
    study = 'named:' + args.study if args.study else 'path:' + files[0]['path']
    title = args.study
    if title is None:
        path = Path(files[0]['path'])
        heading = re.search(r'^#\s+(.+?)\s*#*\s*$', path.read_text(errors='replace'), re.MULTILINE)
        title = heading.group(1) if heading else re.sub(r'[_-]+', ' ', path.stem).strip()
    identity = {'profile': args.profile, 'route': route, 'study': study, 'hashes': sorted({f['sha256'] for f in files}), 'settings': settings}
    return dict(identity, files=files, job=digest(identity), notebook_title=title,
                collection_name='Topic: ' + args.topic if args.topic else BOOKS[route[5:]])


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        data = plan(args)
        if args.dry_run:
            print(json.dumps(data, indent=2))
            return 0
        return workflow(args, data)
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError, KeyError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
