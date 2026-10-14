# LangSmith Latency Benchmark - baseline

- Benchmark ID: `baseline-20260601T172315-fd24a0a1`
- LangSmith project: `CrossBridge-RAG-Latency-Optimization`
- Source of truth: LangSmith root trace duration
- Trace runs: 24
- Overall p95: 30.4255s
- Target p95: <= 35.0s
- Acceptance-ready: True
- Meets target: True

## Per Question

| ID | runs | avg | p50 | p95 | max | target |
|---|---:|---:|---:|---:|---:|---|
| q01 | 1 | 24.7835s | 24.7835s | 24.7835s | 24.7835s | PASS |
| q02 | 1 | 24.2158s | 24.2158s | 24.2158s | 24.2158s | PASS |
| q03 | 1 | 14.2777s | 14.2777s | 14.2777s | 14.2777s | PASS |
| q04 | 1 | 30.4255s | 30.4255s | 30.4255s | 30.4255s | PASS |
| q05 | 1 | 18.4489s | 18.4489s | 18.4489s | 18.4489s | PASS |
| q06 | 1 | 12.4545s | 12.4545s | 12.4545s | 12.4545s | PASS |
| q07 | 1 | 24.5987s | 24.5987s | 24.5987s | 24.5987s | PASS |
| q08 | 1 | 18.0643s | 18.0643s | 18.0643s | 18.0643s | PASS |
| q09 | 1 | 22.051s | 22.051s | 22.051s | 22.051s | PASS |
| q10 | 1 | 23.9158s | 23.9158s | 23.9158s | 23.9158s | PASS |
| q11 | 1 | 18.5649s | 18.5649s | 18.5649s | 18.5649s | PASS |
| q12 | 1 | 19.7489s | 19.7489s | 19.7489s | 19.7489s | PASS |
| q13 | 1 | 19.8401s | 19.8401s | 19.8401s | 19.8401s | PASS |
| q14 | 1 | 23.381s | 23.381s | 23.381s | 23.381s | PASS |
| q15 | 1 | 25.796s | 25.796s | 25.796s | 25.796s | PASS |
| q16 | 1 | 21.3532s | 21.3532s | 21.3532s | 21.3532s | PASS |
| q17 | 1 | 9.5288s | 9.5288s | 9.5288s | 9.5288s | PASS |
| q18 | 1 | 19.9315s | 19.9315s | 19.9315s | 19.9315s | PASS |
| q19 | 1 | 16.8615s | 16.8615s | 16.8615s | 16.8615s | PASS |
| q20 | 1 | 20.045s | 20.045s | 20.045s | 20.045s | PASS |
| q21 | 1 | 20.5713s | 20.5713s | 20.5713s | 20.5713s | PASS |
| q22 | 1 | 26.7593s | 26.7593s | 26.7593s | 26.7593s | PASS |
| q23 | 1 | 22.2336s | 22.2336s | 22.2336s | 22.2336s | PASS |
| q24 | 1 | 30.6968s | 30.6968s | 30.6968s | 30.6968s | PASS |

## Slowest Spans

| span | calls | total | avg | p95 | max |
|---|---:|---:|---:|---:|---:|
| ChatOpenAI | 29 | 482.705s | 16.645s | 27.4285s | 29.3456s |
| GenerateAnswer | 24 | 474.1327s | 19.7555s | 27.43s | 29.3474s |
| SearchVariants | 24 | 18.5888s | 0.7745s | 1.5675s | 1.8066s |
| Rerank | 48 | 17.3687s | 0.3618s | 0.4239s | 0.4443s |
| ChromaSimilaritySearch | 67 | 16.1559s | 0.2411s | 0.3491s | 0.4707s |
| TransformQuery | 24 | 6.7153s | 0.2798s | 1.9787s | 2.8346s |
| BM25Search | 43 | 0.3885s | 0.009s | 0.0134s | 0.0147s |
| FormatOutput | 24 | 0.0239s | 0.001s | 0.0012s | 0.0013s |
| MetadataScoring | 24 | 0.0222s | 0.0009s | 0.0014s | 0.0014s |
| RRFFusion | 24 | 0.0214s | 0.0009s | 0.0013s | 0.0013s |
| BuildPrompt | 24 | 0.016s | 0.0007s | 0.001s | 0.0011s |
| ValidateCitations | 24 | 0.016s | 0.0007s | 0.0009s | 0.001s |
| PrepareInput | 24 | 0.0115s | 0.0005s | 0.0007s | 0.0007s |
| ParseStructuredQuery | 24 | 0.0113s | 0.0005s | 0.0006s | 0.0007s |
| RouteQuery | 24 | 0.0087s | 0.0004s | 0.0006s | 0.0011s |
