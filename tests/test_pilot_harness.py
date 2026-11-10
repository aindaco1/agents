import hashlib
import json
import os
from pathlib import Path
import sqlite3
import socket
import sys
import tempfile
import threading
import time

import pytest

from test_skill_sync import ROOT, load_module

harness = load_module('pilot_harness', ROOT/'scripts/pilot_harness.py')


def database(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('CREATE TABLE records (id INTEGER PRIMARY KEY, value)')
    db.execute('INSERT INTO records VALUES (1, ?)', ('private fixture value',))
    db.commit()
    return db


def snap(path, root):
    root.mkdir(mode=0o700)
    return harness.snapshot_database(path, root/'snapshot.sqlite')


def test_committed_wal_change_is_captured_despite_unchanged_main_file(tmp_path):
    path = tmp_path/'protected/state.db'
    db = database(path)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA wal_autocheckpoint=0')
    db.execute('PRAGMA wal_checkpoint(TRUNCATE)')
    raw = path.read_bytes()
    before = snap(path, tmp_path/'before')
    db.execute('UPDATE records SET value=?', (b'\x00\xff binary value',))
    db.commit()
    assert path.read_bytes() == raw  # The old file-hash-only guard misses this.
    after = snap(path, tmp_path/'after')
    result = harness.compare_snapshots(before, after)
    db.close()
    assert result['tables']['records']['added_rows'] == 1
    assert result['tables']['records']['removed_rows'] == 1
    assert not result['unchanged']
    assert 'private fixture' not in json.dumps(result)
    assert (Path(before['snapshot']).stat().st_mode & 0o777) == 0o600


def test_logical_comparison_ignores_pages_but_detects_schema_metadata_and_types(tmp_path):
    path = tmp_path/'state.db'
    db = database(path)
    before = snap(path, tmp_path/'before')
    db.execute('VACUUM')
    same = snap(path, tmp_path/'same')
    assert harness.compare_snapshots(before, same)['unchanged']
    db.execute('PRAGMA user_version=5')
    db.execute('ALTER TABLE records ADD COLUMN extra')
    db.execute('UPDATE records SET value=1, extra=NULL')
    db.commit()
    after = snap(path, tmp_path/'after')
    result = harness.compare_snapshots(before, after)
    assert result['schema_changed'] and result['pragmas_changed']
    db.execute("UPDATE records SET value='1'")
    db.commit()
    typed = snap(path, tmp_path/'typed')
    assert not harness.compare_snapshots(after, typed)['unchanged']
    db.close()


def test_snapshot_missing_created_deleted_corrupt_and_tampered(tmp_path):
    path = tmp_path/'state.db'
    missing = snap(path, tmp_path/'missing')
    database(path).close()
    created = snap(path, tmp_path/'created')
    assert harness.compare_snapshots(missing, created)['existence_changed']
    path.unlink()
    deleted = snap(path, tmp_path/'deleted')
    assert harness.compare_snapshots(created, deleted)['existence_changed']
    Path(created['snapshot']).write_bytes(b'tampered')
    with pytest.raises(harness.PilotError, match='evidence changed'):
        harness.compare_snapshots(created, created)
    path.write_bytes(b'not sqlite')
    with pytest.raises(sqlite3.DatabaseError):
        snap(path, tmp_path/'corrupt')


def test_snapshot_concurrent_writer_is_transactionally_consistent(tmp_path):
    path = tmp_path/'state.db'
    db = database(path)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('INSERT INTO records VALUES (2, ?)', ('private fixture value',))
    db.commit();db.close()
    stop = threading.Event()
    def writer():
        conn = sqlite3.connect(path)
        i = 0
        while not stop.is_set():
            conn.execute('UPDATE records SET value=?', (i,));conn.commit();i += 1
        conn.close()
    thread = threading.Thread(target=writer);thread.start()
    try:
        result = snap(path, tmp_path/'snapshot')
        with sqlite3.connect(result['snapshot']) as check:
            assert check.execute('SELECT count(DISTINCT value) FROM records').fetchone()[0] == 1
    finally:
        stop.set();thread.join(timeout=5)


def test_snapshot_locked_database_has_bounded_failure(tmp_path):
    path = tmp_path/'state.db'
    db = database(path)
    db.execute('BEGIN EXCLUSIVE')
    started = time.monotonic()
    try:
        with pytest.raises((harness.PilotError, sqlite3.OperationalError)):
            harness.snapshot_database(path, tmp_path/'backup.sqlite', timeout=0.03)
    finally:
        db.rollback();db.close()
    assert time.monotonic()-started < 2


def spec_fixture(tmp_path, code='print("offline pilot")'):
    protected, home, work = [tmp_path/n for n in ['protected', 'isolated-home', 'work']]
    home.mkdir();work.mkdir()
    database(protected/'state.db').close()
    (protected/'config.yaml').write_text('Synthetic private configuration')
    probe = "import os,json,pathlib; h=pathlib.Path(os.environ['HERMES_HOME']); print(json.dumps({k:str(h/p) for k,p in {'home':'','root':'','config':'config.yaml','state_db':'state.db','skills':'skills'}.items()}))"
    return {'workspace':str(work),'runtime_home':str(home),'protected_roots':[str(protected)],
            'databases':[str(protected/'state.db')], 'command':[sys.executable,'-c',code],
            'probe_command':[sys.executable,'-c',probe], 'timeout_seconds':3}


def test_preflight_refuses_live_paths_links_and_missing_database_scope(tmp_path):
    spec = spec_fixture(tmp_path)
    output = tmp_path/'audit'
    spec['runtime_home'] = str(tmp_path/'protected')
    with pytest.raises(harness.PilotError, match='overlap'):
        harness.validate_spec(spec, output)
    spec['runtime_home'] = str(tmp_path/'isolated-home')
    link = tmp_path/'isolated-home/leaked-state.db'
    link.symlink_to(tmp_path/'protected/state.db')
    with pytest.raises(harness.PilotError, match='escapes'):
        harness.validate_spec(spec, output)
    link.unlink();os.link(tmp_path/'protected/state.db', link)
    with pytest.raises(harness.PilotError, match='Hard-linked'):
        harness.validate_spec(spec, output)
    link.unlink();spec['databases'] = []
    with pytest.raises(harness.PilotError, match='Declare unique'):
        harness.validate_spec(spec, output)


def test_environment_drops_gateway_and_provider_overrides(tmp_path, monkeypatch):
    monkeypatch.setenv('HERMES_GATEWAY_URL', 'http://live.invalid')
    monkeypatch.setenv('OPENAI_API_KEY', 'synthetic-secret')
    monkeypatch.setenv('PYTHONPATH', '/untrusted')
    env = harness.isolated_environment(tmp_path/'home', tmp_path/'scratch')
    assert not {'HERMES_GATEWAY_URL','OPENAI_API_KEY','PYTHONPATH'} & set(env)
    assert env.get('HOME') == os.environ.get('HOME')


def test_unsupported_isolation_fails_before_payload(tmp_path, monkeypatch):
    spec = spec_fixture(tmp_path)
    monkeypatch.setattr(harness.sys, 'platform', 'unsupported')
    result = harness.run_guarded(spec, tmp_path/'audit')
    assert result['status'] == 'failed' and not result['payload_started']
    assert 'unsandboxed' in result['error']


@pytest.mark.skipif(sys.platform != 'darwin', reason='OS containment canary is macOS-specific')
def test_actual_sandbox_blocks_private_reads_writes_and_gateway_sockets(tmp_path):
    secret = str(tmp_path/'protected/state.db')
    short = tempfile.TemporaryDirectory(prefix='pilot-', dir='/private/tmp')
    socket_path = str(Path(short.name)/'gateway.sock')
    server = socket.socket(socket.AF_UNIX)
    server.bind(socket_path)
    server.listen()
    code = f'''import socket
from pathlib import Path
for mode in ['rb','ab']:
    try:
        with open({secret!r}, mode): pass
    except PermissionError: pass
    else: raise AssertionError('Protected DB access permitted')
try:
    Path({str(tmp_path/'audit/before/000.sqlite')!r}).read_bytes()
except PermissionError: pass
else: raise AssertionError('Private audit snapshot readable by payload')
for family,address in [(socket.AF_INET,('127.0.0.1',443)),(socket.AF_UNIX,{socket_path!r})]:
    s=socket.socket(family)
    try: s.connect(address)
    except PermissionError: pass
    else: raise AssertionError('Local gateway access permitted')
    finally: s.close()
Path('allowed.txt').write_text('workspace write succeeds')
'''
    spec = spec_fixture(tmp_path, code);spec['allow_provider_https'] = True
    try:
        result = harness.run_guarded(spec, tmp_path/'audit')
    finally:
        server.close();short.cleanup()
    assert result['status'] == 'passed', result
    assert all(r['unchanged'] for r in result['databases'])
    assert (tmp_path/'work/allowed.txt').exists()


@pytest.mark.skipif(sys.platform != 'darwin', reason='OS containment canary is macOS-specific')
@pytest.mark.parametrize('kind', ['probe','failure','timeout'])
def test_failed_run_retains_before_after_and_never_accepts(tmp_path, kind):
    spec = spec_fixture(tmp_path)
    if kind == 'probe':
        spec['probe_command'] = [sys.executable,'-c',"import json;print(json.dumps(dict.fromkeys(['home','root','config','state_db','skills'],'/live')))"]
    elif kind == 'failure':
        spec['command'] = [sys.executable,'-c','raise RuntimeError("expected fixture failure")']
    else:
        spec['timeout_seconds'] = 0.2
        spec['command'] = [sys.executable,'-c','import time;time.sleep(60)']
    result = harness.run_guarded(spec, tmp_path/'audit')
    assert result['status'] == 'failed' and 'error' in result
    assert (tmp_path/'audit/before/manifest.json').exists()
    assert (tmp_path/'audit/after/manifest.json').exists()
    assert all(r['unchanged'] for r in result['databases'])
    assert result['payload_started'] is (kind != 'probe')
    with pytest.raises(FileExistsError):
        harness.run_guarded(spec, tmp_path/'audit')


@pytest.mark.skipif(sys.platform != 'darwin', reason='OS containment canary is macOS-specific')
def test_concurrent_runtime_bookkeeping_change_fails_preservation_gate(tmp_path):
    spec = spec_fixture(tmp_path, "from pathlib import Path;import time;Path('started').touch();time.sleep(0.4)")
    def unrelated_writer():
        deadline = time.monotonic()+5
        while not (tmp_path/'work/started').exists() and time.monotonic()<deadline:
            time.sleep(0.01)
        with sqlite3.connect(tmp_path/'protected/state.db') as db:
            db.execute('CREATE TABLE runtime_epoch(epoch INTEGER)')
            db.execute('INSERT INTO runtime_epoch VALUES (226)')
    thread = threading.Thread(target=unrelated_writer);thread.start()
    try:
        result = harness.run_guarded(spec, tmp_path/'audit')
    finally:
        thread.join(timeout=6)
    assert result['exit_code'] == 0
    assert result['status'] == 'failed' and result['preservation_failed']
    assert 'runtime_epoch' in result['databases'][0]['tables']


@pytest.mark.skipif(sys.platform != 'darwin', reason='OS containment canary is macOS-specific')
def test_missing_after_snapshot_fails_and_keeps_before(tmp_path, monkeypatch):
    spec = spec_fixture(tmp_path)
    original = harness.capture
    def capture(databases, output, timeout=10):
        if output.name == 'after':
            raise OSError('Synthetic disk failure')
        return original(databases, output, timeout)
    monkeypatch.setattr(harness, 'capture', capture)
    result = harness.run_guarded(spec, tmp_path/'audit')
    assert result['status'] == 'failed' and 'snapshot_error' in result
    assert (tmp_path/'audit/before/manifest.json').exists()


@pytest.mark.skipif(sys.platform != 'darwin', reason='OS containment canary is macOS-specific')
def test_suite_stops_after_failure_and_reports_success_only_when_all_pass(tmp_path):
    one = tmp_path/'one';one.mkdir()
    two = tmp_path/'two';two.mkdir()
    first = spec_fixture(one, 'raise RuntimeError("fixture failure")')
    second = spec_fixture(two, 'from pathlib import Path;Path("ran").touch()')
    suite = {'runs':[first,second], 'max_runs':2, 'max_seconds':300}
    result = harness.run_suite(suite, tmp_path/'failed-suite')
    assert result['status'] == 'failed' and len(result['runs']) == 1
    assert not (two/'work/ran').exists()
    result = harness.run_suite(dict(suite, runs=[second]), tmp_path/'passed-suite')
    assert result['status'] == 'passed' and (two/'work/ran').exists()


@pytest.mark.skipif(sys.platform != 'darwin', reason='OS containment canary is macOS-specific')
def test_descendants_are_retired_before_snapshot_acceptance(tmp_path):
    code = '''import subprocess,sys
subprocess.Popen([sys.executable,'-c',"import time;from pathlib import Path;time.sleep(0.3);Path('orphan-write').touch()"])
'''
    result = harness.run_guarded(spec_fixture(tmp_path, code), tmp_path/'audit')
    assert result['status'] == 'passed', result
    time.sleep(0.4)
    assert not (tmp_path/'work/orphan-write').exists()
    assert not (tmp_path/'audit/active-process.json').exists()
