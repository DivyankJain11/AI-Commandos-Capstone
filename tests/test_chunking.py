from policyguard.chunking import load_chunks


def test_every_policy_file_parses_and_ids_are_unique():
    chunks = load_chunks()
    assert len(chunks) == 40
    assert len({c.clause_id for c in chunks}) == 40
    assert {c.clause_id for c in chunks if c.clause_id.startswith("HP-")} == {f"HP-{i:02d}" for i in range(1, 13)}
    health = next(c for c in chunks if c.clause_id == "HP-01")
    assert health.product == "Health"
    assert health.source == "health_protect.md"
    assert "30 days" in next(c.text for c in chunks if c.clause_id == "HP-02")
