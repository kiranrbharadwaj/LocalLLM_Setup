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

## How we used ChatGPT and Codex

We used ChatGPT and Codex as assistants for a conversational setup workflow: discuss the goal, choose the model, perform the setup, check the results, and document the outcome. The user chose Qwen3.8-27B and directed the changes.

Codex carried out the hands-on work:

- Read the existing repository instructions through the signed-in GitHub browser when command-line Git authentication was unavailable.
- Checked the Mac and installed LM Studio’s headless runtime (`llmster`) and `lms` CLI.
- Downloaded Qwen3.8-27B Q4_K_M and verified its published file size and SHA-256 checksum.
- Prepared load and localhost API commands, attempted model loading, and inspected the runtime logs.
- Updated the README and setup guide, then created a documentation branch and pull request for review.

The setup session confirmed an M5 Pro Mac with 48 GB of memory. The model download was verified, but inference and benchmark performance were not: model loading failed with `ggml_metal_init: failed to create command queue` in the Codex session. Running the load commands from a normal macOS Terminal is the next troubleshooting step.

ChatGPT and Codex helped prepare the environment and documentation. Qwen3.8-27B runs through LM Studio’s local API once the model loads successfully.
