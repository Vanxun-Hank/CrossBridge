# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q17_20260604_215326.json`
- Common questions: 1
- Acceptance gate: FAIL
- Improved metrics: answer_relevancy, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: faithfulness

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.9091 | 0.7727 | -0.1364 |
| `answer_relevancy` | 0.0 | 0.7312 | 0.7312 |
| `id_based_context_precision` | 0.6667 | 1.0 | 0.3333 |
| `id_based_context_recall` | 0.6667 | 0.75 | 0.0833 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q17 | remittance_compare | faithfulness:-0.1364, answer_relevancy:+0.7312, id_based_context_precision:+0.3333, id_based_context_recall:+0.0833 | 1 -> 0 (+0/-1) | 2 -> 1 (+0/-1) | +1/-1 |