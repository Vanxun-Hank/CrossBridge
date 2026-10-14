# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q16-q20-q22-q19-q04-q14-q24_20260605_233706.json`
- Common questions: 7
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.4383 | 0.5918 | 0.1535 |
| `answer_relevancy` | 0.6126 | 0.2851 | -0.3275 |
| `id_based_context_precision` | 0.3095 | 0.8476 | 0.5381 |
| `id_based_context_recall` | 0.3881 | 0.8429 | 0.4548 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q04 | compliance_cross_border_payment | faithfulness:-0.0445, answer_relevancy:-0.8020, id_based_context_precision:+0.7500, id_based_context_recall:+0.6667 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |
| q14 | vietnam_supplier | faithfulness:-0.0463, id_based_context_precision:+0.6667, id_based_context_recall:+0.6000 | 2 -> 0 (+0/-2) | 4 -> 1 (+0/-3) | +3/-2 |
| q16 | remittance_compare | faithfulness:+0.0518, id_based_context_recall:-0.5000 | 2 -> 2 (+2/-2) | 1 -> 1 (+0/-0) | +2/-2 |
| q19 | sme_loan | faithfulness:-0.0519, answer_relevancy:-0.1201, id_based_context_precision:+0.5000, id_based_context_recall:+0.6000 | 2 -> 0 (+0/-2) | 3 -> 0 (+0/-3) | +3/-2 |
| q20 | sme_loan | faithfulness:+0.4404, answer_relevancy:-0.7112, id_based_context_precision:+0.3500, id_based_context_recall:+0.6667 | 3 -> 2 (+0/-1) | 2 -> 0 (+0/-2) | +2/-1 |
| q22 | sme_loan | faithfulness:+0.3125, answer_relevancy:-0.8707, id_based_context_precision:+0.7500, id_based_context_recall:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 0 (+0/-3) | +3/-3 |
| q24 | sme_loan | answer_relevancy:-0.0733, id_based_context_precision:+0.7500, id_based_context_recall:+0.4000 | 3 -> 0 (+0/-3) | 4 -> 2 (+1/-3) | +3/-4 |