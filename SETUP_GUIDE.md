# Local LLM Setup Guide for M5 Pro (48GB)

## 🚀 Overview
This guide helps you set up a local AI development environment on your MacBook Pro (M5 Pro, 48GB RAM). Our goal is to run powerful Large Language Models (LLMs) locally to avoid paid API costs.

## 🛠️ Prerequisites
1. **LM Studio**: The "hub" for downloading and running local models.
2. **Cursor**: An AI-powered code editor.
3. **GitHub CLI (`gh`)**: For managing your code and backups.
4. **Python 3**: Pre-installed on macOS.
5. **Node.js 18+ and npm**: Required by the assistant bridge.

## 👣 Step-by-Step Setup

### 1. Install & Configure LM Studio
- Download and install [LM Studio](https://lmstudio.ai/).
- Search for **Qwen3.8-27B** and select the **Q4_K_M GGUF** version from [lmstudio-community/Qwen3.8-27B-GGUF](https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF).
- Download `Qwen3.8-27B-Q4_K_M.gguf` (approximately 16.8 GB).
- Start with an 8,192-token context on a 48 GB Mac and adjust it according to available memory.
- Load the model, then start the local API. With the LM Studio `lms` CLI installed:

```bash
lms load qwen3.8-27b --identifier qwen3.8-27b --context-length 8192 --gpu max --yes
lms server start --port 1234 --bind 127.0.0.1
```

The API base URL is `http://127.0.0.1:1234/v1`, and the model identifier is `qwen3.8-27b`.

### 2. Authenticate GitHub
```bash
gh auth login
gh auth setup-git
```
Follow the prompts to log in via your browser. Browser sign-in alone does not authenticate command-line Git.

### 3. Set Up the Repository
```bash
git clone https://github.com/kiranrbharadwaj/LocalLLM_Setup.git
cd LocalLLM_Setup
npm --prefix documents/Repo/assistant-bridge ci
```
Open the repository root in Cursor or VS Code to use its MCP configuration. See the [bridge README](documents/Repo/assistant-bridge/README.md) for tool usage and environment settings.

### 4. Benchmark Your Hardware
Verify that your local setup is running efficiently:
```bash
python3 scripts/benchmark_lmstudio.py --model qwen3.8-27b --show-response
```
**What to look for:**
- **TTFT**: Should be low (fast response start).
- **Decode Speed**: Higher is better (more tokens per second).

## 📚 Key Concepts for Beginners
- **Quantization**: The process of compressing a model so it fits in RAM without losing too much intelligence.
- **Unified Memory**: Because we have Apple Silicon, our GPU and CPU share the same 48GB of RAM, which is why we can run larger models than most laptops.
