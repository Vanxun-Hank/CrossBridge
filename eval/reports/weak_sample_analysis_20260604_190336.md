# RAG Weak-Sample Analysis

- RAGAS report: `eval/reports/ragas_full_ids_q03-q06-q16-q17-q18-q20-q21-q22-q23_20260604_190321.json`
- Questions: 9
- Weak questions: 9

## Root Cause Counts

| Root cause | Count |
|---|---:|
| `incomplete_answer_synthesis` | 9 |
| `wrong_source_retrieved` | 8 |
| `insufficient_chunk_granularity` | 6 |
| `hallucinated_claim` | 2 |
| `poor_query_expansion` | 1 |

## Weak Samples

| ID | scenario | metric gaps | root causes | next action | evidence |
|---|---|---|---|---|---|
| q03 | compliance_cross_border_payment | answer_relevancy=0.0 < 0.85, id_based_context_precision=0.5 < 0.8 | `incomplete_answer_synthesis`, `insufficient_chunk_granularity`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | off-target prompt docs: safe_current_account_fx_guideline_2020, safe_trade_fx_optimization_2024<br>duplicate parent doc IDs in prompt contexts: 1<br>answer relevancy below target |
| q06 | sme_loan | answer_relevancy=0.0 < 0.85, id_based_context_recall=0.75 < 0.8 | `incomplete_answer_synthesis`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | missing expected docs in prompt contexts: hkmc_sfgs_factsheet<br>answer relevancy below target |
| q16 | remittance_compare | faithfulness=0.8125 < 0.85, answer_relevancy=0.0 < 0.85 | `hallucinated_claim`, `incomplete_answer_synthesis`, `insufficient_chunk_granularity` | `adjust_chunk_or_prompt_context_selection` | duplicate parent doc IDs in prompt contexts: 1<br>answer contains unsupported-claim cue words or examples<br>faithfulness below target despite at least one expected context<br>answer relevancy below target |
| q17 | remittance_compare | answer_relevancy=0.0 < 0.85, id_based_context_precision=0.6667 < 0.8, id_based_context_recall=0.6667 < 0.8 | `incomplete_answer_synthesis`, `insufficient_chunk_granularity`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | missing expected docs in prompt contexts: hkma_payment_systems<br>off-target prompt docs: hkicl_hkd_clearing_house_rules_2026<br>duplicate parent doc IDs in prompt contexts: 2<br>answer relevancy below target |
| q18 | remittance_compare | faithfulness=0.8214 < 0.85, answer_relevancy=0.7868 < 0.85, id_based_context_precision=0.5 < 0.8 | `incomplete_answer_synthesis`, `insufficient_chunk_granularity`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | off-target prompt docs: hkicl_hkd_fps_rules_2025, safe_capital_account_fx_guideline_2024<br>duplicate parent doc IDs in prompt contexts: 1<br>faithfulness below target despite at least one expected context<br>answer relevancy below target |
| q20 | sme_loan | answer_relevancy=0.0 < 0.85, id_based_context_precision=0.6667 < 0.8, id_based_context_recall=0.6667 < 0.8 | `incomplete_answer_synthesis`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | missing expected docs in prompt contexts: hkmc_sfgs_factsheet<br>off-target prompt docs: bochk_sfgs_product<br>answer relevancy below target<br>off-target bank/product source regions: {'bochk_sfgs_product': ['Hong Kong']} |
| q21 | sme_loan | answer_relevancy=0.0 < 0.85, id_based_context_recall=0.3333 < 0.8 | `incomplete_answer_synthesis`, `insufficient_chunk_granularity`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | missing expected docs in prompt contexts: bochk_sme_loan, hkma_sfgs_90_product<br>duplicate parent doc IDs in prompt contexts: 1<br>answer relevancy below target |
| q22 | sme_loan | faithfulness=0.56 < 0.85, answer_relevancy=0.0 < 0.85, id_based_context_recall=0.25 < 0.8 | `incomplete_answer_synthesis`, `insufficient_chunk_granularity`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | missing expected docs in prompt contexts: bochk_sfgs_product, bochk_sme_loan, hkma_sfgs_90_product<br>duplicate parent doc IDs in prompt contexts: 1<br>faithfulness below target despite at least one expected context<br>answer relevancy below target |
| q23 | sme_loan | answer_relevancy=0.0 < 0.85, id_based_context_precision=0.4 < 0.8, id_based_context_recall=0.5 < 0.8 | `hallucinated_claim`, `incomplete_answer_synthesis`, `poor_query_expansion`, `wrong_source_retrieved` | `tune_retrieval_rerank_or_prompt_source_filter` | missing expected docs in prompt contexts: bochk_sfgs_product, hkma_sfgs_extension_2024<br>off-target prompt docs: hkma_sfgs_insight_2025, hkmc_sfgs_application_procedures, hkmc_sfgs_application_procedures_lender<br>answer contains unsupported-claim cue words or examples<br>answer relevancy below target<br>fee/time query retrieved regulatory source families |