"""Offline tests: only the subprocess boundary is replaced."""
import importlib.util
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'bible_podcast.py'

def load():
    spec = importlib.util.spec_from_file_location('bible_podcast', SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_study_identity_title_and_collection(tmp_path):
    m = load()
    argv = setup_job(tmp_path, m)
    Path(argv[0]).write_text('# Proverbs 1:1–7 — Purpose\nText')
    first = m.plan(m.parser().parse_args(argv))
    assert first['collection_name'] == 'Proverbs'
    assert first['notebook_title'] == 'Proverbs 1:1–7 — Purpose'
    Path(argv[0]).write_text('Edited')
    changed = m.plan(m.parser().parse_args(argv + ['--length', 'short']))
    assert first['study'] == changed['study']
    assert first['job'] != changed['job']
    other = tmp_path / 'other.md'
    other.write_text('Edited')
    with pytest.raises(ValueError, match='--study'):
        m.plan(m.parser().parse_args([str(other)] + argv))
    explicit = m.plan(m.parser().parse_args([str(other)] + argv + ['--study', 'Wisdom introduction']))
    assert explicit['study'] == 'named:Wisdom introduction'
    assert explicit['notebook_title'] == 'Wisdom introduction'
    topic = m.plan(m.parser().parse_args([str(other), '--topic', 'Proverbs']))
    assert topic['collection_name'] == 'Topic: Proverbs'


def test_offline_plan_infers_book_and_stable_job(tmp_path):
    assert SCRIPT.exists(), 'CLI implementation is missing'
    m = load()
    f = tmp_path / 'content/Books/OT/PRO/01/study with spaces.md'
    f.parent.mkdir(parents=True)
    f.write_text('Wisdom')
    args = m.parser().parse_args([str(f), '--dry-run'])
    plan = m.plan(args)
    assert plan['route'] == 'book:PRO'
    assert plan['job'] == m.plan(args)['job']
    f.write_text('Changed')
    assert plan['job'] != m.plan(args)['job']
    assert m.main([str(f), '--dry-run', '--state-dir', str(tmp_path / 'state')]) == 0
    assert not (tmp_path / 'state').exists()


def test_rejects_symlink_ancestors_directories_and_ambiguous_routes(tmp_path):
    m = load()
    root = tmp_path / 'real'
    root.mkdir()
    f = root / 'a.md'
    f.write_text('text')
    link = tmp_path / 'link'
    link.symlink_to(root, target_is_directory=True)
    for names in ([str(link / 'a.md'), '--topic', 'Wisdom'], [str(root), '--topic', 'Wisdom'], [str(f)]):
        with pytest.raises(ValueError):
            m.plan(m.parser().parse_args(names))
    paths = []
    for book in ('PRO', 'JHN'):
        path = tmp_path / f'content/Books/OT/{book}/study.md'
        path.parent.mkdir(parents=True)
        path.write_text(book)
        paths.append(str(path))
    with pytest.raises(ValueError, match='topic'):
        m.plan(m.parser().parse_args(paths + ['--book', 'PRO']))
    assert m.plan(m.parser().parse_args(paths + ['--topic', 'Wisdom', '--study', 'Introduction']))['route'] == 'topic:Wisdom'


NB = '11111111-1111-4111-8111-111111111111'
SRC = '22222222-2222-4222-8222-222222222222'
ART = '33333333-3333-4333-8333-333333333333'
COLLECTION = '44444444-4444-4444-8444-444444444444'

class Cloud:
    def __init__(self):
        self.calls = []
        self.completed = False
        self.fail: list[str] | None = None
        self.collections = []
        self.members = set()
        self.notebooks = [NB]  # Also allow explicit adoption of a pre-existing notebook.
        self.created_notebooks = 0

    def __call__(self, argv, **kwargs):
        import json
        import subprocess
        self.calls.append(argv)
        cmd = argv[3:]
        if self.fail and cmd[:len(self.fail)] == self.fail:
            raise RuntimeError('ambiguous network failure')
        if cmd[:2] == ['collection', 'list']:
            data = {'collections': self.collections}
        elif cmd[:2] == ['collection', 'create']:
            self.collections.append({'id': COLLECTION, 'name': cmd[2]})
            data = {'id': COLLECTION, 'name': cmd[2], 'notebook_ids': []}
        elif cmd[:2] == ['collection', 'notebooks']:
            data = {'collection_id': cmd[2], 'notebooks': [{'id': n} for n in self.members]}
        elif cmd[:2] == ['collection', 'add']:
            self.members.add(cmd[3])
            data = {'id': cmd[2], 'added_notebook_ids': [cmd[3]], 'notebook_ids': list(self.members)}
        elif cmd[0] == 'create':
            import uuid
            nb = NB if self.created_notebooks == 0 else str(uuid.uuid4())
            self.created_notebooks += 1
            if nb not in self.notebooks:
                self.notebooks.append(nb)
            data = {'notebook': {'id': nb}}
        elif cmd[0] == 'list':
            data = {'notebooks': [{'id': nb} for nb in self.notebooks]}
        elif cmd[:2] == ['source', 'add']:
            data = {'source': {'id': SRC}}
        elif cmd[:2] in (['source', 'get'], ['source', 'wait']):
            data = {'source': {'id': SRC, 'status': 'ready'}, 'found': True}
        elif cmd[:2] == ['generate', 'audio']:
            data = {'task_id': ART, 'status': 'pending'}
        elif cmd[:2] in (['artifact', 'get'], ['artifact', 'wait']):
            data = {'id': ART, 'found': True, 'type_id': 'audio', 'status': 'completed' if self.completed else 'in_progress'}
        else:
            raise AssertionError(argv)
        return subprocess.CompletedProcess(argv, 0, json.dumps(data), '')


def setup_job(tmp_path, m):
    f = tmp_path / 'study with spaces.md'
    f.write_text('Study')
    return [str(f), '--book', 'PRO', '--state-dir', str(tmp_path / 'state'), '--output-dir', str(tmp_path / 'out')]


def test_collection_reused_and_sources_scoped_per_study(tmp_path, monkeypatch):
    import json
    m = load()
    cloud = Cloud()
    cloud.collections = [{'id': COLLECTION, 'name': 'Proverbs'}]
    monkeypatch.setattr(m, 'RUN', cloud)
    argv = setup_job(tmp_path, m)
    assert m.main(argv + ['--allow-upload']) == 2
    other = tmp_path / 'second.md'
    other.write_text(Path(argv[0]).read_text())
    assert m.main([str(other)] + argv[1:] + ['--allow-upload']) == 2
    assert sum(c[3] == 'create' for c in cloud.calls) == 2
    assert sum(c[3:5] == ['source', 'add'] for c in cloud.calls) == 2
    assert not any(c[3:5] == ['collection', 'create'] for c in cloud.calls)
    assert any(c[3:5] == ['collection', 'add'] for c in cloud.calls)
    state = json.loads((tmp_path / 'state/registry.json').read_text())
    route = state['profiles']['default']['routes']['book:PRO']
    assert route['collection'] == COLLECTION
    assert len(route['studies']) == 2
    assert len({s['notebook'] for s in route['studies'].values()}) == 2
    assert m.main(argv) == 2
    assert sum(c[3:5] == ['collection', 'notebooks'] for c in cloud.calls) >= 4


def test_pending_job_resumes_without_regeneration_and_requires_consent(tmp_path, monkeypatch):
    m = load()
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud, raising=False)
    argv = setup_job(tmp_path, m)
    assert m.main(argv) == 1
    assert cloud.calls == []
    assert m.main(argv + ['--allow-upload', '--wait-seconds', '1']) == 2
    assert m.main(argv + ['--wait-seconds', '1']) == 2
    assert sum(c[3:5] == ['generate', 'audio'] for c in cloud.calls) == 1
    assert sum(c[3:5] == ['source', 'add'] for c in cloud.calls) == 1
    generation = next(c for c in cloud.calls if c[3:5] == ['generate', 'audio'])
    assert generation[generation.index('-s') + 1] == SRC
    assert all(c[1:3] == ['--profile', 'default'] for c in cloud.calls)


