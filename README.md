# Local LLM Setup

Notes and scripts for running local models on Apple Silicon (LM Studio).

## Benchmark LM Studio (TTFT / decode)

With LM Studio’s local server running (default `http://127.0.0.1:1234`) and a model loaded:

```bash
python3 scripts/benchmark_lmstudio.py
```

Useful flags:

```bash
python3 scripts/benchmark_lmstudio.py \
  --model qwen/qwen3.5-9b \
  --max-tokens 200 \
  --warmup 1 \
  --check-memory \
  --show-response
```

Stdlib only — no extra Python packages required.
