#!/usr/bin/env python3
"""Prepare and validate local review inputs; never execute a model or apply a proposal."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from managed_publication import atomic_write, digest, json_bytes, safe_path


def prepare(records: list[Path], output: Path, *, scope: str, repository: Path,
            max_input_tokens: int, max_cost_usd: float, max_seconds: int) -> dict:
    if not 1 <= len(records) <= 10 or len(set(records)) != len(records):
        raise ValueError("Select one to ten distinct task records")
    if max_input_tokens < 1 or not math.isfinite(max_cost_usd) or max_cost_usd < 0 or not 1 <= max_seconds <= 1200:
        raise ValueError("Set positive token/time bounds, nonnegative cost, and at most 1200 seconds")
    repository = repository.resolve(strict=True)
    rows, inputs, ids = [], {}, set()
    for path in records:
        path = path.absolute()
        raw = safe_path(path.parent, path.name).read_bytes()
        record = json.loads(raw)
        for key in ("id", "session_id", "scope", "runtime", "outcome"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                raise ValueError(f"Missing task field: {key}")
        if record["id"] in ids or record["scope"] != scope or record.get("status") != "complete":
            raise ValueError("Task IDs must be unique, complete, and in the selected scope")
        if not isinstance(record.get("evidence"), list) or not record["evidence"]:
            raise ValueError("Completed tasks require evidence")
        ids.add(record["id"])
        inputs[str(path)] = {"sha256": digest(raw), "bytes": len(raw)}
        for evidence in record["evidence"]:
            p = Path(evidence["path"])
            if not p.is_absolute():
                raise ValueError("Evidence paths must be absolute")
            data = safe_path(p.parent, p.name).read_bytes()
            if digest(data) != evidence["sha256"]:
                raise ValueError(f"Evidence hash mismatch: {p}")
            inputs[str(p)] = {"sha256": digest(data), "bytes": len(data)}
        rows.append(record)
    if sum(x["bytes"] for x in inputs.values()) > 4 * max_input_tokens:
        raise ValueError("Evidence exceeds the batch byte ceiling; select smaller relevant excerpts")
    result = {"schema": 1, "scope": scope, "repository": str(repository), "records": rows,
              "inputs": inputs, "limits": {"max_tasks": 10, "max_proposals": 3,
              "max_input_tokens": max_input_tokens, "max_cost_usd": max_cost_usd,
              "max_seconds": max_seconds}, "execution": "not-started"}
    result["batch_hash"] = digest(json_bytes(result))
    safe_path(output)
    output.mkdir(parents=True, mode=0o700, exist_ok=False)
    atomic_write(output / "batch.json", json_bytes(result))
    return {"batch": str(output / "batch.json"), "batch_hash": result["batch_hash"], "tasks": len(rows)}


def validate(batch: Path, proposals: Path) -> dict:
    manifest = json.loads((batch / "batch.json").read_text())
    expected_hash = manifest.pop("batch_hash")
    if digest(json_bytes(manifest)) != expected_hash:
        raise ValueError("Batch manifest changed after preparation")
    for name, info in manifest["inputs"].items():
        path = Path(name)
        if digest(safe_path(path.parent, path.name).read_bytes()) != info["sha256"]:
            raise ValueError(f"Review input changed: {path}")
    document = json.loads(proposals.read_text())
    rows = document.get("proposals")
    if not isinstance(rows, list) or len(rows) > manifest["limits"]["max_proposals"]:
        raise ValueError("Review must contain at most three proposals")
    records = {r["id"]: r for r in manifest["records"]}
    repository = Path(manifest["repository"])
    seen = set()
    for row in rows:
        for key in ("id", "claim", "kind", "change", "target", "validation", "rollback", "recheck", "uncertainty"):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError(f"Missing proposal field: {key}")
        if row["id"] in seen:
            raise ValueError("Duplicate proposal ID")
        seen.add(row["id"])
        if row["kind"] not in {"code", "test", "configuration", "procedure", "fact", "user-preference"}:
            raise ValueError("Unknown proposal kind")
        ids = row.get("evidence_ids")
        if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or set(ids) - set(records):
            raise ValueError("Proposal must cite distinct selected task IDs")
        evidence = [records[i] for i in ids]
        independent = len({r["session_id"] for r in evidence}) >= 2
        defect = any(r.get("confirmed_defect") is True for r in evidence)
        preference = row["kind"] == "user-preference" and any(r.get("explicit_user_instruction") is True for r in evidence)
        if not (independent or defect or preference):
            raise ValueError("Insufficient independent evidence for a generalized proposal")
        target = Path(row["target"])
        if not target.is_absolute() or not target.is_relative_to(repository):
            raise ValueError("Proposal target is outside the selected repository")
        relative = target.relative_to(repository)
        if any(p.startswith(".") for p in relative.parts):
            raise ValueError("Hidden/runtime targets are outside the proposal scope")
        target = safe_path(repository, str(relative))
        actual = digest(target.read_bytes()) if target.exists() else None
        if "target_sha256" not in row or actual != row["target_sha256"]:
            raise ValueError("Proposal target changed after review")
    return {"status": "validated-proposals-only", "proposals": len(rows),
            "batch_hash": expected_hash, "published": False, "model_calls": 0}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("prepare")
    prep.add_argument("--scope", required=True)
    prep.add_argument("--repository", type=Path, required=True)
    prep.add_argument("--record", type=Path, action="append", required=True)
    prep.add_argument("--output", type=Path, required=True)
    prep.add_argument("--max-input-tokens", type=int, required=True)
    prep.add_argument("--max-cost-usd", type=float, required=True)
    prep.add_argument("--max-seconds", type=int, required=True)
    check = sub.add_parser("validate")
    check.add_argument("--batch", type=Path, required=True)
    check.add_argument("--proposals", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.record, args.output, scope=args.scope, repository=args.repository,
                         max_input_tokens=args.max_input_tokens, max_cost_usd=args.max_cost_usd,
                         max_seconds=args.max_seconds)
    else:
        result = validate(args.batch, args.proposals)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit(str(exc)) from exc