def test_adopt_existing_artifact_never_generates_and_downloads_verified_audio(tmp_path, monkeypatch):
    import json
    import subprocess
    m = load()
    cloud = Cloud()
    cloud.completed = True
    commands = []
    def runner(argv, **kwargs):
        commands.append(argv)
        if argv[0] == 'ffprobe':
            return subprocess.CompletedProcess(argv, 0, json.dumps({'format': {'duration': '12.5'}, 'streams': [{'codec_type': 'audio', 'codec_name': 'aac'}]}), '')
        if argv[0] == 'ffmpeg':
            return subprocess.CompletedProcess(argv, 0, '', '')
        if argv[3:5] == ['download', 'audio']:
            assert '--no-clobber' in argv
            Path(argv[5]).write_bytes(b'verified-test-audio')
            return subprocess.CompletedProcess(argv, 0, '{}', '')
        return cloud(argv, **kwargs)
    monkeypatch.setattr(m, 'RUN', runner, raising=False)
    argv = setup_job(tmp_path, m)
    adopt = ['--bind-notebook', NB, '--bind-source', SRC, '--adopt-artifact', ART]
    assert m.main(argv + adopt) == 0
    assert not any(c[3] in ('create', 'generate') or c[3:5] == ['source', 'add'] for c in cloud.calls)
    files = list((tmp_path / 'out').rglob('*.m4a'))
    assert len(files) == 1
    assert any(c[0] == 'ffmpeg' for c in commands)
    assert m.main(argv) == 0
    assert sum(c[3:5] == ['download', 'audio'] for c in commands) == 1
    state = json.loads((tmp_path / 'state/registry.json').read_text())
    study = next(iter(state['profiles']['default']['routes']['book:PRO']['studies'].values()))
    job = next(iter(study['jobs'].values()))
    assert job['adopted'] is True
    assert job['historical_settings'] == 'unknown; user explicitly adopted existing artifact'


