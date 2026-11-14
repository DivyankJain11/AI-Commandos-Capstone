"""Small text helpers shared by retrieval and evaluation."""

import re

_TOKEN = re.compile(r"[a-z0-9]+")
_CLAUSE = re.compile(r"\b([A-Z]{2,3}-\d+)\b")


def tokenize(text: str) -> list[str]:
    return _TOKEN.findall(text.lower())


def clause_ids(text: str) -> list[str]:
    return _CLAUSE.findall(text or "")
