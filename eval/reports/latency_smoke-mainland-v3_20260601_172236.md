# LangSmith Latency Benchmark - smoke-mainland-v3

- Benchmark ID: `smoke-mainland-v3-20260601T172200-797ebe05`
- LangSmith project: `CrossBridge-RAG-Latency-Optimization`
- Source of truth: LangSmith root trace duration
- Trace runs: 1
- Overall p95: 21.0565s
- Target p95: <= 35.0s
- Acceptance-ready: False
- Meets target: False

## Per Question

| ID | runs | avg | p50 | p95 | max | target |
|---|---:|---:|---:|---:|---:|---|
| q01 | 1 | 21.0565s | 21.0565s | 21.0565s | 21.0565s | PASS |

## Slowest Spans

| span | calls | total | avg | p95 | max |
|---|---:|---:|---:|---:|---:|
| GenerateAnswer | 1 | 19.9035s | 19.9035s | 19.9035s | 19.9035s |
| ChatOpenAI | 1 | 19.8594s | 19.8594s | 19.8594s | 19.8594s |
| Rerank | 2 | 0.7632s | 0.3816s | 0.3824s | 0.3824s |
| SearchVariants | 1 | 0.6727s | 0.6727s | 0.6727s | 0.6727s |
| ChromaSimilaritySearch | 3 | 0.654s | 0.218s | 0.3003s | 0.3003s |
| BM25Search | 2 | 0.0117s | 0.0059s | 0.0074s | 0.0074s |
| RRFFusion | 1 | 0.001s | 0.001s | 0.001s | 0.001s |
| ValidateCitations | 1 | 0.0009s | 0.0009s | 0.0009s | 0.0009s |
| MetadataScoring | 1 | 0.0008s | 0.0008s | 0.0008s | 0.0008s |
| FormatOutput | 1 | 0.0007s | 0.0007s | 0.0007s | 0.0007s |
| BuildPrompt | 1 | 0.0007s | 0.0007s | 0.0007s | 0.0007s |
| PrepareInput | 1 | 0.0004s | 0.0004s | 0.0004s | 0.0004s |
| ParseStructuredQuery | 1 | 0.0002s | 0.0002s | 0.0002s | 0.0002s |
| TransformQuery | 1 | 0.0001s | 0.0001s | 0.0001s | 0.0001s |
| RouteQuery | 1 | 0.0001s | 0.0001s | 0.0001s | 0.0001s |