@pytest.mark.parametrize('failure', [['collection', 'create'], ['create'], ['source', 'add'], ['generate', 'audio']])
def test_ambiguous_mutations_fail_closed(tmp_path, monkeypatch, failure):
    m = load()
    cloud = Cloud()
    cloud.fail = failure
    monkeypatch.setattr(m, 'RUN', cloud)
    argv = setup_job(tmp_path, m) + ['--allow-upload']
    assert m.main(argv) == 1
    assert m.main(argv) == 1
    assert sum(c[3:3+len(failure)] == failure for c in cloud.calls) == 1


def test_ambiguous_collection_requires_binding_and_membership_verified(tmp_path, monkeypatch):
    m = load()
    cloud = Cloud()
    cloud.collections = [{'id': COLLECTION, 'name': 'Proverbs'}, {'id': SRC, 'name': 'Proverbs'}]
    monkeypatch.setattr(m, 'RUN', cloud)
    argv = setup_job(tmp_path, m)
    assert m.main(argv + ['--allow-upload']) == 1
    assert not any(c[3] == 'create' for c in cloud.calls)
    assert m.main(argv + ['--bind-collection', COLLECTION, '--bind-notebook', NB]) == 0
    assert NB in cloud.members
    assert not any(c[3] in ('create', 'generate') for c in cloud.calls)
    assert m.main(argv + ['--allow-upload']) == 2


@pytest.mark.parametrize('wrong', ['collection', 'notebook'])
def test_membership_requires_exact_readback(tmp_path, monkeypatch, wrong):
    import json
    m = load()
    cloud = Cloud()
    def runner(argv, **kwargs):
        result = cloud(argv, **kwargs)
        if argv[3:5] == ['collection', 'notebooks']:
            result.stdout = json.dumps({'collection_id': SRC if wrong == 'collection' else COLLECTION,
                                       'notebooks': [{'id': ART}]})
        return result
    monkeypatch.setattr(m, 'RUN', runner)
    assert m.main(setup_job(tmp_path, m) + ['--allow-upload']) == 1
    assert not any(c[3:5] == ['source', 'add'] for c in cloud.calls)


