# PolicyGuard

Grounded claims-policy assistant for a retail insurer. A handler asks a cover, exclusion, waiting-period, or claims-process question. The app retrieves the governing clause from the Northwind Assurance wordings and a small local model drafts an answer that cites the clause, or refuses.

This is a proof of concept for the AI Commandos capstone. The wordings are synthetic. Nothing here is an insurance offer or a claim decision.

## Classification

| Rubric field | Choice |
| --- | --- |
| Fine-tuning | LoRA (PEFT) on Flan-T5-small. Not QLoRA: bitsandbytes needs an NVIDIA GPU, and this machine has none. |
| RAG | Advanced: clause-aware chunks, synonym expansion, BM25 + dense hybrid with reciprocal rank fusion, cross-encoder rerank |
| Modality | Text |
| Base model | T5 (`google/flan-t5-small`) |
| Domain | Customer service, insurance claims |
| Vector database | ChromaDB, persisted under `artifacts/chroma` |

Pure prompting is not the method. Retrieval and LoRA are both implemented, so neither category is N/A.

## Business problem

Junior claims handlers and contact-centre agents answer cover questions from long wordings. PDF search misses paraphrases ("cooling-off", "bonus if I never claim", "flood water seized the engine"). A general chatbot invents limits, and those invented limits become commitments to customers.

**Users.** The primary user is the junior handler. The secondary user is the trainer running induction on the same questions. The customer-facing bot is out of scope: the tone, the refusal policy, and the audit trail would be different.

**PoC scope.** English questions over four synthetic wordings (health cover, health exclusions, private car, claims servicing). In scope: cite-or-refuse answers with the clause text beside the draft. Out of scope: real customer records, claim decisioning, bill images, multilingual wording, and production access control.

**Why this is a generative problem, and what else was considered.**

- Keyword search finds a clause only when the handler already knows its words. It misses the paraphrase set in `data/eval/gold.jsonl`.
- A fixed FAQ breaks as soon as the question is not one of the authored pairs, and it does not show the clause the answer came from.
- A rules engine can encode a few limits. It cannot answer an open wording question such as the co-pay exception for a 62-year-old admitted after an accident.
- A prompted general model with no corpus invents sums insured and waiting periods. It is also not a valid submission under the rubric.
- The chosen design retrieves the clause, then asks a small local model to phrase a cite-or-refuse answer. Retrieval carries the fact. LoRA teaches the format. The two failures are measured separately.

**Success targets for the pilot**

- Gold clause in the top 3 on at least 75 percent of answerable held-out questions.
- Unsafe or out-of-scope questions refused, and the blocking event recorded.
- A shown draft either cites a retrieved clause or is an explicit refusal.
- Median response on this CPU laptop reported, not assumed.

Measured numbers are written to `artifacts/metrics.json` by `python -m policyguard.evaluate` and discussed in `docs/evaluation.md` after a run.

## System design

```
handler question
  -> guardrails (block injection, fraud coaching, diagnosis, purchase advice; redact phone, email, PAN, Aadhaar)
  -> synonym expansion (search only)
  -> Chroma dense search + BM25
  -> reciprocal rank fusion
  -> cross-encoder rerank of the top 8, keep 3 distinct clauses
  -> grounding gate
  -> fixed instruction + retrieved clauses + redacted question
  -> Flan-T5-small, base or LoRA
  -> drop any clause id the retriever did not return
  -> draft + clause text + events
```

The full rationale, the error paths, and the hyperparameter record are in `docs/system_design.md`. What to say about each decision in the individual viva is in `docs/viva_notes.md`.

## Project layout

```
app.py                         streamlit entry point
policyguard/                   pipeline, retrieval, LoRA training, evaluation
data/policies/                 synthetic wordings, one clause per heading
data/finetune/train.jsonl      cite-or-refuse pairs. Does not contain eval questions or held-out clauses.
data/eval/gold.jsonl           held-out questions, paraphrases, one reasoning item, refusals, one PII item
tests/                         chunking, guardrails, fusion, and the train/eval split
artifacts/                     index, adapter, train log, metrics. Created by the commands below.
```

