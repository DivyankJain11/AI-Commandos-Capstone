"""LoRA fine-tune of Flan-T5-small on cite-or-refuse answers.

The training file is a question split, not a copy of the held-out eval file.
Context is taken from the clause text so the adapter learns the answer format
against the same prompt the app uses at inference. Hyperparameters live in
config.py and are copied into artifacts/train_log.json.
"""

from __future__ import annotations

import argparse
import json
import random

from policyguard.chunking import load_chunks
from policyguard.config import (
    GRAD_ACCUM,
    LEARNING_RATE,
    LORA_ALPHA,
    LORA_DIR,
    LORA_DROPOUT,
    LORA_R,
    LORA_TARGETS,
    MAX_SOURCE_LEN,
    MAX_TARGET_LEN,
    NUM_EPOCHS,
    SEED,
    TRAIN_BATCH,
    TRAIN_LOG_PATH,
    TRAIN_PATH,
)
from policyguard.generation import build_source


def read_jsonl(path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def set_seed(seed: int) -> None:
    random.seed(seed)
    import numpy as np
    import torch

    np.random.seed(seed)
    torch.manual_seed(seed)


def context_map() -> dict[str, str]:
    from policyguard.chunking import format_context

    grouped: dict[str, list] = {}
    for chunk in load_chunks():
        grouped.setdefault(chunk.clause_id, []).append(chunk)
    return {clause_id: format_context(chunks) for clause_id, chunks in grouped.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="LoRA fine-tune Flan-T5 on policy answers")
    parser.add_argument("--epochs", type=float, default=NUM_EPOCHS)
    parser.add_argument("--max-steps", type=int, default=-1)
    parser.add_argument("--learning-rate", type=float, default=LEARNING_RATE)
    args = parser.parse_args()

    set_seed(SEED)
    import torch
    from peft import LoraConfig, TaskType, get_peft_model
    from torch.utils.data import Dataset
    from transformers import (
        AutoModelForSeq2SeqLM,
        AutoTokenizer,
        DataCollatorForSeq2Seq,
        Seq2SeqTrainer,
        Seq2SeqTrainingArguments,
    )

    from policyguard.config import GEN_MODEL

    contexts = context_map()
    records = read_jsonl(TRAIN_PATH)
    tokenizer = AutoTokenizer.from_pretrained(GEN_MODEL)
    features = []
    for record in records:
        missing = [clause_id for clause_id in record["clause_ids"] if clause_id not in contexts]
        if missing:
            raise SystemExit(f"Train row cites unknown clauses: {missing}")
        context = "\n".join(contexts[clause_id] for clause_id in record["clause_ids"])
        source = build_source(record["question"], context)
        encoded = tokenizer(source, truncation=True, max_length=MAX_SOURCE_LEN)
        labels = tokenizer(
            text_target=record["target"],
            truncation=True,
            max_length=MAX_TARGET_LEN,
        )
        features.append(
            {
                "input_ids": encoded["input_ids"],
                "attention_mask": encoded["attention_mask"],
                "labels": labels["input_ids"],
            }
        )

    class PairDataset(Dataset):
        def __len__(self):
            return len(features)

        def __getitem__(self, index):
            return features[index]

    model = AutoModelForSeq2SeqLM.from_pretrained(GEN_MODEL)
    model.config.use_cache = False
    lora = LoraConfig(
        task_type=TaskType.SEQ_2_SEQ_LM,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        target_modules=LORA_TARGETS,
        bias="none",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    LORA_DIR.mkdir(parents=True, exist_ok=True)
    run_dir = LORA_DIR.parent / "lora_runs"
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(run_dir),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=TRAIN_BATCH,
        gradient_accumulation_steps=GRAD_ACCUM,
        learning_rate=args.learning_rate,
        logging_steps=1,
        save_strategy="no",
        predict_with_generate=False,
        fp16=False,
        bf16=False,
        report_to="none",
        seed=SEED,
        dataloader_pin_memory=False,
        dataloader_num_workers=0,
        remove_unused_columns=False,
        use_cpu=not torch.cuda.is_available(),
    )
    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=PairDataset(),
        data_collator=DataCollatorForSeq2Seq(tokenizer, model=model, label_pad_token_id=-100),
    )
    train_result = trainer.train()
    model.save_pretrained(LORA_DIR)
    tokenizer.save_pretrained(LORA_DIR)
    log = {
        "base_model": GEN_MODEL,
        "method": "LoRA",
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "lora_dropout": LORA_DROPOUT,
        "target_modules": LORA_TARGETS,
        "learning_rate": args.learning_rate,
        "epochs": args.epochs,
        "max_steps": args.max_steps,
        "train_batch": TRAIN_BATCH,
        "gradient_accumulation": GRAD_ACCUM,
        "effective_batch": TRAIN_BATCH * GRAD_ACCUM,
        "max_source_len": MAX_SOURCE_LEN,
        "max_target_len": MAX_TARGET_LEN,
        "seed": SEED,
        "train_rows": len(records),
        "answer_rows": sum(1 for row in records if row["kind"] == "answer"),
        "negative_rows": sum(1 for row in records if row["kind"] == "negative"),
        "train_loss": train_result.training_loss,
        "log_history": trainer.state.log_history,
        "why": {
            "r": "Fewer than 40 examples. A higher rank would memorise clause wording.",
            "alpha": "Scale of 4, the usual pairing with rank 8.",
            "targets": "Query and value projections are the standard T5 LoRA targets and stay small enough for CPU.",
            "lr": "5e-4. A first run at 1e-4 for 3 epochs (24 optimizer steps) left the LoRA B matrices near their zero initialisation and the loss did not fall. There are only 32 rows, so the rate has to be high enough to move the adapter.",
            "epochs": "12 epochs. Three epochs were not enough updates for the B matrices to leave zero. Rank stays 8, and the held-out clauses are not in the training contexts, so extra epochs teach the cite-or-refuse format rather than those clauses.",
            "not_qlora": "QLoRA via bitsandbytes needs an NVIDIA GPU. This machine has none, so the adapter is trained in full precision.",
            "not_full_finetune": "Full fine-tuning of even this small model is unnecessary for a format change and is not the rubric baseline.",
        },
    }
    TRAIN_LOG_PATH.write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"Saved adapter to {LORA_DIR}")
    print(f"Train loss: {train_result.training_loss:.4f}")
    print(f"Log: {TRAIN_LOG_PATH}")


if __name__ == "__main__":
    main()
