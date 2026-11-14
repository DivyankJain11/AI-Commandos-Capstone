"""Hybrid retrieval: clause chunks, query expansion, BM25, dense search, RRF, rerank.

Query expansion is a fixed synonym list. It improves recall for insurance
paraphrases and it cannot invent a new question the way an LLM rewriter can.
Expansion is applied to the search string and to the reranker. The first run
reranked the handler's raw wording only. On "cooling-off period" the
cross-encoder then preferred the pre-existing-disease clause and pushed the
initial waiting period to rank 2. Scoring the expanded string keeps the
synonym the retriever was trusted with. The generator still sees the
handler's original question, so the draft is about what was asked.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from policyguard.chunking import Chunk
from policyguard.config import (
    BM25_POOL,
    DENSE_MIN,
    DENSE_POOL,
    FINAL_K,
    RERANK_MIN,
    RERANK_POOL,
    RRF_K,
)
from policyguard.textutil import tokenize

# Auditable synonyms. Keys are matched as lowercase substrings of the question.
EXPANSIONS: dict[str, list[str]] = {
    "cooling-off": ["initial waiting period", "illness"],
    "cooling off": ["initial waiting period", "illness"],
    "ped": ["pre-existing disease"],
    "pre-existing": ["pre-existing disease"],
    "pre existing": ["pre-existing disease"],
    "ncb": ["no claim bonus"],
    "no claim bonus": ["NCB"],
    "never claim": ["no claim bonus", "claim-free"],
    "bonus": ["no claim bonus"],
    "idv": ["insured declared value"],
    "zero dep": ["zero depreciation"],
    "nil depreciation": ["zero depreciation"],
    "flood": ["water ingression", "hydrostatic lock", "engine protect"],
    "hydrostatic": ["engine protect", "water ingression"],
    "cashless": ["network hospital", "pre-authorisation"],
    "room rent": ["intensive care unit", "normal room"],
    "icu": ["intensive care unit", "room rent"],
    "maternity": ["caesarean", "newborn"],
    "ambulance": ["road ambulance"],
    "cataract": ["specific disease waiting period"],
    "hernia": ["specific disease waiting period"],
    "tyre": ["tyres", "tubes"],
    "tire": ["tyres"],
    "plastic": ["depreciation", "rubber", "nylon"],
    "bumper": ["plastic parts", "depreciation"],
    "tooth": ["dental", "natural teeth"],
    "co-pay": ["copay", "age"],
    "copay": ["co-pay"],
}


def expand_query(question: str) -> str:
    low = question.lower()
    extra: list[str] = []
    seen: set[str] = set()
    for key, phrases in EXPANSIONS.items():
        if key in low:
            for phrase in phrases:
                token = phrase.lower()
                if token not in seen and token not in low:
                    seen.add(token)
                    extra.append(phrase)
    if not extra:
        return question
    return question + " " + " ".join(extra)


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = RRF_K) -> list[tuple[str, float]]:
    """Cormack RRF. Rank lists are best-first. A document missing from a list simply gets no term from it."""
    scores: dict[str, float] = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda item: item[1], reverse=True)


def is_grounded(dense_score: float, rerank_score: float | None, mode: str) -> bool:
    dense_ok = dense_score >= DENSE_MIN
    if mode == "advanced" and rerank_score is not None:
        return dense_ok or rerank_score >= RERANK_MIN
    return dense_ok


@dataclass
class Hit:
    chunk_id: str
    clause_id: str
    title: str
    text: str
    product: str
    source: str
    score: float
    dense_score: float
    rerank_score: float | None = None
    dense_rank: int | None = None
    bm25_rank: int | None = None

    def as_chunk(self) -> Chunk:
        return Chunk(self.chunk_id, self.clause_id, self.title, self.text, self.product, self.source)


@dataclass
class RetrievalResult:
    hits: list[Hit] = field(default_factory=list)
    expanded_query: str = ""
    mode: str = "advanced"


class Retriever:
    def __init__(self) -> None:
        from policyguard.indexing import Index

        self.index = Index.load()
        self._bm25 = None
        self._tokenized: list[list[str]] | None = None
        self._reranker = None

    def _ensure_bm25(self) -> None:
        if self._bm25 is not None:
            return
        from rank_bm25 import BM25Okapi

        self._tokenized = [tokenize(c.display()) for c in self.index.chunks]
        self._bm25 = BM25Okapi(self._tokenized)

    def _ensure_reranker(self):
        if self._reranker is None:
            from sentence_transformers import CrossEncoder

            from policyguard.config import RERANK_MODEL

            self._reranker = CrossEncoder(RERANK_MODEL)
        return self._reranker

    def search(self, question: str, mode: str = "advanced", k: int = FINAL_K) -> RetrievalResult:
        if mode not in {"dense", "hybrid", "advanced"}:
            raise ValueError(f"Unknown retrieval mode: {mode}")
        expanded = expand_query(question)
        vector = self.index.embed_query(expanded)
        dense_hits = self.index.query_dense(vector, DENSE_POOL)
        dense_rank = {idx: rank for rank, (idx, _score) in enumerate(dense_hits, start=1)}

        order: list[tuple[str, float]]
        bm25_rank: dict[int, int] = {}
        if mode == "dense":
            order = [(self.index.chunks[idx].chunk_id, score) for idx, score in dense_hits]
        else:
            self._ensure_bm25()
            assert self._bm25 is not None
            raw = self._bm25.get_scores(tokenize(expanded))
            ranked_idx = [i for i in sorted(range(len(raw)), key=lambda i: raw[i], reverse=True) if raw[i] > 0][:BM25_POOL]
            bm25_rank = {idx: rank for rank, idx in enumerate(ranked_idx, start=1)}
            dense_ids = [self.index.chunks[idx].chunk_id for idx, _ in dense_hits]
            bm25_ids = [self.index.chunks[idx].chunk_id for idx in ranked_idx]
            order = reciprocal_rank_fusion([dense_ids, bm25_ids], RRF_K)

        id_to_index = {c.chunk_id: i for i, c in enumerate(self.index.chunks)}
        # Drop a second piece of the same clause so the top-k are distinct citations.
        chosen: list[tuple[int, float]] = []
        seen_clauses: set[str] = set()
        for chunk_id, fuse_score in order:
            idx = id_to_index[chunk_id]
            clause_id = self.index.chunks[idx].clause_id
            if clause_id in seen_clauses:
                continue
            seen_clauses.add(clause_id)
            chosen.append((idx, fuse_score))
            if len(chosen) >= RERANK_POOL:
                break

        rerank_scores: dict[int, float] = {}
        if mode == "advanced" and chosen:
            reranker = self._ensure_reranker()
            pairs = [(expanded, self.index.chunks[idx].display()) for idx, _ in chosen]
            scores = reranker.predict(pairs, show_progress_bar=False)
            rerank_scores = {idx: float(score) for (idx, _), score in zip(chosen, scores)}
            chosen.sort(key=lambda item: rerank_scores[item[0]], reverse=True)

        hits: list[Hit] = []
        for idx, fuse_score in chosen[:k]:
            chunk = self.index.chunks[idx]
            hits.append(
                Hit(
                    chunk_id=chunk.chunk_id,
                    clause_id=chunk.clause_id,
                    title=chunk.title,
                    text=chunk.text,
                    product=chunk.product,
                    source=chunk.source,
                    score=float(rerank_scores[idx]) if mode == "advanced" else float(fuse_score),
                    dense_score=self.index.cosine(idx, vector),
                    rerank_score=rerank_scores.get(idx),
                    dense_rank=dense_rank.get(idx),
                    bm25_rank=bm25_rank.get(idx),
                )
            )
        return RetrievalResult(hits=hits, expanded_query=expanded, mode=mode)
