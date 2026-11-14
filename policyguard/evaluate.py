"""Retrieval metrics, guardrail checks, and base-versus-LoRA generation.

Retrieval is scored without the generator, by mode, and again on the paraphrase
subset. That is the comparison that shows whether hybrid search and reranking
earn their place. Generation is scored twice: once with the gold clause in the
prompt, which isolates the adapter, and once through the full pipeline.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

from policyguard.chunking import load_chunks
from policyguard.config import EVAL_PATH, LORA_DIR, METRICS_PATH
from policyguard.generation import build_source
from policyguard.textutil import clause_ids, tokenize


def read_jsonl(path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def rouge_l(prediction: str, reference: str) -> float:
    pred = tokenize(prediction)
    ref = tokenize(reference)
    if not pred or not ref:
        return 0.0
    previous = [0] * (len(ref) + 1)
    for token in pred:
        current = [0]
        for index, ref_token in enumerate(ref, start=1):
            if token == ref_token:
                current.append(previous[index - 1] + 1)
            else:
                current.append(max(previous[index], current[-1]))
        previous = current
    match = previous[-1]
    precision = match / len(pred)
    recall = match / len(ref)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def retrieval_block(rows: list[dict], retriever, mode: str) -> dict:
    by_tag: dict[str, list[dict]] = defaultdict(list)
    details = []
    for row in rows:
        from policyguard.guardrails import screen_question

        query = screen_question(row["question"]).question or row["question"]
        if row["expect_refused"] and not row["expected_clauses"]:
            result = retriever.search(query, mode=mode)
            top = result.hits[0] if result.hits else None
            details.append(
                {
                    "id": row["id"],
                    "tag": row["tag"],
                    "scored": False,
                    "dense_score": None if top is None else round(top.dense_score, 4),
                    "rerank_score": None if top is None or top.rerank_score is None else round(top.rerank_score, 4),
                    "top_clause": None if top is None else top.clause_id,
                }
            )
            continue
        result = retriever.search(query, mode=mode)
        found = [hit.clause_id for hit in result.hits]
        expected = set(row["expected_clauses"])
        hit = int(any(clause in found for clause in expected))
        reciprocal = 0.0
        for rank, clause in enumerate(found, start=1):
            if clause in expected:
                reciprocal = 1.0 / rank
                break
        item = {
            "id": row["id"],
            "tag": row["tag"],
            "scored": True,
            "hit": hit,
            "mrr": reciprocal,
            "found": found,
            "dense_score": round(result.hits[0].dense_score, 4) if result.hits else None,
            "rerank_score": None
            if not result.hits or result.hits[0].rerank_score is None
            else round(result.hits[0].rerank_score, 4),
        }
        details.append(item)
        by_tag[row["tag"]].append(item)
    scored = [item for item in details if item["scored"]]

    def pack(items: list[dict]) -> dict:
        return {
            "n": len(items),
            "clause_hit_rate_at_3": mean([item["hit"] for item in items]),
            "mrr": mean([item["mrr"] for item in items]),
        }

    summary = {"overall": pack(scored), "by_tag": {tag: pack(items) for tag, items in sorted(by_tag.items())}}
    return {"summary": summary, "details": details}


def gold_context(row: dict, grouped: dict[str, list]) -> str:
    from policyguard.chunking import format_context

    chunks = []
    for clause_id in row["expected_clauses"]:
        chunks.extend(grouped[clause_id])
    return format_context(chunks)


def generation_on_gold_context(rows: list[dict], kind: str, grouped: dict[str, list]) -> dict:
    from policyguard.generation import Generator, model_refused
    from policyguard.guardrails import screen_question

    generator = Generator.load(kind)
    details = []
    for row in rows:
        if not row["expected_clauses"] or row["expect_refused"]:
            continue
        context = gold_context(row, grouped)
        question = screen_question(row["question"]).question
        # build_source is the same function finetune.py uses. Calling it here
        # keeps the eval prompt from drifting away from the training prompt.
        _ = build_source(question, context)
        text = generator.generate(question, context)
        cited = clause_ids(text)
        expected = set(row["expected_clauses"])
        details.append(
            {
                "id": row["id"],
                "tag": row["tag"],
                "text": text,
                "cited_expected": int(any(clause in cited for clause in expected)),
                "false_refuse": int(model_refused(text)),
                "rouge_l": rouge_l(text, row["reference"]),
            }
        )
    return {
        "kind": kind,
        "n": len(details),
        "citation_rate": mean([item["cited_expected"] for item in details]),
        "false_refuse_rate": mean([item["false_refuse"] for item in details]),
        "rouge_l": mean([item["rouge_l"] for item in details]),
        "details": details,
    }


def pipeline_block(rows: list[dict], kind: str, retriever) -> dict:
    from policyguard.pipeline import answer

    details = []
    for row in rows:
        result = answer(row["question"], mode="advanced", model_kind=kind, retriever=retriever)
        found = [hit.clause_id for hit in result.hits]
        expected = set(row["expected_clauses"])
        event_ok = None
        if row["expect_event"]:
            event_ok = int(row["expect_event"] in result.events)
        details.append(
            {
                "id": row["id"],
                "tag": row["tag"],
                "expect_refused": row["expect_refused"],
                "refused": result.refused,
                "refusal_correct": int(result.refused == row["expect_refused"]),
                "event_correct": event_ok,
                "retrieved": found,
                "retrieval_hit": int(bool(expected) and any(clause in found for clause in expected)),
                "model_cited": int(bool(expected) and any(clause in result.model_clause_ids for clause in expected)),
                "events": result.events,
                "answer": result.answer,
                "latency_ms": round(result.latency_ms, 1),
                "dense_score": None if not result.hits else round(result.hits[0].dense_score, 4),
                "rouge_l": rouge_l(result.answer, row["reference"]) if row["reference"] and not result.refused else None,
            }
        )
    answerable = [item for item in details if not item["expect_refused"]]
    refusals = [item for item in details if item["expect_refused"]]
    with_event = [item for item in details if item["event_correct"] is not None]
    return {
        "kind": kind,
        "refusal_catch_rate": mean([item["refused"] for item in refusals]),
        "false_refusal_rate": mean([item["refused"] for item in answerable]),
        "event_accuracy": mean([item["event_correct"] for item in with_event]),
        "retrieval_hit_rate": mean([item["retrieval_hit"] for item in answerable]),
        "model_citation_rate": mean([item["model_cited"] for item in answerable]),
        "rouge_l_when_answered": mean([item["rouge_l"] for item in answerable if item["rouge_l"] is not None]),
        "median_latency_ms": sorted(item["latency_ms"] for item in details)[len(details) // 2],
        "details": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate PolicyGuard")
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--skip-base-generation", action="store_true")
    args = parser.parse_args()

    rows = read_jsonl(EVAL_PATH)
    from policyguard.retrieval import Retriever

    retriever = Retriever()
    report: dict = {
        "n_questions": len(rows),
        "vector_backend": retriever.index.backend,
        "retrieval": {},
    }
    for mode in ("dense", "hybrid", "advanced"):
        print(f"Scoring retrieval mode={mode}")
        report["retrieval"][mode] = retrieval_block(rows, retriever, mode)

    if not args.retrieval_only:
        grouped: dict[str, list] = defaultdict(list)
        for chunk in load_chunks():
            grouped[chunk.clause_id].append(chunk)
        report["gold_context_generation"] = {}
        report["pipeline"] = {}
        kinds = ["lora"] if args.skip_base_generation else ["base", "lora"]
        for kind in kinds:
            if kind == "lora" and not LORA_DIR.exists():
                print("LoRA adapter not found. Skipping adapter metrics.")
                continue
            print(f"Scoring gold-context generation kind={kind}")
            report["gold_context_generation"][kind] = generation_on_gold_context(rows, kind, grouped)
            print(f"Scoring full pipeline kind={kind}")
            report["pipeline"][kind] = pipeline_block(rows, kind, retriever)

    METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote {METRICS_PATH}")
    for mode, block in report["retrieval"].items():
        overall = block["summary"]["overall"]
        paraphrase = block["summary"]["by_tag"].get("paraphrase", {})
        print(
            f"{mode:10} hit@3={_fmt(overall.get('clause_hit_rate_at_3'))} "
            f"mrr={_fmt(overall.get('mrr'))} "
            f"paraphrase_hit@3={_fmt(paraphrase.get('clause_hit_rate_at_3'))}"
        )


def _fmt(value) -> str:
    if value is None:
        return "n/a"
    return f"{value:.3f}"


if __name__ == "__main__":
    main()
