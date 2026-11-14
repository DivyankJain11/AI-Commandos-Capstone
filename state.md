# Project state

Updated 14 November 2026. Owner: Divyank Jain (`DivyankJain11`).

## What this is

PolicyGuard is the AI Commandos capstone proof of concept. A claims handler asks a question about synthetic Northwind Assurance wordings. The app retrieves the governing clause and a local Flan-T5-small model drafts a cite-or-refuse answer.

It is not an insurance offer and not a claim decision.

## Rubric choices

| Field | Choice |
| --- | --- |
| Fine-tuning | LoRA on `google/flan-t5-small` (rank 8, alpha 32, learning rate 5e-4, 12 epochs) |
| RAG | Advanced: clause chunks, synonym expansion, BM25 + dense hybrid, cross-encoder rerank |
| Modality | Text |
| Base model | T5 |
| Domain | Customer service, insurance claims |
| Vector database | ChromaDB, built locally by `python -m policyguard.ingest` |

Both RAG and LoRA are implemented. Neither category is N/A.

## What is in this repository

- `policyguard/` application, retrieval, guardrails, training, and evaluation
- `data/policies/` four synthetic wordings
- `data/finetune/train.jsonl` and `data/eval/gold.jsonl`, with eval clauses held out of training
- `artifacts/lora/` the trained adapter
- `artifacts/metrics.json` and `artifacts/train_log.json`
- `docs/` system design, the measured evaluation, and viva notes
- `tests/` for chunking, guardrails, fusion, and the train/eval split

Not in the repository, on purpose: the virtual environment, the Chroma index, and `artifacts/embeddings.npy`. Those are rebuilt by the setup commands in `README.md`.

## Measured result

From `artifacts/metrics.json`, on this laptop:

- Clause hit rate at 3 is 1.00 for dense, hybrid, and advanced retrieval on the 22 answerable questions.
- With only the gold clause in the prompt, the base model names that clause 14% of the time. The LoRA adapter names it 77% of the time.
- In the full app, where three clauses are shown, the adapter names the gold clause 32% of the time. It often writes the right sentence and then stamps another retrieved clause id.
- All six refusal questions are caught. Injection and fraud coaching never call the model.
- Median full-pipeline latency is about 0.8 seconds for the base model and 3.8 seconds for the adapter.

The reading of those numbers, including the co-pay failure, is in `docs/evaluation.md`.

## How to run

From this folder, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m policyguard.ingest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Training is already done. `python -m policyguard.finetune` repeats it. `python -m policyguard.evaluate` repeats the measurement.

## Still open

- The generator needs to cite the clause the sentence came from when three clauses are in the prompt.
- Questions should be written by someone who did not write the wordings.
- A GPU would allow the same code path on `google/flan-t5-base`.
- The individual viva is `docs/viva_notes.md`. The 40 individual marks are not in the repository; they are the spoken defense.
