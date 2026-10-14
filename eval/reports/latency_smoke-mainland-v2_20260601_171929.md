# LangSmith Latency Benchmark - smoke-mainland-v2

- Benchmark ID: `smoke-mainland-v2-20260601T171857-0109cf1d`
- LangSmith project: `CrossBridge-RAG-Latency-Optimization`
- Source of truth: LangSmith root trace duration
- Trace runs: 0
- Overall p95: Nones
- Target p95: <= 35.0s
- Acceptance-ready: False
- Meets target: False

## Per Question

| ID | runs | avg | p50 | p95 | max | target |
|---|---:|---:|---:|---:|---:|---|

## Slowest Spans

| span | calls | total | avg | p95 | max |
|---|---:|---:|---:|---:|---:|
| GenerateAnswer | 1 | 19.6647s | 19.6647s | 19.6647s | 19.6647s |
| ChatOpenAI | 1 | 19.6221s | 19.6221s | 19.6221s | 19.6221s |
| Rerank | 2 | 0.7935s | 0.3967s | 0.3978s | 0.3978s |
| SearchVariants | 1 | 0.7211s | 0.7211s | 0.7211s | 0.7211s |
| ChromaSimilaritySearch | 3 | 0.6978s | 0.2326s | 0.319s | 0.319s |
| BM25Search | 2 | 0.017s | 0.0085s | 0.0106s | 0.0106s |
| MetadataScoring | 1 | 0.0013s | 0.0013s | 0.0013s | 0.0013s |
| FormatOutput | 1 | 0.001s | 0.001s | 0.001s | 0.001s |
| ValidateCitations | 1 | 0.0009s | 0.0009s | 0.0009s | 0.0009s |
| BuildPrompt | 1 | 0.0006s | 0.0006s | 0.0006s | 0.0006s |
| RRFFusion | 1 | 0.0006s | 0.0006s | 0.0006s | 0.0006s |
| PrepareInput | 1 | 0.0005s | 0.0005s | 0.0005s | 0.0005s |
| ParseStructuredQuery | 1 | 0.0002s | 0.0002s | 0.0002s | 0.0002s |
| TransformQuery | 1 | 0.0001s | 0.0001s | 0.0001s | 0.0001s |
| RouteQuery | 1 | 0.0001s | 0.0001s | 0.0001s | 0.0001s |
