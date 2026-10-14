# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q06_20260604_211427.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: id_based_context_precision, id_based_context_recall
- Regressions over 0.03: faithfulness, answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.7778 | 0.7 | -0.0778 |
| `answer_relevancy` | 0.8553 | 0.4718 | -0.3835 |
| `id_based_context_precision` | 0.4 | 1.0 | 0.6 |
| `id_based_context_recall` | 0.5 | 1.0 | 0.5 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q06 | sme_loan | faithfulness:-0.0778, answer_relevancy:-0.3835, id_based_context_precision:+0.6000, id_based_context_recall:+0.5000 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |