"""Input checks that run before retrieval and before the model.

The generator never sees a question that failed a blocking check. Personal
identifiers are masked first, then the masked text is classified, so a phone
number cannot smuggle an instruction and a log cannot keep the raw number.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from policyguard.config import MAX_QUESTION_CHARS

_INJECTION = re.compile(
    r"(ignore (all |the )?(previous|prior|above) (instructions|rules|prompts)"
    r"|reveal (your |the )?(system|hidden) prompt"
    r"|disregard (the |your )?(rules|instructions)"
    r"|you are now"
    r"|jailbreak"
    r"|do not follow (the |your )?rules"
    r"|<\s*/?\s*system\s*>)",
    re.IGNORECASE,
)
_HARMFUL = re.compile(
    r"(\bforge\b|\bfalsif|fake (a |the )?(document|bill|discharge|claim)"
    r"|how (do i|to|can i) (cheat|defraud|lie on a claim))",
    re.IGNORECASE,
)
_OFF_TOPIC = re.compile(
    r"(\bdiagnos|what disease|what (is|are) wrong with me"
    r"|should i buy|which (policy|insurer|company) is better"
    r"|stock (price|tip)|share price"
    r"|write (me )?(malware|a virus|exploit))",
    re.IGNORECASE,
)
_PII = [
    (re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b"), "[AADHAAR]"),
    (re.compile(r"\b[6-9]\d{9}\b"), "[PHONE]"),
    (re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"), "[PAN]"),
    (re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b"), "[EMAIL]"),
]
_ROLE_PREFIX = re.compile(r"(?i)\b(system|assistant|developer)\s*:")


@dataclass
class GuardrailDecision:
    allow_model: bool
    question: str
    events: list[str] = field(default_factory=list)
    refusal_text: str | None = None


def screen_question(question: str) -> GuardrailDecision:
    raw = (question or "").strip()
    if not raw:
        return GuardrailDecision(False, "", ["empty"], "Enter a question about the loaded policy wordings.")
    if len(raw) > MAX_QUESTION_CHARS:
        return GuardrailDecision(
            False,
            raw[:MAX_QUESTION_CHARS],
            ["too_long"],
            "That question is too long. Ask one cover, exclusion, or claims-process question.",
        )

    redacted = raw
    events: list[str] = []
    for pattern, token in _PII:
        if pattern.search(redacted):
            redacted = pattern.sub(token, redacted)
            if "pii_redacted" not in events:
                events.append("pii_redacted")
    redacted = _ROLE_PREFIX.sub("", redacted).strip()

    if _INJECTION.search(redacted):
        events.append("injection")
        return GuardrailDecision(
            False,
            redacted,
            events,
            "I cannot ignore the assistant rules or reveal hidden prompts. "
            "Ask a question about the policy wording.",
        )
    if _HARMFUL.search(redacted):
        events.append("harmful")
        return GuardrailDecision(
            False,
            redacted,
            events,
            "I cannot help with fraud, forgery, or a false claim. "
            "If you need what the wording says about a genuine claim, ask that instead.",
        )
    if _OFF_TOPIC.search(redacted):
        events.append("off_topic")
        return GuardrailDecision(
            False,
            redacted,
            events,
            "I cannot diagnose symptoms, recommend a purchase, or answer topics outside these wordings. "
            "I can explain a cover, an exclusion, a waiting period, or a claims step.",
        )
    return GuardrailDecision(True, redacted, events, None)


def validate_output(text: str, allowed_clause_ids: set[str]) -> tuple[str, list[str]]:
    """Drop clause ids the retriever did not return, so the model cannot cite a stranger clause."""
    events: list[str] = []
    cleaned = text or ""
    unknown = [cid for cid in dict.fromkeys(re.findall(r"\b[A-Z]{2,3}-\d+\b", cleaned)) if cid not in allowed_clause_ids]
    if unknown:
        events.append("stripped_unknown_citations")
        for cid in unknown:
            cleaned = re.sub(rf"\b{re.escape(cid)}\b", "", cleaned)
        cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    return cleaned, events
