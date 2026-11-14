# Evaluation

Measured by `python -m policyguard.evaluate` on this laptop after the submitted LoRA run (Flan-T5-small, rank 8, learning rate 5e-4, 12 epochs, train loss 2.84). The machine-readable copy is `artifacts/metrics.json`.

## Retrieval

22 answerable questions. Clause hit rate at 3 and MRR:

| Mode | Hit rate at 3 | MRR |
| --- | --- | --- |
| Dense only | 1.00 | 1.00 |
| Hybrid (dense + BM25) | 1.00 | 1.00 |
| Advanced (hybrid + rerank) | 1.00 | 1.00 |

The paraphrase subset is also 1.00 on every mode. On 40 short, distinct clauses the dense retriever already finds the gold clause at rank 1, so hybrid search and reranking do not add retrieval points here. They are still the right tools on a real wording set, where paraphrases and shared boilerplate make the top dense hit less reliable. The first reranker, which scored the raw question, had dropped "cooling-off" from rank 1 to rank 2. Scoring the expanded search string put HP-02 back at rank 1.

The grounding gate uses the gap under those hits. Answerable top-hit cosine similarity starts at 0.44. "What salary does the CEO draw?" is 0.14 with a rerank score near -11, and "capital of France" is about 0. The gate is cosine 0.35 or rerank -8.

## LoRA, with the gold clause in the prompt

This isolates the adapter from retrieval. 22 held-out questions.

| Model | Names the gold clause | Says REFUSE anyway | ROUGE-L |
| --- | --- | --- | --- |
| Base Flan-T5-small | 0.14 | 0.00 | 0.13 |
| LoRA adapter | 0.77 | 0.23 | 0.56 |

The base model usually echoes a fragment of the clause and drops the id. The adapter learns the cite-or-refuse format. The cost is a 0.23 false-refusal rate: with the right clause in front of it, it still sometimes says the clause does not answer. ROUGE-L moves with the citation rate because the references use the same sentence shape as the training targets. It is a secondary metric.

Two gold-context outputs:

- Waiting period, base: `[HP-02]`. LoRA: "Expenses for an illness are not payable during the first 30 days from policy inception. Treatment of accidental injuries is covered from day one. Clauses: HP-02."
- Co-pay at age 62 after an accident, base: `yes`. LoRA: `Yes. HP-05.` The wording says co-pay is waived for accidental injury, so "yes" is the wrong decision. The adapter cited the clause and missed the exception. That is the failure to show a handler.

## Full pipeline

Guardrails plus retrieval plus generation. Six questions are supposed to be refused. 22 are supposed to be answered.

| Model | Refusal catch | False refusal | Guardrail event | Retrieval hit | Model names the gold clause | Median latency |
| --- | --- | --- | --- | --- | --- | --- |
| Base | 1.00 | 0.00 | 1.00 | 1.00 | 0.27 | 0.8 s |
| LoRA | 1.00 | 0.09 | 1.00 | 1.00 | 0.32 | 3.8 s |

Every blocked question was blocked for the intended reason. Injection and fraud coaching never call the model. The CEO-salary question is refused by the grounding gate, not by a keyword list.

The pipeline citation rate is much lower than the gold-context rate. The retriever is right, and the draft is often right, but the model is shown three clauses and sometimes stamps the wrong id on a correct sentence. Output validation only removes an id that was not retrieved, so a wrong id from the top 3 survives. Example: the waiting-period answer quotes the 30-day rule and then ends "Clauses: HP-04". HP-04 was retrieved. It is the wrong clause.

## What this does and does not support

The pilot target was a gold clause in the top 3 on at least 75 percent of answerable questions. Retrieval is at 100 percent on this synthetic set. Unsafe questions are refused and the event is recorded. A draft does not yet reliably cite the clause the sentence came from once three clauses are in the prompt.

Do not treat the 1.00 hit rate as evidence about a real wording library. These clauses were written to be distinct, and the questions were written by the same person. The next measurement is questions written by someone who did not write the wordings, on clauses that share boilerplate.
