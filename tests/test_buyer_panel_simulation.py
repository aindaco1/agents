"""Check buyer panel provenance and scoring with fixed offline fixtures."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest


SKILL = Path(__file__).resolve().parents[1] / "skills/research/buyer-panel-simulation"
CLI = SKILL / "scripts/panel.py"
spec = importlib.util.spec_from_file_location("buyer_panel", CLI)
panel = importlib.util.module_from_spec(spec)
spec.loader.exec_module(panel)


@pytest.fixture
def study():
    data = json.loads((SKILL / "examples/group-screening.json").read_text())
    data["cases"] = [data["cases"][0], data["cases"][-1]]
    return data


def responses(study, actions):
    version, trials = panel.design(study)
    run = {"generator": "fixed test rows", "context_mode": "fixture",
           "responses": [{"trial": trial, "action": action, "reason": "Test input.",
                          "offer_excerpt": study["arms"][arm]}
                         for (trial, (_, arm, _)), action in zip(trials.items(), actions, strict=True)]}
    return version, trials, run


def test_single_stimulus_packets_are_stable_and_exclude_analyst_information(study):
    _, trials = panel.design(study)
    packets = panel.packets(trials)
    assert packets == panel.packets(panel.design(json.loads(json.dumps(study)))[1])
    for item in packets:
        prompt = item["prompt"]
        assert sum(offer in prompt for offer in study["arms"].values()) == 1
        assert sum(case["evidence"] in prompt for case in study["cases"]) == 1
        assert all(case["source"] not in prompt for case in study["cases"])
        assert all(arm not in prompt for arm in study["arms"])
    assert len({p["trial"] for p in packets}) == 4


def test_report_cli_keeps_unknowns_and_source_links(tmp_path, study):
    _, _, run = responses(study, ["pass", "act", "unknown", "unknown"])
    study_path, run_path = tmp_path / "study.json", tmp_path / "run.json"
    study_path.write_text(json.dumps(study))
    run_path.write_text(json.dumps(run))
    result = json.loads(subprocess.check_output(
        [sys.executable, CLI, "report", study_path, run_path], text=True))
    control, offer = study["arms"]
    assert result["arms"][control]["act_share_bounds"] == [0, 0.5]
    assert result["arms"][offer]["act_share_bounds"] == [0.5, 1]
    assert result["act_share_delta_bounds"][offer] == [0, 1]
    assert result["segments"]["community clubs"][offer]["unknown"] == 1
    assert result["reason_log"][0]["case_source"] == study["cases"][0]["source"]
    assert result["holdout"] is None


def test_holdout_can_show_model_loses_to_no_change(study):
    version, trials, run = responses(study, ["pass", "act", "pass", "act"])
    control, offer = study["arms"]
    observed = {"study_hash": version, "question": study["question"], "source": "synthetic test",
                "arms": {control: {"act": 2, "total": 8}, offer: {"act": 1, "total": 8}}}
    result = panel.report(study, version, trials, run, observed)["holdout"]["comparisons"][offer]
    assert result["observed_delta"] == -0.125
    assert result["no_change_absolute_error"] == 0.125
    assert result["absolute_delta_error"] == 1.125
    run["responses"][1]["action"] = "unknown"
    result = panel.report(study, version, trials, run, observed)["holdout"]["comparisons"][offer]
    assert result["absolute_delta_error"] is None
    for edit in [{"question": "A different endpoint"}, {"study_hash": "stale"},
                 {"arms": {control: {"act": 2, "total": 1}, offer: {"act": 0, "total": 1}}}]:
        with pytest.raises(ValueError):
            panel.report(study, version, trials, run, {**observed, **edit})


@pytest.mark.parametrize("error", ["missing", "duplicate", "stale", "invalid"])
def test_bad_panel_cannot_be_reported(study, error):
    _, _, run = responses(study, ["pass", "act", "pass", "pass"])
    if error == "missing":
        run["responses"].pop()
    if error == "duplicate":
        run["responses"][1] = run["responses"][0].copy()
    if error == "stale":
        study["context"] += " The date changed."
    if error == "invalid":
        run["responses"][0]["action"] = "probably"
    version, trials = panel.design(study)
    with pytest.raises(ValueError):
        panel.report(study, version, trials, run)


def test_excerpt_from_another_offer_is_scored_as_unknown(study):
    version, trials, run = responses(study, ["act", "act", "pass", "pass"])
    run["responses"][0]["offer_excerpt"] = "when you confirm at the end of the hold"
    result = panel.report(study, version, trials, run)
    assert result["unmatched_offer_excerpts"] == 1
    assert result["arms"][study["control"]]["unknown"] == 1
    assert result["reason_log"][0]["model_action"] == "act"
    assert result["reason_log"][0]["action"] == "unknown"

def test_review_withholds_a_contradiction_and_invalidates_stale_flags(study):
    version, trials, run = responses(study, ["act", "act", "pass", "pass"])
    raw = panel.report(study, version, trials, run)
    trial = raw["reason_log"][0]["trial"]
    flag = {"trial": trial, "reason": "Misreads payment timing."}
    audit = {"reviewer": "Test reviewer", "run_hash": raw["run_hash"], "flags": [flag]}
    reviewed = panel.report(study, version, trials, run, audit=audit)
    assert reviewed["reason_log"][0]["model_action"] == "act"
    assert reviewed["reason_log"][0]["review_flag"] == flag["reason"]
    assert reviewed["arms"][study["control"]]["act_share_bounds"] == [0, 0.5]
    with pytest.raises(ValueError):
        panel.report(study, version, trials, run, audit={**audit, "flags": [flag, flag]})
    run["responses"][0]["reason"] += " Revised."
    with pytest.raises(ValueError):
        panel.report(study, version, trials, run, audit=audit)

def test_public_analogue_retains_locator_only_on_analyst_side(study):
    case = study["cases"][0]
    case.update(basis="public-analogue", source="Public minutes, page 2, 2025-01-01",
                source_url="https://example.org/minutes")
    version, trials, run = responses(study, ["unknown", "unknown", "pass", "act"])
    assert all(case["source"] not in p["prompt"] and case["source_url"] not in p["prompt"]
               for p in panel.packets(trials))
    report = panel.report(study, version, trials, run)
    assert report["case_basis"] == {"public-analogue": 1, "illustrative": 1}
    rows = [r for r in report["reason_log"] if r["case"] == case["id"]]
    assert len(rows) == 2
    assert all(r["case_basis"] == "public-analogue" and r["source_url"] == case["source_url"]
               and r["case_source"] == case["source"] for r in rows)
    for bad_url in [None, "a search snippet", "file:///tmp/notes", "https://"]:
        case["source_url"] = bad_url
        with pytest.raises(ValueError, match="source_url"):
            panel.design(study)
