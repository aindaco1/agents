"""Frozen study boundaries and referential integrity; no live runtime or network."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / "skills/creative/writing-craft-library/references"


def test_library_keeps_evaluation_authors_and_text_out_of_development_package():
    corpus = json.loads((ROOT / "docs/writing-craft-pilot/corpus.json").read_text())["sources"]
    development = {str(row["id"]): row for row in corpus if row["split"] == "development"}
    heldout = {str(row["id"]): row for row in corpus if row["split"] == "heldout"}
    assert development and heldout and not development.keys() & heldout.keys()
    assert not {r["author"] for r in development.values()} & {r["author"] for r in heldout.values()}
    sources = json.loads((REFERENCES / "sources.json").read_text())["sources"]
    assert {row["id"] for row in sources} == development.keys()
    for row in sources:
        assert not {"body", "text", "paragraphs", "article_text"} & row.keys()
        assert row["author"] == development[row["id"]]["author"]
        assert row["capture_timestamp"] == development[row["id"]]["wayback_ts"]
        assert row["capture_url"] == development[row["id"]]["wayback_url"]
        assert row["observation"] and row["limitations"] and row["review_scope"]
        assert row["reviewed_paragraphs"] and min(row["reviewed_paragraphs"]) >= 1
        for field in ["capture_sha256", "extracted_body_sha256"]:
            assert re.fullmatch(r"[0-9a-f]{64}", row[field])


def test_cards_resolve_to_sources_and_preserve_task_specific_retrieval():
    sources = {r["id"] for r in json.loads((REFERENCES / "sources.json").read_text())["sources"]}
    cards = json.loads((REFERENCES / "cards.json").read_text())["cards"]
    assert len({r["id"] for r in cards}) == len(cards)
    covered = set()
    for card in cards:
        assert set(card["source_ids"]) <= sources
        covered.update(card["source_ids"])
        content = (REFERENCES / (card["id"] + ".md")).read_text()
        assert all(label in content for label in ["Use when:", "Observed move:", "Apply it:", "Limits:"])
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if not target.startswith("https://"):
                assert (REFERENCES / target).is_file()
    assert covered == sources
    prefixes = {c["id"].split("-", 1)[0] for c in cards}
    cases = json.loads((ROOT / "docs/writing-craft-pilot/cases.json").read_text())["cases"]
    for case in cases:
        assert 1 <= len(case["cards"]) <= 2
        assert set(case["cards"]) <= prefixes


def test_preservation_inputs_are_held_out_and_original_tasks_are_distinct():
    corpus = json.loads((ROOT / "docs/writing-craft-pilot/corpus.json").read_text())["sources"]
    heldout = {str(r["id"]) for r in corpus if r["split"] == "heldout"}
    cases = json.loads((ROOT / "docs/writing-craft-pilot/cases.json").read_text())["cases"]
    assert len({c["id"] for c in cases}) == len(cases)
    for case in cases:
        if case["category"] == "preservation":
            assert case["source_id"] in heldout
        else:
            assert "source_id" not in case
        assert re.fullmatch(r"[0-9a-f]{64}", case["prompt_sha256"])