def test_changed_file_during_remote_lookup_is_not_uploaded(tmp_path, monkeypatch):
    m = load()
    argv = setup_job(tmp_path, m)
    cloud = Cloud()
    def runner(cmd, **kwargs):
        if cmd[3] == 'list':
            Path(argv[0]).write_text('changed after plan')
        return cloud(cmd, **kwargs)
    monkeypatch.setattr(m, 'RUN', runner)
    assert m.main(argv + ['--allow-upload']) == 1
    assert not any(c[3:5] == ['source', 'add'] for c in cloud.calls)


@pytest.mark.parametrize('extra', [['--book', 'pro'], ['--wait-seconds', '0'], ['--bind-notebook', 'abc'], ['--profile', '../unsafe']])
def test_invalid_options_fail_offline_before_state_or_network(tmp_path, monkeypatch, extra):
    m = load()
    argv = setup_job(tmp_path, m)
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    assert m.main(argv + extra + ['--dry-run']) == 1
    assert not cloud.calls
    assert not (tmp_path / 'state').exists()


def test_profiles_topics_and_content_dedupe(tmp_path, monkeypatch):
    m = load()
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    argv = setup_job(tmp_path, m)
    assert m.main(argv + ['--allow-upload']) == 2
    assert m.main(argv + ['--prompt', 'different prompt']) == 2
    assert sum(c[3:5] == ['source', 'add'] for c in cloud.calls) == 1
    assert sum(c[3] == 'create' for c in cloud.calls) == 1
    assert m.main(argv + ['--profile', 'other', '--allow-upload']) == 2
    assert sum(c[3] == 'create' for c in cloud.calls) == 2
    topic = [x for x in argv if x not in ('--book', 'PRO')] + ['--topic', 'Wisdom', '--allow-upload']
    assert m.main(topic) == 2
    assert sum(c[3] == 'create' for c in cloud.calls) == 3


def test_real_audio_validation_rejects_corruption(tmp_path):
    import shutil
    import subprocess
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        pytest.skip('ffmpeg/ffprobe required for integration check')
    m = load()
    path = tmp_path / 'sound.m4a'
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=0.1', '-c:a', 'aac', str(path)], check=True)
    assert m.verify_audio(path)['duration_seconds'] > 0
    path.write_bytes(b'not audio')
    with pytest.raises(ValueError, match='ffprobe'):
        m.verify_audio(path)


def test_source_readback_wrong_id_prevents_generation(tmp_path, monkeypatch):
    import json
    m = load()
    cloud = Cloud()
    def runner(argv, **kwargs):
        result = cloud(argv, **kwargs)
        if argv[3:5] == ['source', 'get']:
            result.stdout = json.dumps({'source': {'id': NB, 'status': 'ready'}, 'found': True})
        return result
    monkeypatch.setattr(m, 'RUN', runner)
    assert m.main(setup_job(tmp_path, m) + ['--allow-upload']) == 1
    assert not any(c[3:5] == ['generate', 'audio'] for c in cloud.calls)


def test_output_no_clobber_and_decode_failure(tmp_path, monkeypatch):
    import subprocess
    import json
    m = load()
    args = m.parser().parse_args(setup_job(tmp_path, m))
    data = m.plan(args)
    folder = args.output_dir / m.digest(args.profile)[:16]
    folder.mkdir(parents=True)
    output = folder / (data['job'] + '.m4a')
    output.write_bytes(b'keep me')
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    with m.Registry(args.state_dir) as reg:
        with pytest.raises(ValueError, match='clobber'):
            m.download(args, data, reg, m.Client('default'), NB, {'artifact': ART}, {})
    assert output.read_bytes() == b'keep me'
    assert not cloud.calls
    def runner(argv, **kwargs):
        if argv[0] == 'ffprobe':
            return subprocess.CompletedProcess(argv, 0, json.dumps({'format': {'duration': '1'}, 'streams': [{'codec_type': 'audio'}]}), '')
        return subprocess.CompletedProcess(argv, 1, '', 'corrupt')
    monkeypatch.setattr(m, 'RUN', runner)
    with pytest.raises(ValueError, match='decode'):
        m.verify_audio(output)


