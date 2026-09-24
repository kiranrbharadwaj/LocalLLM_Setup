#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const API_BASE   = process.env.ASSISTANT_API_BASE   ?? "http://localhost:8080/v1";
const API_KEY    = process.env.ASSISTANT_API_KEY    ?? "";
const MODEL      = process.env.ASSISTANT_MODEL      ?? "assistant";
const TIMEOUT_MS = Number(process.env.ASSISTANT_TIMEOUT_MS ?? 60_000);

function log(msg) {
  process.stderr.write(`[assistant-bridge] ${msg}\n`);
}

async function callAssistant(prompt, context) {
  const fullPrompt = context
    ? `## Context\n${context}\n\n## Question\n${prompt}`
    : prompt;

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    log(`→ Asking: "${prompt.slice(0, 120)}${prompt.length > 120 ? "…" : ""}"`);

    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(API_KEY ? { Authorization: `Bearer ${API_KEY}` } : {}),
      },
      body: JSON.stringify({
        model: MODEL,
        messages: [{ role: "user", content: fullPrompt }],
      }),
    });

    if (!res.ok) {
      const body = await res.text().catch(() => "(no body)");
      throw new Error(`API ${res.status}: ${body}`);
    }

    const data = await res.json();
    const text =
      data.choices?.[0]?.message?.content ??
      data.message?.content ??
      data.content ??
      JSON.stringify(data);

    log(`← Response (${text.length} chars)`);
    return text;
  } finally {
    clearTimeout(timer);
  }
}

const server = new Server(
  { name: "assistant-bridge", version: "1.0.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "ask_assistant",
      description:
        "Ask the AI assistant for help with coding, debugging, architecture, " +
        "or design questions. Pass relevant code or errors in 'context'.",
      inputSchema: {
        type: "object",
        properties: {
          prompt: {
            type: "string",
            description: "Your question or request",
          },
          context: {
            type: "string",
            description: "Optional: code, error trace, or background info",
          },
        },
        required: ["prompt"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "ask_assistant") {
    try {
      const text = await callAssistant(args.prompt, args.context);
      return { content: [{ type: "text", text }] };
    } catch (err) {
      const msg = err.name === "AbortError"
        ? `Timed out after ${TIMEOUT_MS / 1000}s.`
        : `Failed: ${err.message}`;
      log(`✗ ${msg}`);
      return { content: [{ type: "text", text: msg }], isError: true };
    }
  }

  return {
    content: [{ type: "text", text: `Unknown tool: ${name}` }],
    isError: true,
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
log("MCP server ready on stdio.");
