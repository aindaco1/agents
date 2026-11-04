import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import learning_review as review


def fixture(tmp_path, *, defect=True):
    evidence = tmp_path / "tests.txt"
    evidence.write_text("A real test result in an isolated fixture")
    record = tmp_path / "record.json"
    record.write_text(json.dumps({"id": "one", "session_id": "s1", "scope": "test", "runtime": "codex",
        "outcome": "preserve runtime", "status": "complete", "confirmed_defect": defect,
        "evidence": [{"path": str(evidence), "sha256": review.digest(evidence.read_bytes())}]}))
    repo = tmp_path / "repo"
    repo.mkdir()
    target = repo / "test.py"
    target.write_text("old")
    batch = tmp_path / "batch"
    review.prepare([record], batch, scope="test", repository=repo,
                   max_input_tokens=24000, max_cost_usd=0, max_seconds=1200)
    proposal = {"id": "fix", "claim": "confirmed failure", "kind": "test", "change": "add regression",
        "evidence_ids": ["one"], "target": str(target), "target_sha256": review.digest(target.read_bytes()),
        "validation": "run regression", "rollback": "git revert", "recheck": "compiler changes", "uncertainty": "fixture only"}
    proposals = tmp_path / "proposals.json"
    proposals.write_text(json.dumps({"proposals": [proposal]}))
    return evidence, target, batch, proposals, proposal


def test_verified_defect_and_no_change_are_proposal_only(tmp_path):
    evidence, target, batch, proposals, _ = fixture(tmp_path)
    before = target.read_bytes()
    result = review.validate(batch, proposals)
    assert result["published"] is False and result["model_calls"] == 0
    assert target.read_bytes() == before
    proposals.write_text('{"proposals": []}')
    assert review.validate(batch, proposals)["proposals"] == 0


@pytest.mark.parametrize("which", ["evidence", "target"])
def test_changed_evidence_or_target_cannot_be_promoted(tmp_path, which):
    evidence, target, batch, proposals, _ = fixture(tmp_path)
    (evidence if which == "evidence" else target).write_text("new data")
    with pytest.raises(ValueError, match="changed"):
        review.validate(batch, proposals)


def test_single_unconfirmed_session_is_not_generalized(tmp_path):
    _, _, batch, proposals, _ = fixture(tmp_path, defect=False)
    with pytest.raises(ValueError, match="Insufficient"):
        review.validate(batch, proposals)


def test_out_of_scope_target_and_excessive_batch_refused(tmp_path):
    _, _, batch, proposals, proposal = fixture(tmp_path)
    proposal["target"] = str(tmp_path / "outside.md")
    proposal["target_sha256"] = None
    proposals.write_text(json.dumps({"proposals": [proposal]}))
    with pytest.raises(ValueError, match="outside"):
        review.validate(batch, proposals)
    with pytest.raises(ValueError, match="one to ten"):
        review.prepare([], tmp_path / "empty", scope="test", repository=tmp_path,
                       max_input_tokens=24000, max_cost_usd=0, max_seconds=1200)
