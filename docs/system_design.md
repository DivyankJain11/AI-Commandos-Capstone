# System design

## What the system is

PolicyGuard answers a handler's question from four synthetic Northwind Assurance wordings. It will not answer from model memory. The clause text is always shown next to the draft, and a draft that names a clause the retriever did not return has that id removed.

## Components

| Piece | Choice | Why this and not the neighbour |
| --- | --- | --- |
| Generator | `google/flan-t5-small` | Runs and fine-tunes on a 12 GB CPU laptop with no NVIDIA GPU. Flan-T5-base is the same code path and a better writer, and it is too slow here. A 7B Llama does not fit. An API model would hide the training loop and send questions off the machine. |
| Adaptation | LoRA, rank 8, alpha 32, dropout 0.05, targets `q` and `v` | The rubric baseline is PEFT, not full fine-tuning. QLoRA needs bitsandbytes on NVIDIA. Rank 8 is small because there are 32 training rows; a larger rank memorizes them. |
| Embeddings | `all-MiniLM-L6-v2` | About 80 MB, fast on CPU, strong enough for short clauses. A domain encoder would need in-domain pairs we do not have. |
| Vector store | ChromaDB, cosine space, precomputed vectors | Local and persistent, and it is one of the stores named in the rubric. Vectors are computed once by MiniLM and stored, so Chroma does not download a second embedder. |
| Sparse leg | BM25 (`rank-bm25`) | Exact sums, "1500cc", and "Rs 2,000" are the kind of token a bi-encoder blurs. |
| Fusion | Reciprocal rank fusion, k = 60 | Dense scores and BM25 scores are not on the same scale. RRF combines ranks and needs no weight search. k = 60 is the published default. |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` on the top 8 | A cross-encoder reads the question and the clause together, which matters for exceptions ("waived for accidental injury"). Scoring all 40 clauses on every question is unnecessary on this corpus and wastes CPU. Eight is the pool. |
| Expansion | Fixed synonym dictionary, used for search and for reranking | Auditable. An LLM rewriter can change the question. The generator still sees the handler's original words. The reranker sees the expanded string because a raw-question rerank demoted the cooling-off clause that the synonyms had found. |
| Chunks | One chunk per clause | The citation unit is the clause id. A 512-token window would separate an exclusion from its exception. These clauses are already shorter than that window, so splitting would not help. |
| UI | Streamlit | One screen, a settings sidebar, and the clause text under the draft. Enough for a handler demo. |

## Data flow

1. The question is screened. Empty, over-long, injection, fraud coaching, diagnosis, and purchase advice stop here. The model is not called.
2. Phone, email, PAN, and Aadhaar-shaped numbers are replaced with tokens. Later stages see the tokens.
3. Role prefixes such as `system:` are stripped so a user cannot append a fake instruction channel. The instruction text is a constant in `build_source` and is not taken from the user.
4. The search string is the redacted question plus any dictionary synonyms. The reranker scores that same string. The generator is given the redacted question without the added synonyms.
5. Chroma returns the nearest clauses. BM25 returns its own top 10. RRF merges the two lists.
6. The cross-encoder reranks the best 8 distinct clauses. The app keeps 3.
7. The grounding gate refuses when the top dense score and the rerank score are both weak. The thresholds live in `policyguard/config.py` and are set from the score table produced by evaluation, not by guesswork alone.
8. `build_source` builds the prompt from a fixed instruction, the three clauses, and the redacted question. Training uses this same function.
9. Flan-T5-small generates up to 80 tokens with beam size 2. Beam search is there so the clause id is less likely to be dropped mid-sentence.
10. Any clause id in the draft that was not in the three retrieved clauses is deleted.

## LoRA data

`data/finetune/train.jsonl` has 26 answer rows and 6 negative rows. Each row points at clause ids. The trainer fills the context from the wording, so the clause text exists in one place.

Negative rows pair an off-topic question with a real but irrelevant clause and the target `REFUSE | The clauses do not state an answer to this question.` The adapter learns to refuse when the supplied clause does not answer the question, which is a different skill from the keyword guardrail.

The eval clauses (initial waiting period, pre-existing disease, cataract, room rent, day care, maternity, ambulance, the exception clauses, no-claim bonus, tyres, engine protect, intimation, reimbursement documents, co-pay, plastic depreciation) are not training contexts. The test checks this.

## Error handling

| Failure | What the user sees |
| --- | --- |
| Index not built | The command to run `python -m policyguard.ingest`. No traceback. |
| LoRA selected but not trained | The command to run `python -m policyguard.finetune`. |
| Chroma query throws | Dense search falls back to the saved cosine matrix. The index records which backend answered. |
| Model fails mid-generation | A refusal that says the draft failed, plus the retrieved clauses. A missing draft is not treated as a yes. |
| Weak retrieval | Refusal. The weak clauses can still be inspected. |
| Output names an unknown clause | That id is removed and the event `stripped_unknown_citations` is recorded. |

## Hyperparameters

Recorded again at train time into `artifacts/train_log.json`.

| Value | Setting | Reason |
| --- | --- | --- |
| Rank | 8 | Thirty-two rows. Higher rank memorizes. |
| Alpha | 32 | Scale of 4 on rank 8. |
| Dropout | 0.05 | Light regularisation on a small set. |
| Targets | `q`, `v` | Standard T5 attention targets. Small enough for CPU. |
| Learning rate | 5e-4 | A first run at 1e-4 for 3 epochs did not move the LoRA B matrices off their zero start, and the loss did not fall. 32 rows need a higher rate. |
| Epochs | 12 | Three epochs were 24 optimizer steps, which was not enough. Rank stays 8, and held-out clauses are not in the training file, so the extra epochs are for the cite-or-refuse format. |
| Batch | 1, accumulation 4 | Effective batch 4. Fits CPU memory. |
| Source / target length | 384 / 96 | Three short clauses plus a question fit. Targets are one or two sentences and a clause id. |
| Seed | 42 | The run can be repeated. |
| Beams at inference | 2 | Slightly more stable clause ids. Training itself is teacher-forced, so beams are not a training hyperparameter. |

Full fine-tuning was not used. It is a rubric bonus only when the hardware supports a real full training loop. This laptop does not, and LoRA is the stated baseline.

## What was deliberately left out

Multimodal input (bill photos, scanned wordings) would add the complexity bonus, and it would also add an OCR failure mode this PoC cannot evaluate honestly. Text is the handler's actual question. Images are a later project, with their own error analysis, not a checkbox.
