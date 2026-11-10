#!/usr/bin/env python3
"""Bounded local pilot execution with private SQLite evidence and macOS isolation.

Snapshots are audit evidence, never inputs to the agent. Tests use synthetic homes.
This is a guard for trusted evaluation commands, not a hostile-code containment VM.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time

import managed_publication as publication


class PilotError(ValueError):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inside(path, root):
    return path == root or root in path.parents


def canonical(path):
    path = Path(path).expanduser().absolute()
    # Resolve OS aliases such as /var, but never accept a symlink supplied as a root.
    if path.is_symlink():
        raise PilotError(f"Symlink root refused: {path}")
    return path.resolve()


def private_directory(path):
    path = canonical(path)
    if any(part in {'Mobile Documents', 'CloudStorage', '.git'} for part in path.parts):
        raise PilotError('Pilot evidence must be outside cloud storage and Git')
    if any((p / '.git').exists() for p in [path, *path.parents]):
        raise PilotError('Pilot evidence must be outside a checkout')
    path.mkdir(parents=True, exist_ok=False, mode=0o700)
    return path


def write_json(path, data):
    publication.atomic_write(path, publication.json_bytes(data))


def quote_identifier(name):
    return '"' + name.replace('"', '""') + '"'


def cell(value):
    if value is None:
        return ['null']
    if isinstance(value, bytes):
        return ['blob', base64.b64encode(value).decode('ascii')]
    if isinstance(value, float):
        return ['real', value.hex()]
    if isinstance(value, int):
        return ['integer', str(value)]
    return ['text', value]


def logical_database(snapshot, deadline=None):
    """Row multisets include types, duplicates and accessible implicit rowids.

    Physical SQLite pages, WAL layout, and query order are not logical identity.
    Schema, application/user version, all tables (including internal/FTS state)
    and row identity are compared; runtime_epoch receives no automatic exemption.
    """
    db = sqlite3.connect(Path(snapshot).as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        if deadline is not None:
            db.set_progress_handler(lambda: int(time.monotonic() > deadline), 1000)
        integrity = [r[0] for r in db.execute('PRAGMA integrity_check')]
        if integrity != ['ok']:
            raise PilotError('SQLite integrity check failed')
        schema = list(db.execute("SELECT type,name,tbl_name,sql FROM sqlite_master ORDER BY type,name"))
        tables = {}
        for kind, name, _, sql in schema:
            if kind != 'table':
                continue
            identifier = quote_identifier(name)
            columns = [r[1] for r in db.execute(f'PRAGMA table_xinfo({identifier})')]
            rowid = next((n for n in ['_rowid_', 'rowid', 'oid'] if n not in {c.lower() for c in columns}), None)
            prefix = ''
            if rowid:
                try:
                    db.execute(f'SELECT {rowid} FROM {identifier} LIMIT 0')
                    prefix = rowid + ','
                except sqlite3.OperationalError:
                    pass
            rows = Counter()
            for row in db.execute(f'SELECT {prefix}* FROM {identifier}'):
                if deadline is not None and time.monotonic() > deadline:
                    raise PilotError('SQLite logical inventory deadline exceeded')
                encoded = json.dumps([cell(v) for v in row], ensure_ascii=True, separators=(',', ':')).encode()
                rows[digest(encoded)] += 1
            tables[name] = {'columns': columns, 'rowid': prefix.rstrip(','),
                            'rows': dict(sorted(rows.items())), 'count': sum(rows.values())}
        return {'schema': schema, 'tables': tables,
                'pragmas': {key: db.execute('PRAGMA ' + key).fetchone()[0]
                            for key in ['user_version', 'application_id', 'encoding']}}
    finally:
        db.close()


def snapshot_database(source, destination, timeout=10):
    source, destination = canonical(source), Path(destination)
    if destination.exists():
        raise PilotError('Snapshot destination already exists')
    if not source.exists():
        return {'source': str(source), 'exists': False}
    if not source.is_file() or source.stat().st_nlink != 1:
        raise PilotError('Database must be an unaliased regular file')
    started = time.monotonic()
    before_inode = (source.stat().st_dev, source.stat().st_ino)
    db = sqlite3.connect(source.as_uri() + '?mode=ro', uri=True, timeout=timeout)
    # Do NOT use immutable=1 on a live source: that would omit committed WAL data.
    target = None
    try:
        fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        target = sqlite3.connect(destination)

        def progress(status, remaining, total):
            if time.monotonic() - started > timeout:
                raise PilotError('SQLite snapshot deadline exceeded')

        db.backup(target, pages=128, progress=progress, sleep=0.01)
    finally:
        if target is not None:
            target.close()
        db.close()
    if before_inode != (source.stat().st_dev, source.stat().st_ino):
        raise PilotError('Database replaced during snapshot')
    logical = logical_database(destination, deadline=started+timeout)
    logical_path = destination.with_suffix('.logical.json')
    write_json(logical_path, logical)
    return {'source': str(source), 'exists': True, 'snapshot': str(destination),
            'sha256': digest(destination.read_bytes()), 'logical': str(logical_path),
            'logical_sha256': digest(logical_path.read_bytes()), 'integrity': 'ok'}


def compare_snapshots(before, after):
    if before['source'] != after['source']:
        raise PilotError('Snapshot source identities differ')
    if before['exists'] != after['exists']:
        return {'unchanged': False, 'existence_changed': True}
    if not before['exists']:
        return {'unchanged': True}
    data = []
    for item in [before, after]:
        snap, logical = Path(item['snapshot']), Path(item['logical'])
        if digest(snap.read_bytes()) != item['sha256'] or digest(logical.read_bytes()) != item['logical_sha256']:
            raise PilotError('Snapshot evidence changed after capture')
        data.append(json.loads(logical.read_text()))
    left, right = data
    differences = {}
    for table in sorted(set(left['tables']) | set(right['tables'])):
        a, b = left['tables'].get(table), right['tables'].get(table)
        if a == b:
            continue
        old, new = Counter((a or {}).get('rows', {})), Counter((b or {}).get('rows', {}))
        differences[table] = {'before_rows': None if a is None else a['count'],
                              'after_rows': None if b is None else b['count'],
                              'removed_rows': sum((old-new).values()),
                              'added_rows': sum((new-old).values())}
    schema_changed = left['schema'] != right['schema']
    pragma_changed = left['pragmas'] != right['pragmas']
    return {'unchanged': not (differences or schema_changed or pragma_changed),
            'schema_changed': schema_changed, 'pragmas_changed': pragma_changed,
            'tables': differences, 'snapshot_bytes_equal': before['sha256'] == after['sha256']}


def capture(databases, output, timeout=10):
    output = private_directory(output)
    records = [snapshot_database(p, output / f'{i:03}.sqlite', timeout)
               for i, p in enumerate(databases)]
    write_json(output / 'manifest.json', records)
    return records


def check_tree(root, credentials):
    for path in root.rglob('*'):
        if path.is_symlink():
            if not inside(path.resolve(), root) and path.resolve() not in credentials:
                raise PilotError(f'Path escapes isolated tree: {path}')
        elif path.is_file() and path.stat().st_nlink != 1:
            raise PilotError(f'Hard-linked input refused: {path}')


def validate_spec(spec, output):
    workspace, home = canonical(spec['workspace']), canonical(spec['runtime_home'])
    roots = [canonical(p) for p in spec['protected_roots']]
    databases = [canonical(p) for p in spec['databases']]
    if not roots or not databases or len(set(databases)) != len(databases):
        raise PilotError('Declare unique protected databases and protected roots')
    if any(not any(inside(p, root) for root in roots) for p in databases):
        raise PilotError('Every database must belong to a protected root')
    paths = [workspace, home, output]
    if any(inside(a, b) or inside(b, a) for i, a in enumerate(paths) for b in paths[i+1:]):
        raise PilotError('Workspace, runtime home and audit output must be separate trees')
    if any(inside(p, r) or inside(r, p) for p in paths for r in roots):
        raise PilotError('Isolated and protected roots overlap')
    if not workspace.is_dir() or not home.is_dir():
        raise PilotError('Prepare synthetic workspace and runtime home first')
    credentials = {canonical(p) for p in spec.get('read_only_credentials', [])}
    if any(p.name not in {'auth.json'} or not p.is_file() for p in credentials):
        raise PilotError('Only explicit auth.json credential references are supported')
    for root in [workspace, home]:
        check_tree(root, credentials)
    for key in ['command', 'probe_command']:
        argv = spec.get(key)
        if not isinstance(argv, list) or not argv or not all(isinstance(v, str) and v for v in argv):
            raise PilotError(f'{key} must be a nonempty argv list')
        if not Path(argv[0]).is_absolute() or not Path(argv[0]).is_file():
            raise PilotError('Use an explicit installed executable; no PATH resolution')
    if Path(spec['command'][0]).resolve() != Path(spec['probe_command'][0]).resolve():
        raise PilotError('Probe and payload must use the same runtime executable')
    if type(spec.get('allow_provider_https', False)) is not bool:
        raise PilotError('allow_provider_https must be a boolean')
    if not isinstance(spec.get('timeout_seconds', 60), (int, float)) or not 0 < spec.get('timeout_seconds', 60) <= 600:
        raise PilotError('Run deadline must be in (0, 600] seconds')
    return workspace, home, roots, databases, credentials


def sandbox_policy(workspace, home, scratch, roots, databases, credentials, https=False):
    if sys.platform != 'darwin' or not Path('/usr/bin/sandbox-exec').is_file():
        raise PilotError('OS isolation unavailable; refusing an unsandboxed pilot')
    q = lambda p: json.dumps(str(p))
    lines = ['(version 1)', '(allow default)', '(deny file-write*)', '(deny network*)']
    lines += [f'(allow file-write* (subpath {q(p)}))' for p in [workspace, home, scratch]]
    lines += ['(allow file-write* (literal "/dev/null"))']
    # Evidence contains private database contents. Only disposable scratch is visible.
    lines += [f'(deny file-read* (subpath {q(scratch.parent)}))',
              f'(allow file-read* (subpath {q(scratch)}))']
    if https:
        lines += ['(allow network-outbound (remote tcp "*:443") (remote udp "*:53"))',
                  '(deny network-outbound (remote ip "localhost:*"))']
    # Unix/local gateway sockets are not permitted by the internet-only allowance.
    private = set(databases)
    for root in roots:
        lines.append(f'(deny file-write* (subpath {q(root)}))')
        private.update(root / n for n in ['profiles', 'memories', 'memories_v2', 'sessions',
                                          'skills', 'rules', 'AGENTS.md', 'state',
                                          'config.yaml', 'config.toml', '.env', 'state.db'])
    for p in private:
        lines.append(f'(deny file-read* (subpath {q(p)}))')
        if p.suffix in {'.db', '.sqlite'}:
            lines += [f'(deny file-read* (literal {q(str(p)+s)}))' for s in ['-wal', '-shm', '-journal']]
    for p in credentials:
        lines.append(f'(allow file-read* (literal {q(p)}))')
    return '\n'.join(lines) + '\n'


def isolated_environment(home, scratch):
    # Retain native HOME without repurposing it. Runtime-specific roots are explicit.
    env = {k: os.environ[k] for k in ['HOME', 'PATH', 'LANG', 'LC_ALL', 'USER', 'LOGNAME', 'SHELL', 'TERM']
           if k in os.environ}
    env.update(HERMES_HOME=str(home), TMPDIR=str(scratch), TMP=str(scratch), TEMP=str(scratch),
               PYTHONDONTWRITEBYTECODE='1', XDG_CACHE_HOME=str(scratch / 'cache'))
    return env


def execute(argv, *, policy, cwd, env, stdout, stderr, timeout):
    with stdout.open('xb') as out, stderr.open('xb') as err:
        os.chmod(stdout, 0o600)
        os.chmod(stderr, 0o600)
        child = subprocess.Popen(['/usr/bin/sandbox-exec', '-f', str(policy), *argv],
                                 cwd=cwd, env=env, stdout=out, stderr=err, start_new_session=True)
        active = stdout.parent/'active-process.json'
        try:
            write_json(active, {'pid': child.pid, 'started_at_unix': time.time(),
                                'argv_sha256': digest(json.dumps(argv).encode())})
            return child.wait(timeout=timeout)
        finally:
            # Also retire descendants when the top-level process exits early.
            try:
                os.killpg(child.pid, signal.SIGTERM)
                time.sleep(0.05)
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.wait()
            active.unlink(missing_ok=True)


def run_guarded(spec, destination):
    output = private_directory(destination)
    report = {'status': 'incomplete', 'started_at_unix': time.time(), 'payload_started': False}
    write_json(output / 'report.json', report)
    before = None
    started = time.monotonic()
    try:
        workspace, home, roots, databases, credentials = validate_spec(spec, output)
        scratch = output / 'scratch'
        scratch.mkdir(mode=0o700)
        policy = output / 'sandbox.sb'
        publication.atomic_write(policy, sandbox_policy(workspace, home, scratch, roots,
            databases, credentials, spec.get('allow_provider_https', False)).encode())
        report['isolation'] = {'backend': 'macOS sandbox-exec', 'runtime_home': str(home),
                               'protected_roots': list(map(str, roots)),
                               'provider_https': spec.get('allow_provider_https', False)}
        write_json(output / 'spec.json', spec)
        before = capture(databases, output / 'before')
        env = isolated_environment(home, scratch)
        code = execute(spec['probe_command'], policy=policy, cwd=workspace, env=env,
                       stdout=output/'probe.stdout', stderr=output/'probe.stderr', timeout=30)
        if code:
            raise PilotError(f'Runtime isolation probe failed: exit {code}')
        resolved = json.loads((output/'probe.stdout').read_text())
        for key in ['home', 'root', 'config', 'state_db', 'skills']:
            if not Path(resolved[key]).is_absolute():
                raise PilotError(f'Runtime {key} path is not absolute')
            path = Path(resolved[key]).resolve()
            if not inside(path, home) or (key in ['home', 'root'] and path != home):
                raise PilotError(f'Runtime resolves {key} outside isolated home')
        report['resolved_runtime'] = resolved
        # Probe must not rewrite a path to escape between validation and payload.
        check_tree(workspace, credentials)
        check_tree(home, credentials)
        report['payload_started'] = True
        write_json(output/'report.json', report)
        report['exit_code'] = execute(spec['command'], policy=policy, cwd=workspace, env=env,
            stdout=output/'stdout.log', stderr=output/'stderr.log', timeout=spec.get('timeout_seconds', 60))
        if report['exit_code']:
            raise PilotError(f"Pilot command failed: exit {report['exit_code']}")
        check_tree(workspace, credentials)
        check_tree(home, credentials)
    except (Exception, KeyboardInterrupt) as exc:
        report['error'] = f'{type(exc).__name__}: {exc}'
    finally:
        if before is not None:
            try:
                after = capture(databases, output/'after')
                report['databases'] = [dict(source=a['source'], **compare_snapshots(a, b))
                                       for a, b in zip(before, after, strict=True)]
                if not all(row['unchanged'] for row in report['databases']):
                    report['preservation_failed'] = True
            except Exception as exc:
                report['snapshot_error'] = f'{type(exc).__name__}: {exc}'
        report['elapsed_seconds'] = round(time.monotonic()-started, 3)
        report['status'] = 'passed' if (report.get('exit_code') == 0 and before is not None
            and not any(k in report for k in ['error', 'snapshot_error', 'preservation_failed'])) else 'failed'
        write_json(output/'report.json', report)
    return report


def run_suite(suite, destination):
    """Every prepared run goes through the guard; failures stop later runs."""
    runs, limit = suite['runs'], suite['max_runs']
    seconds = suite['max_seconds']
    if type(limit) is not int or not 0 < len(runs) <= limit <= 40:
        raise PilotError('Suite requires 1-40 runs within an explicit max_runs')
    if not isinstance(seconds, (int, float)) or not 0 < seconds <= 24000:
        raise PilotError('Suite requires a positive max_seconds <= 24000')
    output = private_directory(destination)
    started = time.monotonic()
    result = {'status': 'incomplete', 'runs': []}
    write_json(output/'suite.json', suite)
    write_json(output/'report.json', result)
    for i, spec in enumerate(runs):
        remaining = seconds-(time.monotonic()-started)
        # Leave room for probe and before/after snapshots (bounded independently).
        reserve = 30 + 20*len(spec['databases'])
        if remaining <= reserve:
            result['error'] = 'Suite deadline leaves insufficient time for audited execution'
            break
        spec = dict(spec, timeout_seconds=min(spec.get('timeout_seconds', 60), remaining-reserve))
        report = run_guarded(spec, output/f'run-{i:03}')
        result['runs'].append({'path':f'run-{i:03}/report.json', 'status':report['status']})
        write_json(output/'report.json', result)
        if report['status'] != 'passed':
            break
    result['status'] = 'passed' if len(result['runs']) == len(runs) and all(
        r['status'] == 'passed' for r in result['runs']) else 'failed'
    result['elapsed_seconds'] = round(time.monotonic()-started, 3)
    write_json(output/'report.json', result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    run = commands.add_parser('run')
    run.add_argument('--spec', type=Path, required=True)
    run.add_argument('--output', type=Path, required=True)
    suite = commands.add_parser('suite')
    suite.add_argument('--spec', type=Path, required=True)
    suite.add_argument('--output', type=Path, required=True)
    snap = commands.add_parser('snapshot')
    snap.add_argument('--database', type=Path, action='append', required=True)
    snap.add_argument('--output', type=Path, required=True)
    compare = commands.add_parser('compare')
    compare.add_argument('--before', type=Path, required=True)
    compare.add_argument('--after', type=Path, required=True)
    args = parser.parse_args()
    if args.action in {'run', 'suite'}:
        # SIGKILL cannot be caught; an incomplete report is never an acceptance.
        signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
        runner = run_suite if args.action == 'suite' else run_guarded
        result = runner(json.loads(args.spec.read_text()), args.output)
        print(json.dumps(result, indent=2))
        return 0 if result['status'] == 'passed' else 1
    if args.action == 'snapshot':
        print(json.dumps(capture(args.database, args.output), indent=2))
        return 0
    before, after = json.loads(args.before.read_text()), json.loads(args.after.read_text())
    if len(before) != len(after):
        raise PilotError('Snapshot sets differ')
    result = [dict(source=a['source'], **compare_snapshots(a, b)) for a, b in zip(before, after, strict=True)]
    print(json.dumps(result, indent=2))
    return 0 if all(r['unchanged'] for r in result) else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, sqlite3.Error) as exc:
        raise SystemExit(str(exc)) from exc