def test_registry_is_locked_between_processes_and_atomic(tmp_path):
    import subprocess
    import sys
    import json
    m = load()
    with m.Registry(tmp_path / 'state') as reg:
        reg.data['sentinel'] = 'preserved'
        reg.save()
        script = 'import fcntl,sys; f=open(sys.argv[1],"a"); fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)'
        child = subprocess.run([sys.executable, '-c', script, str(reg.root / 'registry.lock')], capture_output=True)
        assert child.returncode != 0
        assert json.loads(reg.path.read_text())['sentinel'] == 'preserved'
    child = subprocess.run([sys.executable, '-c', script, str(reg.root / 'registry.lock')], capture_output=True)
    assert child.returncode == 0
    assert not list(reg.root.glob('.registry-*'))


@pytest.mark.parametrize('location', ['root', 'ancestor', 'profile', 'dangling'])
def test_download_rejects_symlink_ancestry_before_side_effects(tmp_path, monkeypatch, location):
    m = load()
    args = m.parser().parse_args(setup_job(tmp_path, m))
    data = m.plan(args)
    target = tmp_path / 'outside'
    if location != 'dangling':
        target.mkdir()
    if location == 'profile':
        args.output_dir.mkdir()
        link = args.output_dir / m.digest(args.profile)[:16]
    else:
        link = args.output_dir
    link.symlink_to(target, target_is_directory=True)
    if location == 'ancestor':
        args.output_dir = link / 'not-created' / 'outputs'
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    job = {'artifact': ART}
    with m.Registry(args.state_dir) as reg:
        with pytest.raises(ValueError, match='symlink'):
            m.download(args, data, reg, m.Client('default'), NB, job, {})
        assert not reg.path.exists()
    assert job == {'artifact': ART}
    assert not cloud.calls
    assert not target.exists() if location == 'dangling' else not list(target.iterdir())


@pytest.mark.parametrize('relative', [False, True])
def test_verify_audio_rejects_symlink_ancestry_before_media_reads(tmp_path, monkeypatch, relative):
    m = load()
    real = tmp_path / 'real'
    real.mkdir()
    (real / 'audio.m4a').write_bytes(b'untouched')
    link = tmp_path / 'link'
    link.symlink_to(real, target_is_directory=True)
    path = link / 'audio.m4a'
    if relative:
        monkeypatch.chdir(tmp_path)
        path = Path('link/audio.m4a')
    def unexpected(*args, **kwargs):
        pytest.fail('Unsafe output reached a media subprocess')
    monkeypatch.setattr(m, 'RUN', unexpected)
    with pytest.raises(ValueError, match='unsafe'):
        m.verify_audio(path)
    assert (real / 'audio.m4a').read_bytes() == b'untouched'


def test_inference_requires_every_input_to_have_a_book(tmp_path):
    m = load()
    known = tmp_path / 'content/Books/OT/PRO/01/study.md'
    unknown = tmp_path / 'content/Books/notes.md'
    known.parent.mkdir(parents=True)
    known.write_text('Known')
    unknown.write_text('Unknown')
    with pytest.raises(ValueError, match='infer'):
        m.plan(m.parser().parse_args([str(known), str(unknown)]))


