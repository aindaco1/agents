import json
from pathlib import Path
import subprocess
import sys

import pytest

from test_skill_sync import codex_sync, ROOT


def fixture(tmp_path, alias='web-application-builder-persona'):
    repo, dest = tmp_path/'repo', tmp_path/'codex'
    profile = repo/'web-application-builder'
    profile.mkdir(parents=True)
    entry = {'role_id': profile.name, 'codex_skill_name': alias,
             'display_name': 'Marisol', 'role_name': 'Web Application Builder',
             'emoji': '', 'tagline': 'Builds applications',
             'hermes_skills': ['web-application-builder']}
    (profile/'roster_entry.json').write_text(json.dumps(entry))
    (profile/'IDENTITY_SUMMARY.md').write_text('# Marisol\n\nPersona summary.')
    (profile/'IDENTITY.md').write_text('# Marisol\n\nPersona details.')
    procedure = dest/'web-application-builder'
    procedure.mkdir(parents=True)
    (procedure/'SKILL.md').write_text('---\nname: web-application-builder\n---\nProcedure, not persona.')
    (procedure/'private.txt').write_text('Preserve unrelated local material')
    command = [sys.executable, str(ROOT/'scripts/sync_codex_skills.py'), '--repo', str(repo), '--dest', str(dest)]
    return repo, dest, entry, command


def call(command, *args):
    return subprocess.run([*command, *args], capture_output=True, text=True)


def test_alias_publishes_independently_and_rollback_preserves_procedure(tmp_path):
    repo, dest, entry, command = fixture(tmp_path)
    protected = {p.name: p.read_bytes() for p in (dest/entry['role_id']).iterdir()}
    plan = call(command, '--plan')
    assert plan.returncode == 0, plan.stderr
    preview = json.loads(plan.stdout)
    assert preview['preserved_collisions'] == []
    assert [Path(p['root']).name for p in preview['packages']] == [entry['codex_skill_name']]
    result = call(command, '--apply', preview['plan_hash'])
    assert result.returncode == 0, result.stderr
    mirror = dest/entry['codex_skill_name']
    assert 'name: web-application-builder-persona\n' in (mirror/'SKILL.md').read_text()
    assert '- $web-application-builder\n' in (mirror/'SKILL.md').read_text()
    assert '$web-application-builder-persona' in (mirror/'agents/openai.yaml').read_text()
    assert call(command, '--check').returncode == 0
    assert {p.name: p.read_bytes() for p in (dest/entry['role_id']).iterdir()} == protected
    state = dest/'.persona-state'/entry['role_id']
    transaction = json.loads((state/'manifest.json').read_text())['transaction']
    codex_sync.publication.recover(mirror, state, transaction)
    assert not (mirror/'SKILL.md').exists()
    assert {p.name: p.read_bytes() for p in (dest/entry['role_id']).iterdir()} == protected


@pytest.mark.parametrize('alias', ['../escape', '', None, 4, 'x'*64, 'UPPER'])
def test_invalid_alias_fails_before_writes(tmp_path, alias):
    _, dest, _, command = fixture(tmp_path, alias)
    assert call(command, '--plan').returncode != 0
    assert not (dest/'.persona-state').exists()


def test_duplicate_exports_and_procedure_aliases_rejected(tmp_path):
    repo, _, entry, _ = fixture(tmp_path)
    second = dict(entry, role_id='other')
    with pytest.raises(SystemExit, match='Duplicate'):
        codex_sync.validate_export_names(repo, [entry, second])
    skill = repo/'skills/web'/entry['codex_skill_name']
    skill.mkdir(parents=True)
    (skill/'SKILL.md').write_text('Reserved procedure')
    with pytest.raises(SystemExit, match='conflicts with portable'):
        codex_sync.validate_export_names(repo, [entry])


def test_alias_requires_correct_prompt_and_routes_handoffs(tmp_path):
    repo, _, entry, _ = fixture(tmp_path)
    entry['codex_interface'] = {'default_prompt': 'Use $web-application-builder to work.'}
    with pytest.raises(SystemExit, match='must mention'):
        codex_sync.default_openai_yaml(entry)
    entry['handoff_rules'] = {'delegate_to': [{'role_id': entry['role_id'], 'when': 'Implementation'}]}
    body = codex_sync.build_body(repo, entry, {entry['role_id']: entry['codex_skill_name']})
    assert '**web-application-builder-persona**' in body
    assert '- $web-application-builder\n' in body


def test_stale_alias_preview_and_later_rename_fail_closed(tmp_path):
    repo, dest, entry, command = fixture(tmp_path)
    token = json.loads(call(command, '--plan').stdout)['plan_hash']
    summary = repo/entry['role_id']/'IDENTITY_SUMMARY.md'
    summary.write_text('Changed after preview')
    assert 'Stale' in call(command, '--apply', token).stderr
    assert not (dest/entry['codex_skill_name']).exists()
    token = json.loads(call(command, '--plan').stdout)['plan_hash']
    assert call(command, '--apply', token).returncode == 0
    entry['codex_skill_name'] = 'another-persona'
    (repo/entry['role_id']/'roster_entry.json').write_text(json.dumps(entry))
    assert 'separate migration' in call(command, '--plan').stderr
    assert not (dest/'another-persona').exists()


def test_real_web_persona_alias_retains_canonical_role_and_procedure():
    entry = json.loads((ROOT/'web-application-builder/roster_entry.json').read_text())
    assert entry['role_id'] == 'web-application-builder'
    assert entry['codex_skill_name'] == 'web-application-builder-marisol'
    assert entry['hermes_skills'] == ['web-application-builder']
    assert '$web-application-builder-marisol' in codex_sync.default_openai_yaml(entry)


