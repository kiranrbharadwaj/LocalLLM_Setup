# Assistant Bridge (MCP Server)

Exposes the `ask_assistant` tool to Cursor and VS Code. The tool sends your question and optional code context to Qwen3.8-27B through LM Studio’s local API.

## Setup

From the repository root, install the locked dependencies:

```bash
cd documents/Repo/assistant-bridge
npm ci
```

Use Node.js 18 or newer. Load Qwen3.8-27B in LM Studio with identifier `qwen3.8-27b`, then start the server on `127.0.0.1:1234`; see the root README for commands.

Open the repository root in Cursor or VS Code. The project configurations in `.cursor/mcp.json` and `.vscode/mcp.json` start the bridge with Node and pass the local endpoint and model identifier. Enable the assistant MCP server in the editor when prompted. Node must be available to the editor’s process.

## Configuration

The bridge reads process environment variables. `.env.example` documents them; the bridge does not automatically load a `.env` file.

| Variable | Default |
| --- | --- |
| `ASSISTANT_API_BASE` | `http://127.0.0.1:1234/v1` |
| `ASSISTANT_MODEL` | `qwen3.8-27b` |
| `ASSISTANT_API_KEY` | Empty; set it if your local server requires authentication |
| `ASSISTANT_TIMEOUT_MS` | `120000` |

## Usage

Ask the editor to use `ask_assistant`, for example: “Ask the assistant why this race condition keeps happening,” and provide relevant code as context. Tool invocation depends on the editor and its current tool settings.

The bridge communicates over stdio; diagnostic logs go to stderr. Running `npm start` directly waits for an MCP client.
