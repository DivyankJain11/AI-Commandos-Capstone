"""Build the clause index: Chroma collection, chunk file, and embedding matrix."""

from __future__ import annotations

from policyguard.indexing import build_index


def main() -> None:
    index = build_index()
    # Smoke check: the vector of a clause should retrieve that same clause.
    sample = index.chunks[0]
    vector = index.embed_query(sample.display())
    top = index.query_dense(vector, 3)
    top_ids = [index.chunks[i].clause_id for i, _ in top]
    print(f"Indexed {len(index.chunks)} clauses with backend={index.backend}.")
    print(f"Self-retrieval of {sample.clause_id}: top3={top_ids}")
    if sample.clause_id not in top_ids:
        raise SystemExit("Self-retrieval failed. The embedding index is not usable.")


if __name__ == "__main__":
    main()
