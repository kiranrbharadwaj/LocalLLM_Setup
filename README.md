# Local LLM Setup

Run **Qwen3.8-27B Q4_K_M** on Apple Silicon through LM Studio, then connect Cursor or VS Code through the included MCP assistant bridge. This walkthrough records the repository review, fixes, and checks so the next person can reproduce the setup.

## Default setup: local coding without Cursor Agent quotas

Follow [SETUP_GUIDE.md](SETUP_GUIDE.md). After installing LM Studio's CLI, downloading Qwen3.8-27B Q4_K_M, and providing Git, Python 3, Node.js 18+, and npm, quit VS Code/Cline and run in a normal Mac Terminal:

```bash
bash scripts/setup_local.sh
```

This installs/configures VS Code + Cline 4.1.24 for **local Qwen in both Plan and Act**, loads **32,768-token context with one concurrent request**, enables macOS login startup, installs the optional bridge dependencies, and installs Open WebUI. Use the **Cline sidebar** for local coding. Cursor Agent still uses its selected cloud model even when it calls `ask_assistant`; that bridge does not bypass Cursor usage limits.

The default is tested on a 48 GB Apple Silicon Mac (32K memory estimate: 21.02 GiB). Smaller machines must select a lower context explicitly; see the setup guide. Cline state is backed up and merged while the editor is closed. Open WebUI account creation remains a user step, and its server starts separately. Installation requires internet access and running the setup command; cloning alone does not install anything.

## What is in this repository

All ten original project-owned files were read during the initial setup. Open WebUI scripts and local-state exclusions were added afterward. Installed third-party dependency source was not exhaustively audited.

| File | Purpose |
| --- | --- |
| `README.md` | End-to-end setup, verification, and troubleshooting |
| `SETUP_GUIDE.md` | Default Cline setup, prerequisites, context sizing, and verification |
| `scripts/setup_local.sh` | Default setup orchestration |
| `scripts/setup_cline.sh` | Installs VS Code and pinned Cline |
| `scripts/configure_cline.py` | Backs up and merges local Plan/Act provider settings |
| `.clineignore` | Excludes dependencies and private state from Cline context |
| `.vscode/extensions.json` | Recommends the Cline extension |
| `tests/test_configure_cline.py` | Configuration preservation and failure tests |
| `scripts/start-qwen.sh` | Repeatable Qwen and localhost API launcher |
| `scripts/install_macos_startup.sh` | Installs and updates the macOS login job |
| `scripts/setup_openwebui.sh` | Installs pinned Open WebUI with isolated Python 3.11 |
| `scripts/start_openwebui.sh` | Starts the localhost chat UI connected to LM Studio |
| `.gitignore` | Excludes machine-local environments, chats, caches, and secrets |
| `scripts/benchmark_lmstudio.py` | Streaming API benchmark using only Python's standard library |
| `.cursor/mcp.json` | Cursor MCP server configuration |
| `.vscode/mcp.json` | VS Code MCP server configuration |
| `documents/Repo/assistant-bridge/README.md` | Bridge configuration and tool usage |
| `documents/Repo/assistant-bridge/mcp-assistant.mjs` | Stdio MCP server exposing `ask_assistant` |
| `documents/Repo/assistant-bridge/.env.example` | Example environment variables; not loaded automatically |
| `documents/Repo/assistant-bridge/package.json` | Node requirements, start command, and dependency declaration |
| `documents/Repo/assistant-bridge/package-lock.json` | Dependency versions used by `npm ci` |

Run the commands below from the **repository root**, unless a step says otherwise. Open that same folder in your editor; opening only the bridge subfolder prevents discovery of the root MCP configuration.

## 1. Prepare the machine and clone

You need an Apple Silicon Mac, Git, Node.js **18 or newer** with npm, Python 3, and enough storage for the approximately **16.8 GB** model plus runtime and dependencies. The verified machine had an **M5 Pro and 48 GB memory**; smaller machines may need different model or context settings.

Check prerequisites:

```bash
node --version
npm --version
python3 --version
git --version
```

Authenticate Git before cloning this private repository. With the GitHub CLI installed, HTTPS authentication is:

```bash
gh auth login
gh auth setup-git
git clone https://github.com/kiranrbharadwaj/LocalLLM_Setup.git
cd LocalLLM_Setup
```

