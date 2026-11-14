import json

from policyguard.chunking import load_chunks
from policyguard.config import DENSE_MIN, EVAL_PATH, RERANK_MIN, TRAIN_PATH
from policyguard.retrieval import expand_query, is_grounded, reciprocal_rank_fusion


def _rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_rrf_promotes_a_document_both_lists_agree_on():
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["a", "c", "d"]])
    assert fused[0][0] == "a"
    assert fused[0][1] > fused[1][1]


def test_grounding_gate():
    assert is_grounded(DENSE_MIN - 0.05, RERANK_MIN - 1, "advanced") is False
    assert is_grounded(DENSE_MIN - 0.05, RERANK_MIN + 1, "advanced") is True
    assert is_grounded(DENSE_MIN + 0.10, RERANK_MIN - 1, "advanced") is True
    assert is_grounded(DENSE_MIN - 0.05, None, "dense") is False
    assert is_grounded(DENSE_MIN + 0.10, None, "dense") is True


def test_cooling_off_expansion_adds_the_waiting_period_terms():
    expanded = expand_query("Is there a cooling-off period for sickness just after the policy starts?")
    assert "initial waiting period" in expanded.lower()


def test_train_clauses_do_not_include_held_out_eval_clauses():
    chunks = {chunk.clause_id for chunk in load_chunks()}
    train = _rows(TRAIN_PATH)
    gold = _rows(EVAL_PATH)
    train_clauses = {clause_id for row in train for clause_id in row["clause_ids"]}
    held_out = {
        clause_id
        for row in gold
        if row["tag"] in {"heldout", "paraphrase", "reasoning", "pii"}
        for clause_id in row["expected_clauses"]
    }
    assert train_clauses.isdisjoint(held_out)
    assert train_clauses <= chunks
    assert held_out <= chunks
    train_questions = {row["question"].strip().lower() for row in train}
    gold_questions = {row["question"].strip().lower() for row in gold}
    assert train_questions.isdisjoint(gold_questions)
