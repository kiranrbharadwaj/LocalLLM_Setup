# Default Local LLM Setup: Cline + Qwen on Apple Silicon

The default coding workflow is **VS Code → Cline → local Qwen3.8-27B**, without a Cursor cloud model coordinating the task. Cursor's `ask_assistant` bridge remains available, but using it inside Cursor Agent still consumes Cursor model usage.

## Prerequisites and model download

Use an Apple Silicon Mac with **48 GB RAM or more** for the tested 32K setup, internet access for installation, Git, Python 3, Node.js 18+ and npm. Python 3 is sufficient for the setup scripts; Open WebUI installs its own isolated Python 3.11. Do not replace Apple's `/usr/bin/python3`.

Authenticate and clone the private repository:

```bash
gh auth login
gh auth setup-git
git clone https://github.com/kiranrbharadwaj/LocalLLM_Setup.git
cd LocalLLM_Setup
```

Install LM Studio's official headless runtime if `~/.lmstudio/bin/lms` is missing:

```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
export PATH="$HOME/.lmstudio/bin:$PATH"
lms daemon up
lms get https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF --gguf --select
```

Select **Qwen3.8-27B-Q4_K_M.gguf**, approximately 16.8 GB. See the [README](README.md#2-install-lm-studio-and-download-the-model) for checksum verification and the desktop-app alternative. The default setup script assumes this download is complete; it does not silently download or choose another quantization.

## Run the default setup

**Quit VS Code and Cline CLI first**, because configuration is shared and a running application could overwrite it. Run in a normal Mac Terminal, not an agent sandbox:

```bash
bash scripts/setup_local.sh
```

The command:

1. Installs official VS Code into `~/Applications` if absent, or uses the existing installation.
2. Installs the tested **Cline 4.1.24** marketplace extension and configures **both Plan and Act** for `qwen3.8-27b` at `http://127.0.0.1:1234`.
3. Starts Qwen with **32,768 tokens**, full GPU offload, and **one concurrent request**. It replaces an idle 8K configuration; if Qwen is busy with different settings it stops with instructions instead of interrupting the task.
4. Installs/updates the per-user macOS login job, retaining 32K on future model loads.
5. Installs locked Node dependencies for the optional MCP bridge and pinned Open WebUI 0.11.4 with isolated Python 3.11.

Cline configuration is stored in `~/.cline/data/globalState.json`. The configuration helper merges only the local-provider settings, leaves unrelated preferences and secrets alone, makes a private `globalState.json.before-local-qwen.bak` before the first change, and writes atomically. This helper targets the verified 4.1.24 schema; review it before changing the pinned extension version. Re-running setup deliberately resets both modes to local Qwen. Cloning alone does not install software; running this command enables startup and changes your Cline provider preferences.

## Use and verify Cline

Open VS Code, open your project folder, and click the **Cline icon in the left sidebar**. Use that panel rather than VS Code's Copilot Chat or Cursor Agent. No Cline cloud API key or subscription is needed for the configured local provider.

Check Cline Settings → API Configuration:

| Setting | Default |
| --- | --- |
| Provider for both modes | LM Studio |
| Base URL | `http://127.0.0.1:1234` |
| Model | `qwen3.8-27b` |
| Server context | `32768` |

Ask: “Do not edit files or run commands. Reply: Local Qwen is ready.” This succeeded through Cline during setup. For coding, start with a small change in your own project and review the diff. `.clineignore` excludes this repository's dependency trees, private state, and caches from model context.

Check the actual loaded context:

```bash
lms ps --json
curl -fsS http://127.0.0.1:1234/v1/models
```

Look for `contextLength: 32768` and `parallel: 1`. LM Studio estimated **21.02 GiB** for 32K on the verified 48 GB M5 Pro. Context includes system instructions, tool definitions, files, history, and output. Cline can show a generic task meter that differs from the runtime limit; the server's loaded context is authoritative. Start new tasks or compact history before sending too much context. Local inference avoids cloud model quotas but coding quality and speed still depend on the model and task.

## Smaller Macs and context changes

The default launcher checks RAM and refuses 32K on machines below 40 GiB. For a smaller Mac, choose a lower context explicitly:

```bash
QWEN_CONTEXT_LENGTH=8192 bash scripts/setup_local.sh
```

The chosen context is saved in the login job and Cline provider setup. An 8K window may be restrictive for coding agents. Larger context needs more memory and increases prompt-processing time; estimate first:

```bash
lms load qwen3.8-27b --context-length 65536 --gpu max --parallel 1 --estimate-only --yes
```

To change the installed context after setup, quit VS Code/Cline, finish outstanding model requests, and rerun setup with your chosen `QWEN_CONTEXT_LENGTH`. Do not assume the model's advertised maximum will fit your Mac. The launcher preserves a matching loaded model and only reloads an idle mismatched configuration.

## Startup, browser chat, and optional bridge

Qwen and its API start **after macOS login**, not before login at system boot. Logs are in `~/Library/Logs/LocalLLM/`. See [README step 7](README.md#7-start-qwen-automatically-at-macos-login) for restart and disable instructions. A successful one-shot job exits with code 0 while the daemon remains running. A full reboot was not performed during validation.

Open WebUI is installed by default but starts separately:

```bash
bash scripts/start_openwebui.sh
```

Open http://127.0.0.1:3000 and create your first local administrator account. Authentication stays enabled. Open WebUI is not configured to start at login. Private state lives under ignored `.local/open-webui/`; back it up with the UI stopped.

Cursor and VS Code MCP configuration still exposes `ask_assistant` if you want it. It is not needed for Cline to use Qwen as its primary model, and it does not remove Cursor's Agent limits. See the [bridge README](documents/Repo/assistant-bridge/README.md).

## Verification and troubleshooting

```bash
python3 -m unittest discover -s tests -v
python3 scripts/benchmark_lmstudio.py --model qwen3.8-27b --show-response
```

Setup scripts and the Cline state helper were checked; state merge, backup, fresh-profile, and invalid-profile tests passed. A real Cline request returned “Local Qwen is ready.” with the 32K runtime. On failure, correct the prerequisite and rerun; completed steps can be repeated. If VS Code is open or process inspection is unavailable, the installer stops before editing configuration. For a sandboxed Metal error, start the runtime from a normal host Terminal. For an empty model dropdown, verify the API is running and select Qwen explicitly (not the embedding model). Check that both Plan and Act use LM Studio.

Official references: [Cline local models](https://github.com/cline/cline/blob/main/docs/running-models-locally/overview.mdx), [VS Code CLI extension installation](https://code.visualstudio.com/docs/configure/command-line#_working-with-extensions), and [Open WebUI installation](https://docs.openwebui.com/getting-started/quick-start/).
