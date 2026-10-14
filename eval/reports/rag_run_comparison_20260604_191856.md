# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q03-q06-q16-q17-q18-q20-q21-q22-q23_20260604_191836.json`
- Common questions: 9
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.7064 | 0.8364 | 0.13 |
| `answer_relevancy` | 0.5705 | 0.1822 | -0.3883 |
| `id_based_context_precision` | 0.4611 | 0.7667 | 0.3056 |
| `id_based_context_recall` | 0.5926 | 0.6852 | 0.0926 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q03 | compliance_cross_border_payment | faithfulness:+0.0968, answer_relevancy:-0.5361, id_based_context_precision:-0.3333 | 0 -> 1 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q06 | sme_loan | faithfulness:+0.2222, answer_relevancy:-0.8553, id_based_context_precision:+0.6000, id_based_context_recall:+0.2500 | 3 -> 0 (+0/-3) | 2 -> 1 (+0/-1) | +1/-3 |
| q16 | remittance_compare | faithfulness:+0.1911, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 1 -> 0 (+0/-1) | +1/-2 |
| q17 | remittance_compare | faithfulness:-0.5996 | 1 -> 1 (+0/-0) | 1 -> 1 (+0/-0) | +0/-0 |
| q18 | remittance_compare | faithfulness:+0.0162, answer_relevancy:+0.0559, id_based_context_precision:-0.1667 | 1 -> 2 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q20 | sme_loan | faithfulness:+0.5833, answer_relevancy:-0.7112, id_based_context_precision:+0.4167, id_based_context_recall:+0.3334 | 3 -> 1 (+0/-2) | 2 -> 1 (+0/-1) | +1/-2 |
| q21 | sme_loan | faithfulness:-0.1467, answer_relevancy:-0.6364, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 2 -> 2 (+0/-0) | +0/-2 |
| q22 | sme_loan | faithfulness:+0.5666, answer_relevancy:-0.8707, id_based_context_precision:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 3 (+0/-0) | +0/-3 |
| q23 | sme_loan | faithfulness:+0.2400, answer_relevancy:+0.0585, id_based_context_precision:+0.1500, id_based_context_recall:+0.2500 | 3 -> 3 (+0/-0) | 3 -> 2 (+0/-1) | +1/-0 |