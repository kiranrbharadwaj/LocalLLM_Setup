# Local LLM Setup

Notes and scripts for running Qwen3.8-27B locally on Apple Silicon with LM Studio.

## Model and local server

Use **Qwen3.8-27B** with the **Q4_K_M GGUF** quantization from [lmstudio-community/Qwen3.8-27B-GGUF](https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF). The model file is `Qwen3.8-27B-Q4_K_M.gguf` (approximately 16.8 GB).

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for installation and GitHub authentication. With LM Studio and its `lms` CLI installed, download the model in LM Studio, then load it and start the local API:

```bash
lms load qwen3.8-27b --identifier qwen3.8-27b --context-length 8192 --gpu max --yes
lms server start --port 1234 --bind 127.0.0.1
```

The API base URL is `http://127.0.0.1:1234/v1`; the model identifier used below is `qwen3.8-27b`. An 8,192-token context is a starting point for a 48 GB Apple Silicon Mac; adjust it according to available memory.

## Benchmark LM Studio (TTFT / decode)

With the local server running and Qwen3.8-27B loaded:

```bash
python3 scripts/benchmark_lmstudio.py --model qwen3.8-27b
```

Useful flags:

```bash
python3 scripts/benchmark_lmstudio.py \
  --model qwen3.8-27b \
  --max-tokens 200 \
  --warmup 1 \
  --check-memory \
  --show-response
```

Stdlib only — no extra Python packages required. Benchmark results depend on your hardware, runtime, and context settings.
