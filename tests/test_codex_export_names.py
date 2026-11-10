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
    assert entry['codex_skill_name'] == 'web-application-builder-persona'
    assert entry['hermes_skills'] == ['web-application-builder']
    assert '$web-application-builder-persona' in codex_sync.default_openai_yaml(entry)
