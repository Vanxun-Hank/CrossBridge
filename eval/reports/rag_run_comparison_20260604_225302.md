# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q15_20260604_225252.json`
- Common questions: 1
- Acceptance gate: PASS
- Improved metrics: faithfulness, answer_relevancy, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: none

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.4426 | 0.8 | 0.3574 |
| `answer_relevancy` | 0.0 | 0.9843 | 0.9843 |
| `id_based_context_precision` | 0.3333 | 1.0 | 0.6667 |
| `id_based_context_recall` | 0.3333 | 1.0 | 0.6667 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q15 | vietnam_supplier | faithfulness:+0.3574, answer_relevancy:+0.9843, id_based_context_precision:+0.6667, id_based_context_recall:+0.6667 | 2 -> 0 (+0/-2) | 2 -> 0 (+0/-2) | +2/-2 |