Held-out clauses never appear in a training context. The adapter has to learn the cite-or-refuse format on other clauses and apply it to clauses it was not trained on. That split is checked by `tests/test_retrieval.py`.

## Setup

From this folder, in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m policyguard.ingest
.\.venv\Scripts\python.exe -m policyguard.finetune
.\.venv\Scripts\python.exe -m policyguard.evaluate
.\.venv\Scripts\python.exe -m streamlit run app.py
```

The first ingest, training run, and evaluation download three models (MiniLM, a cross-encoder, and Flan-T5-small). Training on CPU is a few epochs over 32 short examples. Expect several minutes, not hours. A GPU is not required.

`python -m policyguard.finetune --max-steps 20` is only a smoke test. The submitted run uses the defaults in `policyguard/config.py` (learning rate 5e-4, 12 epochs). A first run at 1e-4 for 3 epochs did not move the adapter. The loss and the exact hyperparameters are saved to `artifacts/train_log.json`.

Evaluation can be split:

```powershell
.\.venv\Scripts\python.exe -m policyguard.evaluate --retrieval-only
.\.venv\Scripts\python.exe -m policyguard.evaluate --skip-base-generation
```

## Safety

These checks are in `policyguard/guardrails.py` and run before retrieval:

- Prompt-injection phrases are refused. The model is not called.
- Requests to forge a document or falsify a claim are refused. A genuine question about what the fraud clause says is allowed.
- Diagnosis and "which policy should I buy" are refused.
- Phone numbers, email addresses, PAN, and Aadhaar-shaped numbers are replaced with tokens before the question is embedded or generated.
- If the best clause is still a weak match, the app refuses instead of drafting from it.
- If the model names a clause id that was not retrieved, that id is removed from the draft.

The sidebar of the app can switch retrieval from advanced to hybrid to dense, and the generator from the LoRA adapter to the untouched base model. That is the before/after for both adaptation methods.

## Evaluation

`policyguard/evaluate.py` reports:

- Clause hit rate at 3 and MRR for dense, hybrid, and advanced retrieval, overall and by tag. The paraphrase tag is the set that keyword overlap is supposed to miss.
- Guardrail event accuracy, refusal catch rate, and false-refusal rate on the full pipeline.
- With the gold clause pasted into the prompt: citation rate, false-refusal rate, and ROUGE-L, for the base model and the LoRA adapter. This isolates the adapter from retrieval error.
- Median latency.

ROUGE-L is secondary. Several wordings of a correct answer share little surface form, so a low ROUGE-L with the right clause id is still a successful answer. The task metrics are clause hit rate, citation of that clause, and correct refusal.

## Limitations

- The wordings are synthetic and short. A real wording set is longer, amended, and sometimes contradictory across circulars.
- Flan-T5-small will phrase some answers clumsily. It was chosen because it trains and answers on a 12 GB CPU laptop. `GEN_MODEL` in `policyguard/config.py` is the switch to `google/flan-t5-base` when a GPU is available. A 7B chat model does not fit this machine.
- The embedding model and the reranker are general English models, not insurance models.
- Query expansion is a dictionary. It is auditable, and it misses synonyms that were not listed.
- PII detection is a set of regular expressions. It misses names, policy numbers, and unusual formats.
- The train/eval split holds out clauses, which is stricter than holding out questions only, and it also means the training set cannot teach those particular facts. Facts have to come from retrieval at test time.
- No human handler study has been run. The gold set is the authoring set for this PoC, so the next iteration needs questions written by someone who did not write the wordings.

## Next iteration

Move the generator to Flan-T5-base or a small instruct model on a GPU, train on retrieved context rather than gold context, and replace the synonym list with a rewriter only if the dictionary's misses are measured first. Add a handler review sheet for the qualitative sample. Do not put real customer files into the index until access control and retention exist.
