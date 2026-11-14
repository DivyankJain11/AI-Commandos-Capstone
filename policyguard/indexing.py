"""Persistent Chroma collection plus the vectors used to score hits.

Chroma is the vector database on the query path. Embeddings are computed with
MiniLM and passed in, so Chroma does not download a second ONNX embedder.
The same vectors are stored in embeddings.npy so a cosine score is available
even for a chunk that Chroma did not place in the top pool, and so retrieval
still runs if the Chroma query fails.
"""

from __future__ import annotations

import json
from dataclasses import asdict

import chromadb
import numpy as np
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

from policyguard.chunking import Chunk, load_chunks
from policyguard.config import (
    CHROMA_DIR,
    CHUNKS_PATH,
    COLLECTION_NAME,
    EMBEDDINGS_PATH,
    EMBED_MODEL,
)


class PrecomputedEmbedding(EmbeddingFunction[Documents]):
    """Tells Chroma the vectors were already computed by MiniLM."""

    def __init__(self) -> None:
        return

    def __call__(self, input: Documents) -> Embeddings:
        raise RuntimeError("Pass precomputed embeddings to this collection.")

    @staticmethod
    def name() -> str:
        return "policyguard-precomputed"

    @staticmethod
    def build_from_config(config: dict) -> "PrecomputedEmbedding":
        return PrecomputedEmbedding()

    def get_config(self) -> dict:
        return {}

    def default_space(self) -> str:
        return "cosine"


class IndexNotBuiltError(RuntimeError):
    pass


class Index:
    def __init__(self, chunks: list[Chunk], embeddings: np.ndarray, collection, backend: str):
        self.chunks = chunks
        self.embeddings = embeddings
        self.collection = collection
        self.backend = backend
        self._embedder = None
        self._by_id = {chunk.chunk_id: index for index, chunk in enumerate(chunks)}

    @classmethod
    def load(cls) -> "Index":
        if not CHUNKS_PATH.exists() or not EMBEDDINGS_PATH.exists():
            raise IndexNotBuiltError(
                "The policy index is not built. From the project root run: python -m policyguard.ingest"
            )
        payload = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
        chunks = [Chunk(**row) for row in payload]
        embeddings = np.load(EMBEDDINGS_PATH)
        collection, backend = _open_collection()
        return cls(chunks, embeddings, collection, backend)

    def embed_query(self, text: str) -> np.ndarray:
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer

            self._embedder = SentenceTransformer(EMBED_MODEL)
        vector = self._embedder.encode([text], normalize_embeddings=True)[0]
        return np.asarray(vector, dtype=np.float32)

    def cosine(self, chunk_index: int, vector: np.ndarray) -> float:
        return float(np.dot(self.embeddings[chunk_index], vector))

    def query_dense(self, vector: np.ndarray, k: int) -> list[tuple[int, float]]:
        k = min(k, len(self.chunks))
        if self.collection is not None:
            try:
                result = self.collection.query(
                    query_embeddings=[vector.tolist()],
                    n_results=k,
                    include=["distances"],
                )
                ranked: list[tuple[int, float]] = []
                for chunk_id, distance in zip(result["ids"][0], result["distances"][0]):
                    index = self._by_id[chunk_id]
                    # Prefer the local cosine. It uses the same normalised vectors
                    # the collection was built with, and it does not depend on
                    # whether Chroma returns a distance or a similarity.
                    ranked.append((index, self.cosine(index, vector)))
                if ranked:
                    ranked.sort(key=lambda item: item[1], reverse=True)
                    return ranked
            except Exception as exc:
                print(f"Chroma query failed ({exc}). Using the local cosine index.")
        scores = self.embeddings @ vector
        order = np.argsort(-scores)[:k]
        return [(int(index), float(scores[index])) for index in order]


def _open_collection():
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
            embedding_function=PrecomputedEmbedding(),
        )
        return collection, "chromadb"
    except Exception as exc:
        print(f"Chroma is unavailable ({exc}). Dense search will use the local cosine index.")
        return None, "numpy-cosine"


def _embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)


def build_index() -> Index:
    chunks = load_chunks()
    model = _embedder()
    vectors = model.encode(
        [chunk.display() for chunk in chunks],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    embeddings = np.asarray(vectors, dtype=np.float32)

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    # Rebuild from scratch so a changed clause cannot linger in the collection.
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
            embedding_function=PrecomputedEmbedding(),
        )
        collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.display() for chunk in chunks],
            metadatas=[
                {
                    "clause_id": chunk.clause_id,
                    "title": chunk.title,
                    "product": chunk.product,
                    "source": chunk.source,
                }
                for chunk in chunks
            ],
            embeddings=embeddings.tolist(),
        )
        backend = "chromadb"
    except Exception as exc:
        print(f"Could not write the Chroma collection ({exc}). Saved the local cosine index only.")
        collection = None
        backend = "numpy-cosine"

    ARTIFACTS_PARENT = CHUNKS_PATH.parent
    ARTIFACTS_PARENT.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(
        json.dumps([asdict(chunk) for chunk in chunks], indent=2),
        encoding="utf-8",
    )
    np.save(EMBEDDINGS_PATH, embeddings)
    index = Index(chunks, embeddings, collection, backend)
    index._embedder = model
    return index