def test_edit_keeps_notebook_and_collection_but_changes_source_job(tmp_path, monkeypatch):
    m = load()
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    argv = setup_job(tmp_path, m)
    assert m.main(argv + ['--allow-upload']) == 2
    Path(argv[0]).write_text('# Revised title\nNew content')
    assert m.main(argv + ['--allow-upload']) == 2
    assert sum(c[3] == 'create' for c in cloud.calls) == 1
    assert sum(c[3:5] == ['collection', 'create'] for c in cloud.calls) == 1
    assert sum(c[3:5] == ['source', 'add'] for c in cloud.calls) == 2
    assert sum(c[3:5] == ['generate', 'audio'] for c in cloud.calls) == 2


def test_uncertain_collection_requires_explicit_bind_even_if_name_appears(tmp_path, monkeypatch):
    m = load()
    cloud = Cloud()
    cloud.fail = ['collection', 'create']
    monkeypatch.setattr(m, 'RUN', cloud)
    argv = setup_job(tmp_path, m)
    assert m.main(argv + ['--allow-upload']) == 1
    cloud.fail = None
    cloud.collections = [{'id': COLLECTION, 'name': 'Proverbs'}]
    assert m.main(argv + ['--allow-upload']) == 1
    assert m.main(argv + ['--bind-collection', COLLECTION]) == 0
    assert m.main(argv + ['--allow-upload']) == 2
    assert sum(c[3:5] == ['collection', 'create'] for c in cloud.calls) == 1


def test_membership_add_timeout_rechecks_before_retry(tmp_path, monkeypatch):
    m = load()
    cloud = Cloud()
    failed = False
    def runner(argv, **kwargs):
        nonlocal failed
        result = cloud(argv, **kwargs)
        if argv[3:5] == ['collection', 'add'] and not failed:
            failed = True
            raise RuntimeError('Lost response after membership was added')
        return result
    monkeypatch.setattr(m, 'RUN', runner)
    argv = setup_job(tmp_path, m)
    assert m.main(argv + ['--allow-upload']) == 1
    assert m.main(argv + ['--allow-upload']) == 2
    assert sum(c[3:5] == ['collection', 'add'] for c in cloud.calls) == 1


@pytest.mark.parametrize('book, name', [('JOL', 'Joel'), ('JUD', 'Jude'), ('PRO', 'Proverbs')])
def test_repository_book_names(tmp_path, book, name):
    m = load()
    argv = setup_job(tmp_path, m)
    data = m.plan(m.parser().parse_args(argv + ['--book', book]))
    assert data['collection_name'] == name
    assert data['notebook_title'] == 'study with spaces'


def legacy_registry(tmp_path, m, argv):
    import json
    data = m.plan(m.parser().parse_args(argv))
    old_plan = {k: data[k] for k in ('profile', 'route', 'hashes', 'settings', 'files')}
    old_key = m.digest({k: old_plan[k] for k in ('profile', 'route', 'hashes', 'settings')})
    old_plan['job'] = old_key
    job = {'plan': old_plan, 'artifact': ART, 'adopted': True,
           'output': str(tmp_path / 'out' / m.digest('default')[:16] / (old_key + '.m4a')),
           'download_started': True, 'verified': {'sha256': 'old-hash'}}
    old = {'profiles': {'default': {'routes': {'book:PRO': {
        'notebook': NB, 'sources': {data['hashes'][0]: {'id': SRC}}, 'jobs': {old_key: job}}}}}}
    path = tmp_path / 'state/registry.json'
    path.parent.mkdir()
    path.write_text(json.dumps(old))
    return data, old_key, old, path


def test_offline_migration_preserves_job_output_and_resume_alias(tmp_path, monkeypatch):
    import json
    m = load()
    argv = setup_job(tmp_path, m)
    data, key, old, path = legacy_registry(tmp_path, m, argv)
    original = path.read_bytes()
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    assert m.main(argv) == 1  # Migration must be explicit.
    assert path.read_bytes() == original
    assert m.main(argv + ['--migrate-state']) == 0
    assert not cloud.calls
    assert (path.parent / 'registry.v1.backup.json').read_bytes() == original
    state = json.loads(path.read_text())
    study = state['profiles']['default']['routes']['book:PRO']['studies'][data['study']]
    assert study['notebook'] == NB
    assert study['jobs'][key] == old['profiles']['default']['routes']['book:PRO']['jobs'][key]
    assert study['job_aliases'][data['job']] == key
    assert m.main(argv + ['--migrate-state']) == 0
    assert m.main(argv) == 2
    assert not any(c[3] in ('create', 'generate') or c[3:5] == ['source', 'add'] for c in cloud.calls)


