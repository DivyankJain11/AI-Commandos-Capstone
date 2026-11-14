"""Flan-T5 generation, with an optional LoRA adapter on the same base model."""

from __future__ import annotations

import gc

from policyguard.chunking import format_context
from policyguard.config import (
    GENERATE_BEAMS,
    GENERATE_MAX_NEW_TOKENS,
    GEN_MODEL,
    LORA_DIR,
    MAX_SOURCE_LEN,
)


def build_source(question: str, context: str) -> str:
    """Training and inference must call this same function."""
    return (
        "Answer the question using only the context. "
        "If the context does not contain the answer, reply exactly: "
        "REFUSE | The clauses do not state an answer to this question. "
        "If it does, answer in one or two sentences and end with Clauses: and the clause id.\n"
        f"Context:\n{context}\n"
        f"Question: {question}"
    )


def model_refused(text: str) -> bool:
    return (text or "").strip().lower().startswith("refuse")


class AdapterNotFoundError(RuntimeError):
    pass


class Generator:
    """Holds one model at a time so a 12 GB CPU machine is not asked to keep two."""

    _current: "Generator | None" = None

    def __init__(self, kind: str):
        if kind not in {"base", "lora"}:
            raise ValueError("kind must be 'base' or 'lora'")
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self.kind = kind
        self.torch = torch
        self.tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL)
        model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL)
        if kind == "lora":
            if not LORA_DIR.exists():
                raise AdapterNotFoundError(
                    "No LoRA adapter found. From the project root run: python -m policyguard.finetune"
                )
            from peft import PeftModel

            model = PeftModel.from_pretrained(model, str(LORA_DIR))
        model.eval()
        model.config.use_cache = True
        self.model = model

    @classmethod
    def load(cls, kind: str) -> "Generator":
        if cls._current is not None and cls._current.kind == kind:
            return cls._current
        if cls._current is not None:
            cls._current.model = None
            cls._current = None
            gc.collect()
        generator = cls(kind)
        cls._current = generator
        return generator

    def generate(self, question: str, chunks) -> str:
        context = format_context(chunks) if not isinstance(chunks, str) else chunks
        source = build_source(question, context)
        inputs = self.tokenizer(
            source,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_SOURCE_LEN,
        )
        with self.torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=GENERATE_MAX_NEW_TOKENS,
                num_beams=GENERATE_BEAMS,
                repetition_penalty=1.15,
                early_stopping=True,
            )
        return self.tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
