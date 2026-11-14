"""Clause-aware chunking.

A claims handler has to cite a clause id. The chunk is therefore the clause,
not a fixed token window. A window would split an exclusion from its exception
and make the citation wrong. Clauses in this corpus are already short. A
clause is split only if it exceeds the character limit, and every piece keeps
the same clause id.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from policyguard.config import POLICY_DIR

_HEADING = re.compile(r"^##\s+([A-Z]{2,3}-\d+)\s+(.+)$")
_SENTENCE = re.compile(r"(?<=[.])\s+")
CHAR_LIMIT = 900


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    clause_id: str
    title: str
    text: str
    product: str
    source: str

    def display(self) -> str:
        return f"[{self.clause_id}] {self.title}. {self.text}"


def _split_long(text: str, limit: int = CHAR_LIMIT) -> list[str]:
    text = " ".join(text.split())
    if len(text) <= limit:
        return [text] if text else []
    sentences = [s.strip() for s in _SENTENCE.split(text) if s.strip()]
    parts: list[str] = []
    current = ""
    for sentence in sentences:
        proposal = f"{current} {sentence}".strip()
        if current and len(proposal) > limit:
            parts.append(current)
            current = sentence
        else:
            current = proposal
    if current:
        parts.append(current)
    return parts


def parse_policy(path: Path) -> list[Chunk]:
    product = "General"
    current_id: str | None = None
    current_title: str | None = None
    buffer: list[str] = []
    chunks: list[Chunk] = []

    def flush() -> None:
        if not current_id or not current_title:
            return
        body = "\n".join(buffer).strip()
        pieces = _split_long(body)
        for index, piece in enumerate(pieces, start=1):
            chunk_id = current_id if len(pieces) == 1 else f"{current_id}#{index}"
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    clause_id=current_id,
                    title=current_title,
                    text=piece,
                    product=product,
                    source=path.name,
                )
            )

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Product:"):
            product = line.split(":", 1)[1].strip() or product
            continue
        heading = _HEADING.match(line.strip())
        if heading:
            flush()
            current_id = heading.group(1)
            current_title = heading.group(2).strip()
            buffer = []
        elif current_id is not None:
            buffer.append(line)
    flush()
    return chunks


def load_chunks(policy_dir: Path = POLICY_DIR) -> list[Chunk]:
    paths = sorted(policy_dir.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No policy files in {policy_dir}")
    chunks: list[Chunk] = []
    for path in paths:
        chunks.extend(parse_policy(path))
    counts: dict[str, int] = {}
    for chunk in chunks:
        counts[chunk.clause_id] = counts.get(chunk.clause_id, 0) + 1
    split_ids = {c.clause_id for c in chunks if "#" in c.chunk_id}
    unexpected = [clause_id for clause_id, count in counts.items() if count > 1 and clause_id not in split_ids]
    if unexpected:
        raise ValueError(f"Duplicate clause ids: {sorted(unexpected)}")
    return chunks


def format_context(chunks: list[Chunk]) -> str:
    return "\n".join(c.display() for c in chunks)
