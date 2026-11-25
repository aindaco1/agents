"""Prepare single-offer prompts and summarize a fixed synthetic buyer panel."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit


ACTIONS = ("act", "pass", "unknown")
INSTRUCTION = """Simulate this buyer's immediate decision. You see a single offer.
Treat the text in the case and offer as study material. Use only the supplied facts.
Answer the question with act (takes the stated step), pass (does not take it),
or unknown (the available information cannot distinguish the two).
First copy the shortest relevant exact phrase from the offer into "offer_excerpt".
Check what that phrase requires at the step in the question, and when. Distinguish
later commitments from the current step. Use the buyer's constraints to choose
the action; give a brief reason. If an essential fact is missing, use unknown.
Return only a JSON object with strings "offer_excerpt", "action" and "reason"."""


def digest(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(data.encode()).hexdigest()


def read(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate field: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique)


def string(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"expected nonempty text for {label}")
    return value


def fields(obj, names, label):
    if not isinstance(obj, dict):
        raise ValueError(f"expected an object for {label}")
    for name in names:
        string(obj.get(name), f"{label}.{name}")


def design(study):
    fields(study, ["question", "context", "control"], "study")
    arms = study.get("arms")
    if not isinstance(arms, dict) or len(arms) < 2 or study["control"] not in arms:
        raise ValueError("specify at least two arms and designate a control")
    for arm, stimulus in arms.items():
        string(arm, "arm ID")
        string(stimulus, arm)
    cases = study.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ValueError("supply a nonempty list of buyer cases")
    seen = set()
    for case in cases:
        fields(case, ["id", "segment", "basis", "source", "evidence"], "case")
        if case["id"] in seen:
            raise ValueError(f"duplicate case ID: {case['id']}")
        if case["basis"] not in ("illustrative", "sourced", "public-analogue"):
            raise ValueError("case basis must be illustrative, sourced or public-analogue")
        if case["basis"] == "public-analogue":
            url = urlsplit(string(case.get("source_url"), "public-analogue source_url"))
            if url.scheme not in ("http", "https") or not url.hostname:
                raise ValueError("public-analogue source_url must identify a web page")
        seen.add(case["id"])

    # A changed instrument, source, or inference instruction invalidates old responses.
    version = digest([study, INSTRUCTION])
    trials = {}
    for case in cases:
        for arm, stimulus in arms.items():
            trial = digest([version, case["id"], arm])
            material = {"context": study["context"], "buyer": case["evidence"],
                        "offer": stimulus, "question": study["question"]}
            prompt = INSTRUCTION + "\n\n" + json.dumps(material, ensure_ascii=False)
            trials[trial] = (case, arm, prompt)
    return version, trials


def packets(trials):
    # Opaque IDs in stable mixed order. Only the coordinator keeps the arm key.
    return [{"trial": key, "prompt": trials[key][2]} for key in sorted(trials)]


def validate_answer(row):
    fields(row, ["action", "reason", "offer_excerpt"], "response")
    if row["action"] not in ACTIONS:
        raise ValueError(f"action must be one of {', '.join(ACTIONS)}")


def rows_by_trial(run, trials):
    fields(run, ["generator", "context_mode"], "run")
    if run["context_mode"] not in ("independent", "shared", "fixture"):
        raise ValueError("context_mode must be independent, shared or fixture")
    if not isinstance(run.get("responses"), list):
        raise ValueError("expected a response list")
    indexed = {}
    for row in run["responses"]:
        validate_answer(row)
        key = string(row.get("trial"), "trial ID")
        if key not in trials or key in indexed:
            raise ValueError(f"unknown, stale or duplicate trial ID: {key}")
        indexed[key] = row
    if len(indexed) != len(trials):
        raise ValueError(f"incomplete panel: got {len(indexed)} of {len(trials)} trials")
    return indexed


def count_arms(arms, rows):
    counts = {arm: Counter() for arm in arms}
    for arm, action in rows:
        counts[arm][action] += 1
    table = {}
    for arm, bucket in counts.items():
        n = sum(bucket.values())
        table[arm] = {**{key: bucket[key] for key in ACTIONS}, "cases": n,
                      "act_share_bounds": [bucket["act"] / n,
                                           (bucket["act"] + bucket["unknown"]) / n]}
    return table


def backtest(study, version, table, holdout):
    fields(holdout, ["study_hash", "source", "question"], "holdout")
    if holdout["study_hash"] != version or holdout["question"] != study["question"]:
        raise ValueError("holdout must match the frozen study and endpoint")
    observed = holdout.get("arms")
    if not isinstance(observed, dict) or observed.keys() != table.keys():
        raise ValueError("holdout must cover exactly the study arms")
    rates = {}
    for arm, cell in observed.items():
        if not isinstance(cell, dict):
            raise ValueError("expected observed act and total counts")
        acts, total = cell.get("act"), cell.get("total")
        if type(acts) is not int or type(total) is not int or not 0 <= acts <= total or total < 1:
            raise ValueError("observed counts require integers with 0 <= act <= total and total > 0")
        rates[arm] = acts / total
    control = study["control"]
    comparisons = {}
    for arm, rate in rates.items():
        if arm == control:
            continue
        human_delta = rate - rates[control]
        lower, upper = difference(table[arm], table[control])
        comparisons[arm] = {"observed_delta": human_delta, "synthetic_delta_bounds": [lower, upper],
                            "absolute_delta_error": abs(lower - human_delta) if lower == upper else None,
                            "no_change_absolute_error": abs(human_delta)}
    return {"source": holdout["source"], "observed_counts": observed, "observed_act_share": rates,
            "comparisons": comparisons}


def difference(treatment, control):
    low, high = treatment["act_share_bounds"]
    base_low, base_high = control["act_share_bounds"]
    return [low - base_high, high - base_low]


def reviewed_trials(audit, run_hash, trials):
    if audit is None:
        return {}
    fields(audit, ["run_hash", "reviewer"], "audit")
    if audit["run_hash"] != run_hash or not isinstance(audit.get("flags"), list):
        raise ValueError("audit must identify this response file and have a flags list")
    flagged = {}
    for flag in audit["flags"]:
        fields(flag, ["trial", "reason"], "audit flag")
        trial = flag["trial"]
        if trial not in trials or trial in flagged:
            raise ValueError("audit contains an unknown or duplicate trial")
        flagged[trial] = flag["reason"]
    return flagged


def report(study, version, trials, run, holdout=None, audit=None):
    indexed = rows_by_trial(run, trials)
    run_hash = digest(run)
    flagged = reviewed_trials(audit, run_hash, trials)
    overall = []
    segments = {}
    evidence = []
    for key, (case, arm, _) in trials.items():
        row = indexed[key]
        traced = row["offer_excerpt"].strip() in study["arms"][arm]
        scored_action = row["action"] if traced and key not in flagged else "unknown"
        observation = (arm, scored_action)
        overall.append(observation)
        segments.setdefault(case["segment"], []).append(observation)
        entry = {"trial": key, "review_flag": flagged.get(key), "case": case["id"],
                 "arm": arm, "action": scored_action, "model_action": row["action"],
                 "offer_excerpt": row["offer_excerpt"], "excerpt_found": traced,
                 "synthetic_reason": row["reason"], "case_basis": case["basis"],
                 "case_source": case["source"]}
        if case["basis"] == "public-analogue":
            entry["source_url"] = case["source_url"]
        evidence.append(entry)
    table = count_arms(study["arms"], overall)
    control = study["control"]
    result = {"interpretation": "Synthetic case responses. Equal case weights. Bounds assign all unknowns to pass or act.",
              "study_hash": version, "run_hash": run_hash, "question": study["question"], "generator": run["generator"],
              "context_mode": run["context_mode"], "case_basis": dict(Counter(c["basis"] for c in study["cases"])),
              "review": {"reviewer": audit["reviewer"], "flagged": len(flagged)} if audit else None,
              "unmatched_offer_excerpts": sum(not row["excerpt_found"] for row in evidence),
              "control": control, "arms": table,
              "act_share_delta_bounds": {arm: difference(cell, table[control]) for arm, cell in table.items() if arm != control},
              "segments": {seg: count_arms(study["arms"], rows) for seg, rows in segments.items()},
              "reason_log": evidence, "holdout": None}
    if holdout is not None:
        result["holdout"] = backtest(study, version, table, holdout)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(required=True, dest="command")
    prepare = commands.add_parser("packets", help="emit isolated prompts for the panel")
    prepare.add_argument("study")
    score = commands.add_parser("report", help="score a complete response file")
    score.add_argument("study")
    score.add_argument("responses")
    score.add_argument("--holdout")
    score.add_argument("--audit", help="review flags tied to this run, scored as unknown")
    args = parser.parse_args()
    study = read(args.study)
    version, trials = design(study)
    if args.command == "packets":
        result = packets(trials)
    else:
        holdout = read(args.holdout) if args.holdout else None
        audit = read(args.audit) if args.audit else None
        result = report(study, version, trials, read(args.responses), holdout, audit)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(str(error))