def publish_fixture(command):
    preview = call(command, '--plan')
    assert preview.returncode == 0, preview.stderr
    result = call(command, '--apply', json.loads(preview.stdout)['plan_hash'])
    assert result.returncode == 0, result.stderr


def package_bytes(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}


def test_initial_alias_retirement_new_name_and_rollback_preserve_separate_packages(tmp_path):
    repo, dest, entry, command = fixture(tmp_path)
    publish_fixture(command)
    old = dest/entry['codex_skill_name']
    (old/'private.txt').write_text('Unrelated material stays in its original location')
    old_bytes = package_bytes(old)
    procedure = package_bytes(dest/entry['role_id'])
    state = dest/'.persona-state'/entry['role_id']
    transaction = json.loads((state/'manifest.json').read_text())['transaction']
    journal = json.loads((state/'transactions'/transaction/'journal.json').read_text())
    assert journal['before_manifest'] is None
    assert all(row['before_data'] is None for row in journal['writes'])
    original = dict(entry)
    entry['codex_skill_name'] = 'web-application-builder-marisol'
    (repo/entry['role_id']/'roster_entry.json').write_text(json.dumps(entry))
    assert 'separate migration' in call(command, '--plan').stderr

    codex_sync.publication.recover(old, state, transaction)
    assert package_bytes(old) == {'private.txt': old_bytes['private.txt']}
    publish_fixture(command)
    new = dest/entry['codex_skill_name']
    assert 'name: web-application-builder-marisol\n' in (new/'SKILL.md').read_text()
    assert '- $web-application-builder\n' in (new/'SKILL.md').read_text()
    assert '$web-application-builder-marisol' in (new/'agents/openai.yaml').read_text()
    assert call(command, '--check').returncode == 0
    assert package_bytes(dest/entry['role_id']) == procedure

    current = json.loads((state/'manifest.json').read_text())['transaction']
    codex_sync.publication.recover(new, state, current)
    (repo/entry['role_id']/'roster_entry.json').write_text(json.dumps(original))
    publish_fixture(command)
    assert package_bytes(old) == old_bytes
    assert not (new/'SKILL.md').exists()
    assert package_bytes(dest/entry['role_id']) == procedure


def test_alias_retirement_refuses_later_edits_and_concurrent_writer(tmp_path):
    _, dest, entry, command = fixture(tmp_path)
    publish_fixture(command)
    old = dest/entry['codex_skill_name']
    state = dest/'.persona-state'/entry['role_id']
    transaction = json.loads((state/'manifest.json').read_text())['transaction']
    original = (old/'SKILL.md').read_bytes()
    (old/'SKILL.md').write_bytes(original + b'\nLocal edit\n')
    changed = package_bytes(old)
    with pytest.raises(codex_sync.publication.PublicationError, match='later edit'):
        codex_sync.publication.recover(old, state, transaction)
    assert package_bytes(old) == changed
    (old/'SKILL.md').write_bytes(original)
    with codex_sync.publication.writer_lock(state):
        with pytest.raises(codex_sync.publication.PublicationError, match='Another publisher'):
            codex_sync.publication.recover(old, state, transaction)
    assert (old/'SKILL.md').read_bytes() == original


@pytest.mark.parametrize('failure', ['stale', 'write'])
def test_failed_new_alias_publication_can_restore_old_export(tmp_path, monkeypatch, failure):
    repo, dest, entry, command = fixture(tmp_path)
    publish_fixture(command)
    old = dest/entry['codex_skill_name']
    old_bytes = package_bytes(old)
    procedure = package_bytes(dest/entry['role_id'])
    state = dest/'.persona-state'/entry['role_id']
    transaction = json.loads((state/'manifest.json').read_text())['transaction']
    codex_sync.publication.recover(old, state, transaction)
    original = dict(entry)
    entry['codex_skill_name'] = 'web-application-builder-marisol'
    source = repo/entry['role_id']/'roster_entry.json'
    source.write_text(json.dumps(entry))
    preview = json.loads(call(command, '--plan').stdout)
    new = dest/entry['codex_skill_name']
    if failure == 'stale':
        source.write_text(json.dumps(dict(entry, display_name='Source changed after preview')))
        assert 'Stale' in call(command, '--apply', preview['plan_hash']).stderr
    else:
        plan = preview['packages'][0]
        files = {'SKILL.md': (codex_sync.build_frontmatter(entry) + '\n' +
                             codex_sync.build_body(repo, entry)).encode(),
                 'agents/openai.yaml': codex_sync.default_openai_yaml(entry).encode()}
        real_write = codex_sync.publication.atomic_write
        def fail_metadata(path, data, mode=0o600):
            if path == new/'agents/openai.yaml':
                raise OSError('Synthetic destination failure')
            return real_write(path, data, mode)
        with monkeypatch.context() as patch:
            patch.setattr(codex_sync.publication, 'atomic_write', fail_metadata)
            with pytest.raises(OSError, match='Synthetic'):
                codex_sync.publication.publish(new, state, files, expected=plan['plan_hash'],
                                               source=plan['source'])
    assert not (new/'SKILL.md').exists()
    assert not (state/'pending.json').exists()
    source.write_text(json.dumps(original))
    publish_fixture(command)
    assert package_bytes(old) == old_bytes
    assert package_bytes(dest/entry['role_id']) == procedure
