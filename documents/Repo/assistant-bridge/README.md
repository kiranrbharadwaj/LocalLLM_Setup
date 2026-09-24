# Assistant Bridge (MCP Server)

Lets Cursor call your AI assistant as a tool.

## Setup
cd documents/Repo/assistant-bridge
npm install

Edit .cursor/mcp.json to set your real API base URL and key.

## Usage in Cursor
> "Ask the assistant why this race condition keeps happening."

Cursor detects the ask_assistant tool and calls it automatically.
