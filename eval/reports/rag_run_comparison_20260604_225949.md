# RAG Run Comparison

- Baseline: `eval/reports/ragas_full_20260601_180627.json`
- Candidate: `eval/reports/ragas_full_ids_q11_20260604_225942.json`
- Common questions: 1
- Acceptance gate: PASS
- Improved metrics: faithfulness, id_based_context_precision
- Regressions over 0.03: none

## Metric Means

| Metric | baseline | candidate | delta |
|---|---:|---:|---:|
| `faithfulness` | 0.7667 | 1.0 | 0.2333 |
| `answer_relevancy` | 0.7085 | 0.7027 | -0.0058 |
| `id_based_context_precision` | 0.3333 | 1.0 | 0.6667 |
| `id_based_context_recall` | 1.0 | 1.0 | 0.0 |

## Per-Question Context Movement

| ID | scenario | metric deltas | off-target docs | missing expected docs | context changes |
|---|---|---|---|---|---|
| q11 | gba_market_entry | faithfulness:+0.2333, answer_relevancy:-0.0058, id_based_context_precision:+0.6667 | 2 -> 0 (+0/-2) | 0 -> 0 (+0/-0) | +0/-2 |