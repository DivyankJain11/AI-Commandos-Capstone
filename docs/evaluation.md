# Evaluation

The method is fixed in `policyguard/evaluate.py`. This page is filled with the measured numbers after a run, together with a reading of the errors. Do not invent figures here. If the metrics file is missing, run:

```powershell
.\.venv\Scripts\python.exe -m policyguard.evaluate
```

## How to read the file

`artifacts/metrics.json` has three blocks.

**retrieval.** For `dense`, `hybrid`, and `advanced`: clause hit rate at 3 and MRR, overall and by tag. Tags are `heldout`, `paraphrase`, `reasoning`, and `pii`. Refusal rows are not in the hit rate. Their top score is still stored, and that score is what the grounding threshold is compared against.

**gold_context_generation.** The gold clause is placed in the prompt. This is the before/after for LoRA. `citation_rate` is the share of answers that name the gold clause id. `false_refuse_rate` is the share that say REFUSE even though the clause was provided. `rouge_l` is the surface overlap with the reference sentence.

**pipeline.** The full path, including guardrails and the grounding gate, for the base model and the adapter. `refusal_catch_rate` should be high. `false_refusal_rate` is the share of answerable questions the system refused. A system that refuses everything scores perfectly on the first and terribly on the second.

## Qualitative sample

After the run, quote five rows from the pipeline details rather than only the averages:

- one direct held-out question the system answered with the right clause
- one paraphrase, whether it hit or missed
- the co-pay reasoning question (f19)
- one blocked question (injection or fraud coaching), including the event name
- one failure, with the clause that was retrieved instead of the gold clause

State the limitation next to the failure. The usual ones are listed in the README: small generator, general-domain embedder, dictionary expansion, synthetic wordings, no handler study.
