# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_20260604_222148.json`
- Common questions: 24
- Acceptance gate: FAIL
- Improved metrics: faithfulness, id_based_context_precision, id_based_context_recall
- Regressions over 0.03: answer_relevancy

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.6019 | 0.8546 | 0.2527 |
| `answer_relevancy` | 0.6673 | 0.5457 | -0.1216 |
| `id_based_context_precision` | 0.4618 | 0.6111 | 0.1493 |
| `id_based_context_recall` | 0.7 | 0.7319 | 0.0319 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q01 | compliance_cross_border_payment | faithfulness:+0.3682, answer_relevancy:+0.1034, id_based_context_precision:-0.0833 | 2 -> 3 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q02 | compliance_cross_border_payment | faithfulness:+0.3164, answer_relevancy:+0.2254, id_based_context_precision:-0.6667 | 0 -> 2 (+2/-0) | 0 -> 0 (+0/-0) | +2/-0 |
| q03 | compliance_cross_border_payment | faithfulness:+0.0098, answer_relevancy:-0.0022, id_based_context_precision:-0.3333 | 0 -> 1 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q04 | compliance_cross_border_payment | faithfulness:+0.5662, answer_relevancy:-0.8020, id_based_context_precision:-0.0500 | 3 -> 4 (+1/-0) | 2 -> 2 (+0/-0) | +1/-0 |
| q05 | sme_loan | faithfulness:+0.3116, answer_relevancy:-0.0180, id_based_context_precision:+0.5000, id_based_context_recall:-0.5000 | 2 -> 0 (+0/-2) | 0 -> 1 (+1/-0) | +0/-3 |
| q06 | sme_loan | faithfulness:+0.2222, answer_relevancy:-0.0171, id_based_context_precision:+0.6000, id_based_context_recall:+0.5000 | 3 -> 0 (+0/-3) | 2 -> 0 (+0/-2) | +2/-3 |
| q07 | sme_loan | faithfulness:+0.1903, answer_relevancy:-0.0270, id_based_context_precision:+0.3333, id_based_context_recall:-0.5000 | 1 -> 0 (+0/-1) | 0 -> 1 (+1/-0) | +0/-2 |
| q08 | sme_loan | faithfulness:+0.0645, answer_relevancy:-0.1540, id_based_context_precision:+0.4000 | 2 -> 0 (+0/-2) | 0 -> 0 (+0/-0) | +0/-2 |
| q09 | gba_market_entry | faithfulness:+0.2594, answer_relevancy:-0.0686, id_based_context_precision:-0.3000 | 1 -> 4 (+3/-0) | 0 -> 0 (+0/-0) | +3/-0 |
| q10 | gba_market_entry | faithfulness:+0.5275, answer_relevancy:-0.0259, id_based_context_precision:-0.1667 | 1 -> 2 (+2/-1) | 0 -> 0 (+0/-0) | +2/-1 |
| q11 | gba_market_entry | faithfulness:+0.0904, answer_relevancy:-0.7085, id_based_context_precision:-0.1333 | 2 -> 4 (+3/-1) | 0 -> 0 (+0/-0) | +3/-1 |
| q12 | gba_market_entry | faithfulness:+0.0314, answer_relevancy:+0.1956, id_based_context_precision:-0.0833 | 2 -> 3 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q13 | vietnam_supplier | faithfulness:+0.3364, answer_relevancy:+0.0323, id_based_context_precision:-0.1333 | 2 -> 4 (+2/-0) | 0 -> 0 (+0/-0) | +2/-0 |
| q14 | vietnam_supplier | faithfulness:+0.1510, answer_relevancy:+0.8474, id_based_context_precision:+0.2667, id_based_context_recall:+0.4000 | 2 -> 2 (+1/-1) | 4 -> 2 (+0/-2) | +3/-1 |
| q15 | vietnam_supplier | faithfulness:+0.2003, id_based_context_precision:-0.1333 | 2 -> 4 (+2/-0) | 2 -> 2 (+0/-0) | +2/-0 |
| q16 | remittance_compare | faithfulness:+0.3276, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 1 -> 0 (+0/-1) | +1/-2 |
| q17 | remittance_compare | faithfulness:+0.0909, id_based_context_precision:+0.3333, id_based_context_recall:+0.0833 | 1 -> 0 (+0/-1) | 2 -> 1 (+0/-1) | +1/-1 |
| q18 | remittance_compare | faithfulness:+0.2756, answer_relevancy:+0.0633, id_based_context_precision:-0.1667 | 1 -> 2 (+1/-0) | 0 -> 0 (+0/-0) | +1/-0 |
| q19 | sme_loan | faithfulness:+0.2724, answer_relevancy:-0.9973, id_based_context_precision:+0.5000, id_based_context_recall:+0.2000 | 2 -> 0 (+0/-2) | 3 -> 2 (+0/-1) | +1/-2 |
| q20 | sme_loan | faithfulness:+0.5833, answer_relevancy:-0.7112, id_based_context_precision:+0.4167, id_based_context_recall:+0.3334 | 3 -> 1 (+0/-2) | 2 -> 1 (+0/-1) | +1/-2 |
| q21 | sme_loan | faithfulness:+0.1333, answer_relevancy:-0.0125, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 2 -> 2 (+0/-0) | +0/-2 |
| q22 | sme_loan | faithfulness:+0.1304, answer_relevancy:-0.8707, id_based_context_precision:+0.7500 | 3 -> 0 (+0/-3) | 3 -> 3 (+0/-0) | +0/-3 |
| q23 | sme_loan | faithfulness:+0.0341, answer_relevancy:+0.0256, id_based_context_precision:+0.1500, id_based_context_recall:+0.2500 | 3 -> 3 (+0/-0) | 3 -> 2 (+0/-1) | +1/-0 |
| q24 | sme_loan | faithfulness:+0.5705, answer_relevancy:+0.0024, id_based_context_precision:+0.2500 | 3 -> 1 (+0/-2) | 4 -> 4 (+0/-0) | +0/-2 |