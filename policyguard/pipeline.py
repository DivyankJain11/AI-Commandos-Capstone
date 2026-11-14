"""Guardrails, then retrieval, then generation. One path for the app and the eval script."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

from policyguard.chunking import Chunk
from policyguard.config import DISCLAIMER
from policyguard.guardrails import screen_question, validate_output
from policyguard.retrieval import Hit, Retriever, is_grounded
from policyguard.textutil import clause_ids

logger = logging.getLogger("policyguard")


@dataclass
class AnswerResult:
    question: str
    redacted_question: str
    answer: str
    refused: bool
    events: list[str] = field(default_factory=list)
    hits: list[Hit] = field(default_factory=list)
    expanded_query: str = ""
    mode: str = "advanced"
    model_kind: str = "base"
    latency_ms: float = 0.0
    model_clause_ids: list[str] = field(default_factory=list)
    disclaimer: str = DISCLAIMER


def _refusal(question: str, decision, mode: str, model_kind: str, started: float, hits=None, expanded: str = "") -> AnswerResult:
    return AnswerResult(
        question=question,
        redacted_question=decision.question,
        answer=decision.refusal_text or "",
        refused=True,
        events=list(decision.events),
        hits=hits or [],
        expanded_query=expanded,
        mode=mode,
        model_kind=model_kind,
        latency_ms=(time.perf_counter() - started) * 1000,
    )


def answer(
    question: str,
    mode: str = "advanced",
    model_kind: str = "base",
    retriever: Retriever | None = None,
    generate: bool = True,
) -> AnswerResult:
    started = time.perf_counter()
    decision = screen_question(question)
    if not decision.allow_model:
        return _refusal(question, decision, mode, model_kind, started)

    owned = retriever is None
    if owned:
        retriever = Retriever()
    assert retriever is not None
    retrieved = retriever.search(decision.question, mode=mode)
    hits = retrieved.hits
    if not hits or not is_grounded(hits[0].dense_score, hits[0].rerank_score, mode):
        decision.allow_model = False
        decision.events.append("low_grounding")
        decision.refusal_text = (
            "The loaded Northwind wordings do not contain a clause close enough to support an answer. "
            "Ask about a cover, an exclusion, a waiting period, or a claims step."
        )
        return _refusal(
            question,
            decision,
            mode,
            model_kind,
            started,
            hits=hits,
            expanded=retrieved.expanded_query,
        )

    if not generate:
        return AnswerResult(
            question=question,
            redacted_question=decision.question,
            answer="",
            refused=False,
            events=list(decision.events),
            hits=hits,
            expanded_query=retrieved.expanded_query,
            mode=mode,
            model_kind=model_kind,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    from policyguard.generation import AdapterNotFoundError, Generator, model_refused

    events = list(decision.events)
    chunks: list[Chunk] = [hit.as_chunk() for hit in hits]
    allowed = {hit.clause_id for hit in hits}
    try:
        draft = Generator.load(model_kind).generate(decision.question, chunks)
    except AdapterNotFoundError:
        raise
    except Exception as exc:
        logger.exception("Generation failed")
        events.append("generation_error")
        return AnswerResult(
            question=question,
            redacted_question=decision.question,
            answer=(
                "The draft could not be produced. Read the retrieved clauses below. "
                f"Do not treat a missing draft as approval. ({type(exc).__name__})"
            ),
            refused=True,
            events=events,
            hits=hits,
            expanded_query=retrieved.expanded_query,
            mode=mode,
            model_kind=model_kind,
            latency_ms=(time.perf_counter() - started) * 1000,
        )

    cleaned, output_events = validate_output(draft, allowed)
    events.extend(output_events)
    refused = model_refused(cleaned)
    cited = [cid for cid in clause_ids(cleaned) if cid in allowed]
    if not refused and not cited:
        events.append("uncited")
    return AnswerResult(
        question=question,
        redacted_question=decision.question,
        answer=cleaned,
        refused=refused,
        events=events,
        hits=hits,
        expanded_query=retrieved.expanded_query,
        mode=mode,
        model_kind=model_kind,
        latency_ms=(time.perf_counter() - started) * 1000,
        model_clause_ids=cited,
    )