def test_migration_refuses_unrelated_legacy_studies_without_changes(tmp_path, monkeypatch, capsys):
    import copy
    import json
    m = load()
    argv = setup_job(tmp_path, m)
    _, key, old, path = legacy_registry(tmp_path, m, argv)
    jobs = old['profiles']['default']['routes']['book:PRO']['jobs']
    jobs['other'] = copy.deepcopy(jobs[key])
    jobs['other']['plan']['files'][0]['path'] = str(tmp_path / 'unrelated.md')
    path.write_text(json.dumps(old))
    original = path.read_bytes()
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    assert m.main(argv + ['--migrate-state']) == 1
    assert 'migration' in capsys.readouterr().err.lower()
    assert path.read_bytes() == original
    assert not (path.parent / 'registry.v1.backup.json').exists()
    assert not cloud.calls


@pytest.mark.parametrize('location', ['root', 'ancestor', 'registry.json', 'registry.lock'])
def test_registry_rejects_symlinks(tmp_path, location):
    m = load()
    outside = tmp_path / 'outside'
    outside.mkdir()
    root = tmp_path / 'state'
    if location in ('root', 'ancestor'):
        root.symlink_to(outside, target_is_directory=True)
        if location == 'ancestor':
            root = root / 'nested'
    else:
        root.mkdir()
        (root / location).symlink_to(outside / 'target')
    with pytest.raises(ValueError, match='symlink'):
        with m.Registry(root):
            pass
    assert not list(outside.iterdir())


def test_migrated_completed_job_keeps_output_and_uncertain_state(tmp_path, monkeypatch):
    import json
    m = load()
    argv = setup_job(tmp_path, m)
    data, key, old, path = legacy_registry(tmp_path, m, argv)
    legacy = old['profiles']['default']['routes']['book:PRO']
    legacy['sources'][data['hashes'][0]]['uncertain'] = 'id'
    output = Path(legacy['jobs'][key]['output'])
    output.parent.mkdir(parents=True)
    output.write_bytes(b'owned-audio')
    path.write_text(json.dumps(old))
    cloud = Cloud()
    cloud.completed = True
    monkeypatch.setattr(m, 'RUN', cloud)
    checked = []
    def verify(p):
        checked.append(p)
        return {'sha256': 'old-hash', 'bytes': 11, 'duration_seconds': 1}
    monkeypatch.setattr(m, 'verify_audio', verify)
    assert m.main(argv + ['--migrate-state']) == 0
    assert m.main(argv) == 0
    assert checked == [output]
    migrated = json.loads(path.read_text())['profiles']['default']['routes']['book:PRO']['studies'][data['study']]
    assert migrated['sources'][data['hashes'][0]]['uncertain'] == 'id'
    assert list(migrated['jobs']) == [key]
    assert not any(c[3:5] == ['download', 'audio'] for c in cloud.calls)


def test_migration_never_overwrites_existing_backup(tmp_path, monkeypatch):
    m = load()
    argv = setup_job(tmp_path, m)
    _, _, _, path = legacy_registry(tmp_path, m, argv)
    original = path.read_bytes()
    backup = path.parent / 'registry.v1.backup.json'
    backup.write_bytes(b'irreplaceable')
    cloud = Cloud()
    monkeypatch.setattr(m, 'RUN', cloud)
    assert m.main(argv + ['--migrate-state']) == 1
    assert path.read_bytes() == original
    assert backup.read_bytes() == b'irreplaceable'
    assert not cloud.calls
