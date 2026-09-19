# Local LLM Setup Guide for M5 Pro (48GB)

## 🚀 Overview
This guide helps you set up a local AI development environment on your MacBook Pro (M5 Pro, 48GB RAM). Our goal is to run powerful Large Language Models (LLMs) locally to avoid paid API costs.

## 🛠️ Prerequisites
1. **LM Studio**: The "hub" for downloading and running local models.
2. **Cursor**: An AI-powered code editor.
3. **GitHub CLI (`gh`)**: For managing your code and backups.
4. **Python 3**: Pre-installed on macOS.

## 👣 Step-by-Step Setup

### 1. Install & Configure LM Studio
- Download and install [LM Studio](https://lmstudio.ai/).
- Search for a model (e.g., `Qwen 2.5 7B` or `Llama 3.1 8B`).
- **Pro Tip**: Look for "GGUF" versions. Since we have 48GB of RAM, we can handle medium-sized models comfortably.
- Go to the **Local Server** tab (↔️ icon) and click **Start Server**. This makes the model available via an API.

### 2. Set Up the Repository
```bash
# Clone the setup repo
git clone https://github.com/kiranrbharadwaj/LocalLLM_Setup.git
cd LocalLLM_Setup
```

### 3. Authenticate GitHub
```bash
gh auth login
```
Follow the prompts to log in via your browser.

### 4. Benchmark Your Hardware
Verify that your local setup is running efficiently:
```bash
python3 scripts/benchmark_lmstudio.py --show-response
```
**What to look for:**
- **TTFT**: Should be low (fast response start).
- **Decode Speed**: Higher is better (more tokens per second).

## 📚 Key Concepts for Beginners
- **Quantization**: The process of compressing a model so it fits in RAM without losing too much intelligence.
- **Unified Memory**: Because we have Apple Silicon, our GPU and CPU share the same 48GB of RAM, which is why we can run larger models than most laptops.
