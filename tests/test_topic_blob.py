"""Topic routing reads the whole store, not a prefix sample."""

from __future__ import annotations

import json
from pathlib import Path

from coherence_cache.atoms import REVIEW_CHECKED, atom_review_status, is_active, make_atom
from coherence_cache.cli import _topic_blob, set_root


def test_topic_blob_includes_later_atoms_and_skips_rejected(tmp_path: Path) -> None:
    topic_dir = tmp_path / "topics" / "demo"
    topic_dir.mkdir(parents=True)
    atoms = [
        {"text": f"filler claim {i}", "review": {"status": "accepted"}}
        for i in range(25)
    ]
    atoms.append({
        "text": "unique zanzibar sentinel",
        "review": {"status": "accepted"},
        "mentions": [{"name": "Zanzibar", "kind": "place"}],
    })
    atoms.append({
        "text": "rejected zanzibar sentence",
        "review": {"status": "rejected"},
    })
    (topic_dir / "atoms.json").write_text(json.dumps({"atoms": atoms}), encoding="utf-8")
    set_root(tmp_path)
    blob = _topic_blob({
        "id": "demo",
        "title": "Demo",
        "path": "topics/demo",
        "tags": [],
    })
    assert "unique zanzibar sentinel" in blob
    assert "zanzibar" in blob
    assert "rejected zanzibar sentence" not in blob


def test_checked_is_searchable_and_not_coerced_to_accepted() -> None:
    atom = make_atom(
        "Y Combinator ships GBrain as open source software.",
        constraint="fact",
        review_status=REVIEW_CHECKED,
        mentions=[{"name": "Y Combinator", "kind": "org"}],
    )
    assert atom_review_status(atom) == "checked"
    assert is_active(atom)
