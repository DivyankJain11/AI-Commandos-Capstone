# Viva notes

Forty of the hundred marks are individual. These notes are the decisions to be able to defend, mapped to the modules that implement them. Speak from the repo, not from a memorised definition.

## Ownership

| If asked "what did you build?" | Open this |
| --- | --- |
| The question is blocked or redacted before any model sees it | `policyguard/guardrails.py` |
| Clauses, not token windows | `policyguard/chunking.py`, `data/policies/` |
| Hybrid search, expansion, rerank, grounding gate | `policyguard/retrieval.py`, `policyguard/indexing.py` |
| The prompt used both in training and in the app | `build_source` in `policyguard/generation.py` |
| The LoRA run and the reason for each hyperparameter | `policyguard/finetune.py`, `policyguard/config.py`, `artifacts/train_log.json` |
| The split that keeps eval clauses out of training | `data/finetune/train.jsonl`, `data/eval/gold.jsonl`, `tests/test_retrieval.py` |
| The numbers | `python -m policyguard.evaluate`, then `artifacts/metrics.json` and `docs/evaluation.md` |
| The demo path | `streamlit run app.py` |

## Trade-offs worth saying out loud

**Cost, latency, accuracy.** A hosted 7B or GPT-class model would write smoother sentences and would cost money per question, send handler questions off the laptop, and make the fine-tune undemonstrable. Flan-T5-small is local, finishes LoRA in minutes on CPU, and writes short, sometimes clumsy sentences. The clause is on screen so a clumsy sentence can be checked. Median latency is the number in the metrics file, measured on this machine, not a brochure figure.

**RAG versus fine-tuning versus both.** Fine-tuning does not store the wordings. If a clause changes, a fine-tuned model is wrong until it is trained again. RAG picks up an edited clause on the next ingest. Fine-tuning is still here because the small model does not reliably follow "cite a clause or say REFUSE" from the instruction alone. LoRA is for the behaviour. RAG is for the fact. The eval reports those two separately: gold-context generation (adapter only) and retrieval hit rate (retriever only).

**Why the training context is the gold clause, not whatever retrieval returned.** If the adapter is trained on a wrong retrieved clause, it learns to answer from the wrong evidence. Gold context teaches the format. The cost is train/serve skew: at inference the context is retrieved, not labelled. The next iteration trains on retrieved context, including deliberate misses, once retrieval hit rate is high enough that the label is usually right.

**Why not a larger LoRA rank, and why 12 epochs.** Thirty-two examples. Rank 16 would memorise those rows. The first training run used rank 8, learning rate 1e-4, and 3 epochs. The B matrices stayed near zero and the loss did not fall: 24 optimizer steps was too few. The submitted run is rank 8, learning rate 5e-4, 12 epochs. The held-out clauses are still absent from training, so the extra epochs are there to learn "cite the clause or say REFUSE", not to store HP-02 or MC-05.

**Chunking.** A handler cites HP-02, not "characters 400 to 900". The exception in a clause ("accidental injuries are covered from day one") has to stay in the same chunk as the rule it qualifies. That is why the chunker splits on headings.

**Advanced RAG, and when it will not win.** On forty short clauses a dense retriever already finds the direct questions. Hybrid search and the synonym list are aimed at paraphrases: cooling-off, bonus if I never claim, flood water, a broken tooth. The first reranker scored the raw question and moved "cooling-off" from rank 1 to rank 2, behind the pre-existing-disease clause. The reranker now scores the expanded search string. Read the metrics file for the after-change hit rate and MRR. If advanced retrieval is tied with dense rather than ahead of it, say that. The corpus is too small for a large gap, and pretending otherwise is worse than the tie.

**Query expansion as a dictionary.** It cannot hallucinate a new question, and a reviewer can read every synonym. It will miss a paraphrase that was not listed. That miss shows up as a retrieval error with an empty expansion, which is diagnosable. An LLM rewriter hides the same miss inside a rewritten question.

**Safety.** Injection and fraud coaching never call the model. That is stronger than asking the model to behave, and it is also narrower: a new phrasing can slip past the regular expressions. The grounding gate and the REFUSE behaviour are the second line. PII regexes miss person names. Say that limitation before someone else does.

**Metrics.** Clause hit rate at 3 and MRR are the retrieval metrics. Citation rate with the gold clause in the prompt is the generation metric. ROUGE-L is reported because the rubric names it, and it is the wrong primary metric: two correct sentences about a 30-day waiting period can share few tokens. Refusal catch rate and false-refusal rate are reported separately so a model that refuses everything cannot look accurate.

**Business value.** The handler's expensive mistake is stating a limit that is not in the wording. The system is valuable when it shows the clause and refuses otherwise, even if the sentence is plain. It is not valuable as a chat toy that sounds confident. The next step a business owner would fund is a review of fifty real handler questions, not a larger model.

## A two-minute demo order

1. Direct question: initial waiting period. Show the clause id and the 30-day / accident split.
2. Paraphrase: cooling-off, or flood water and the engine. Open the sidebar and, if the numbers support it, flip from dense to advanced.
3. Reasoning: 62 years old, admitted after an accident, co-pay waived. Read HP-05 out loud, including the exception.
4. PII: the ambulance question with a phone and an email. Show the redacted question.
5. Injection, then "how do I forge a discharge summary". Point out that the model was not called.
6. CEO salary. This one is refused because nothing in the wordings is close enough, not because of a keyword list.
7. Switch the generator from LoRA to base on one held-out question and compare whether the clause id survives. Use the gold-context table if the live answer is noisy.

## If a number is challenged

Open `artifacts/metrics.json` and `artifacts/train_log.json`. Do not quote a figure from memory that is not in those files. If a paraphrase was missed, walk the expansion list and the top clause that was returned instead. That walk-through is the practical-ownership mark.