Alternatively, configure a GitHub SSH key and clone `git@github.com:kiranrbharadwaj/LocalLLM_Setup.git`. Being signed in to GitHub in a browser does not authenticate command-line Git. See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more detail.

## 2. Install LM Studio and download the model

Choose either the [LM Studio desktop app](https://lmstudio.ai/download) or its headless runtime. This setup used **llmster**, so the desktop app was not required. To install the headless runtime using LM Studio's official installer:

```bash
curl -fsSL https://lmstudio.ai/install.sh | bash
export PATH="$HOME/.lmstudio/bin:$PATH"
lms --help
lms daemon up
```

Add the PATH entry to your shell configuration if needed for future terminals. For the desktop app, use its CLI setup instructions if `lms` is not available.

Download **`Qwen3.8-27B-Q4_K_M.gguf`** from [lmstudio-community/Qwen3.8-27B-GGUF](https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF). In the desktop app, select that exact quantization. The CLI can present the repository's GGUF choices:

```bash
lms get https://huggingface.co/lmstudio-community/Qwen3.8-27B-GGUF --gguf --select
```

Select **Q4_K_M**. This setup did not install Qwen2.5. The verified file was stored at:

```text
~/.lmstudio/models/lmstudio-community/Qwen3.8-27B-GGUF/Qwen3.8-27B-Q4_K_M.gguf
```

The downloaded file was **16,810,714,336 bytes**, with SHA-256:

```text
e00082f779fa385cee8c68a3ec8833a75778cc87272240b942f74e0b8243e520
```

Verify your copy with `shasum -a 256` and compare it with the publisher's metadata for the same file revision.

## 3. Load the model and start the API

```bash
lms daemon up
lms load qwen3.8-27b --identifier qwen3.8-27b --context-length 32768 --gpu max --parallel 1 --yes
lms server start --port 1234 --bind 127.0.0.1
```

The explicit identifier **`qwen3.8-27b`** must match the bridge configuration. The default is now 32,768 tokens with one concurrent request, validated on the 48 GB Mac. See the setup guide for memory estimates and smaller-machine overrides.

Confirm the model is visible, then ask for a real response:

```bash
curl -fsS http://127.0.0.1:1234/v1/models
curl -fsS http://127.0.0.1:1234/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"qwen3.8-27b","messages":[{"role":"user","content":"Reply with: Local model is ready."}],"max_tokens":256}'
```

The server binds to localhost. The verified configuration did not require an API key.

## 4. Install and connect the assistant bridge

From the repository root:

```bash
npm --prefix documents/Repo/assistant-bridge ci
```

Rebuild dependencies from the lockfile even if the checkout includes `node_modules`; copied dependencies are not a substitute for a clean installation. The setup installed 94 packages, with MCP SDK 1.30.1 selected by the lockfile; npm reported no known vulnerabilities at that time.

Both editor configurations and the bridge defaults were aligned to:

| Setting | Value |
| --- | --- |
| `ASSISTANT_API_BASE` | `http://127.0.0.1:1234/v1` |
| `ASSISTANT_MODEL` | `qwen3.8-27b` |
| `ASSISTANT_API_KEY` | Empty for this local server |
| `ASSISTANT_TIMEOUT_MS` | `120000` |

The bridge reads **process environment variables**. Copying `.env.example` to `.env` alone does not configure it: export variables or edit the MCP configuration's `env` object. Use an API key only if your server requires one.

Open the repository root in Cursor or VS Code, enable/start the configured MCP server, and allow the editor to use **`ask_assistant`**. That tool accepts a required `prompt` string and optional `context` string. Node must be available to the editor process. VS Code uses `${workspaceFolder}` in the bridge path; Cursor uses a path relative to the repository root.

`npm start` inside the bridge folder starts a stdio MCP server and waits for a client; it is not an interactive chat prompt. Diagnostics go to stderr because stdout carries the MCP protocol. See the [bridge README](documents/Repo/assistant-bridge/README.md) for further details.

## 5. Verify and benchmark

With the API running, from the repository root:

```bash
python3 scripts/benchmark_lmstudio.py \
  --model qwen3.8-27b \
  --max-tokens 200 \
  --warmup 1 \
  --check-memory \
  --show-response
```

No Python packages need to be installed. If changing the endpoint, pass **`--base-url http://127.0.0.1:1234`**, without `/v1`: the benchmark appends `/v1/chat/completions`. The bridge's API base, by contrast, includes `/v1`.

The benchmark was fixed to start TTFT timing on the first **reasoning or answer** chunk. Previously, starting only on answer text could inflate decode speed because API token usage also includes reasoning. Chunk counts are approximate when the API omits usage.

The setup verified:

- Model file size and published SHA-256 matched.
- The model loaded with Metal GPU offload and an 8,192-token context.
- A real local API request returned “Local model is ready.”
- An MCP SDK client listed `ask_assistant`, called it through the stdio bridge, and received “MCP bridge is ready.”
- Node syntax and a reasoning-first streaming regression check passed.
- One short smoke benchmark recorded approximately **322 ms TTFT** and **26 tokens/second**. This is not a representative performance benchmark; results depend on prompt, model runtime, and hardware.

Editor-specific MCP activation and automatic tool selection still require verification in your own editor. A working API and bridge do not by themselves confirm editor integration.

## 6. Install Open WebUI for browser chat

Open WebUI is a browser interface to the same LM Studio API. It does not require Ollama or the Cursor MCP bridge. With Git authenticated and this repository cloned, run from its root on macOS or Linux:

```bash
bash scripts/setup_openwebui.sh
bash scripts/start_openwebui.sh
```

The setup script installs **Open WebUI 0.11.4** into `.local/open-webui/venv`. It uses an existing `uv` if available; otherwise it downloads uv's official installer and keeps uv inside `.local/open-webui/bin`. uv provides Python **3.11** without replacing macOS's system Python. Internet access is required for installation. Open WebUI's direct version is pinned; transitive dependencies are resolved by uv at installation time.

Keep LM Studio running as described in step 3. Open **http://127.0.0.1:3000**, create your own first administrator account, select **qwen3.8-27b**, and ask a question. Authentication remains enabled; your account and password are local to this Open WebUI installation. The first account is the administrator, so complete this step before inviting other users.

The launcher binds only to `127.0.0.1`, connects to `http://127.0.0.1:1234/v1`, and supplies `lm-studio` as a placeholder API key for the local server that does not require authentication. It disables the unused Ollama connection and selects `qwen3.8-27b` as the default model. If you enable authentication on LM Studio later, export `LMSTUDIO_API_KEY` with your actual key before starting the UI; keep it out of Git.

Chats, users, uploads, settings, the persistent session key, Python, and caches live under **`.local/open-webui/`**, excluded by `.gitignore`. Back up this entire directory while the server is stopped. Cloning the repository installs none of these automatically: run the setup script once, and rerun the start script after restarting your machine. Keep the start terminal open; **Ctrl+C** stops Open WebUI. There is no automatic login-start service.

Basic health check:

```bash
curl -fsS http://127.0.0.1:3000/health
```

This launcher uses offline mode to avoid automatic model downloads. Basic chat uses the already-running LM Studio model; local document embeddings, speech, and other features needing additional models require separate configuration. If the model list is empty, check LM Studio's `/v1/models` first, then check Open WebUI **Admin Panel → Settings → Connections** for the local URL. Saved settings can override initial environment defaults. If port 3000 is occupied, stop the existing service or change the launcher's port. A first-start import/migration can take longer than later starts.

Installation follows the official [Open WebUI Python/uv instructions](https://docs.openwebui.com/getting-started/quick-start/) and [environment configuration reference](https://docs.openwebui.com/reference/env-configuration/).

## 7. Start Qwen automatically at macOS login

After installing `lms` and downloading Qwen in step 2, run from the repository root in a normal Mac Terminal:

```bash
zsh scripts/start-qwen.sh
bash scripts/install_macos_startup.sh
```

The launcher reuses a matching `qwen3.8-27b` configuration, avoiding duplicate-identifier errors. It defaults to 32,768 tokens, full GPU offload, and one concurrent request. An idle mismatched model is unloaded and reloaded; a busy one is left running and setup stops with instructions. It starts the localhost API on port 1234 when it is not already responding. Python 3 and curl are required; `lms` is expected at `$HOME/.lmstudio/bin/lms`.

The installer creates a per-user LaunchAgent: startup occurs **after login**, not before login at system boot. No sudo is required. It copies the launcher to `~/Library/LaunchAgents/LocalLLM/start-qwen.sh`, generates `~/Library/LaunchAgents/com.kiran.local-qwen.plist` with your home directory, and activates it immediately. Failed attempts retry with a 30-second throttle. After success, the launcher exits while LM Studio keeps running; it does not continuously monitor the model or API.

The installed launcher survives moving the checkout. Rerun the installer after changing the repository script to update the installed copy. This starts Qwen and the API; Open WebUI and Cursor's MCP activation remain separate. The model uses approximately 16.8 GB plus runtime/context memory.

Verify startup and inspect logs:

```bash
launchctl print "gui/$(id -u)/com.kiran.local-qwen"
cat "$HOME/Library/Logs/LocalLLM/startup.log"
cat "$HOME/Library/Logs/LocalLLM/startup-error.log"
curl -fsS http://127.0.0.1:1234/v1/models
```

`last exit code = 0` indicates success; `state = not running` is normal after this one-shot launcher finishes. The API should list `qwen3.8-27b`. To run the job manually:

```bash
launchctl kickstart "gui/$(id -u)/com.kiran.local-qwen"
```

To disable automatic startup, unload the job and move its plist out of LaunchAgents:

```bash
launchctl bootout "gui/$(id -u)/com.kiran.local-qwen"
mv "$HOME/Library/LaunchAgents/com.kiran.local-qwen.plist" \
   "$HOME/Library/LaunchAgents/LocalLLM/com.kiran.local-qwen.plist.disabled"
```

This does not stop a running model. Use `lms server stop` and `lms daemon down` to stop it. Rerun the installer to enable startup again. For failures, inspect the error log and check the downloaded model, memory, Python, and `lms` installation.

Validation: shell syntax and plist checks passed; running the repository installer updated the installed job successfully; launchctl reported exit code 0; the API listed Qwen; and a real MCP call returned “MCP bridge is ready.” A full reboot was not performed.

## Troubleshooting and restarting

| Symptom | Resolution learned during setup |
| --- | --- |
| Git clone requests credentials or fails over SSH | Authenticate Git separately from the browser; use HTTPS with `gh auth setup-git`, or configure an SSH key. |
| `lms: command not found` | Add `$HOME/.lmstudio/bin` to PATH for the headless installation, or complete the desktop app's CLI setup. |
| `ggml_metal_init: failed to create command queue` in an agent sandbox | The sandboxed daemon could not initialize Metal. Stop that daemon and start `lms daemon up` from a normal host Terminal with the required permissions, then retry loading. This resolved the observed error. |
| Connection refused on port 1234 | Start the daemon, load the model, and start the server; check the server's port. |
| Model not found by API or bridge | Check `/v1/models` and load using the explicit `--identifier qwen3.8-27b`. |
| Benchmark requests a doubled `/v1` path | Give its `--base-url` the origin only; bridge `ASSISTANT_API_BASE` includes `/v1`. |
| Editor cannot find the bridge or Node | Open the repository root, run `npm ci`, and ensure the editor can resolve `node`. |
| Editing `.env` has no effect | Export the variables or update the editor MCP `env` values; the script does not load `.env` files. |
| Bridge appears idle after `npm start` | Connect an MCP client/editor; the bridge waits for stdio protocol messages. |
| Requests time out | Confirm API inference works first, then adjust the 120,000 ms bridge timeout if your workload needs more time. |

After restarting the Mac, the login job in step 7 starts the runtime if installed. Otherwise run `zsh scripts/start-qwen.sh` manually. Run that launcher again after stopping the daemon. To stop the local API:

```bash
lms server stop
```

To stop the runtime as well:

```bash
lms daemon down
```

## How we used ChatGPT and Codex

We used ChatGPT and Codex for a conversational workflow: discuss the goal, choose the model, perform setup, check results, and document the outcome. The user chose **Qwen3.8-27B** and directed the changes.

Codex read every project-owned file through the signed-in GitHub browser when command-line Git authentication was unavailable, reconstructed a local working snapshot, checked the Mac, installed llmster and the CLI, downloaded and verified the model, and diagnosed the Metal sandbox failure. It then aligned the model, endpoint, and timeout across the bridge and editor configurations, corrected reasoning-aware benchmark timing, and verified actual API and MCP responses.

The changes were submitted in [pull request #2](https://github.com/kiranrbharadwaj/LocalLLM_Setup/pull/2), including this walkthrough. The runtime installation and model download are local machine state; cloning the repository does not install them. ChatGPT and Codex assisted with setup and verification; **Qwen3.8-27B** serves the local model responses.
