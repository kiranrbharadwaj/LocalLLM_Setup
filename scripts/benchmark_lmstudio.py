#!/usr/bin/env python3
"""Benchmark TTFT and decode speed against an LM Studio OpenAI-compatible API."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "http://127.0.0.1:1234"
DEFAULT_MODEL = "qwen3.8-27b"
DEFAULT_PROMPT = (
    "Write a short paragraph explaining quantization in local LLMs."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Stream a chat completion from LM Studio and report TTFT, "
            "wall time, and approximate decode speed."
        )
    )
    parser.add_argument(
        "--base-url",
        default=DEFAULT_BASE_URL,
        help=f"LM Studio API base URL (default: {DEFAULT_BASE_URL})",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Model id as shown in LM Studio (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help="User message to send",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=200,
        help="max_tokens for the completion (default: 200)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Sampling temperature (default: 0.7)",
    )
    parser.add_argument(
        "--warmup",
        type=int,
        default=0,
        metavar="N",
        help="Run N discarded warmup requests before the timed run (default: 0)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="HTTP timeout in seconds (default: 120)",
    )
    parser.add_argument(
        "--check-memory",
        action="store_true",
        help="Print macOS memory_pressure and LM Studio process RSS before the run",
    )
    parser.add_argument(
        "--show-response",
        action="store_true",
        help="Print the generated text after the metrics summary",
    )
    return parser.parse_args()


def chat_completions_url(base_url: str) -> str:
    return base_url.rstrip("/") + "/v1/chat/completions"


def optional_memory_snapshot() -> None:
    """Best-effort macOS memory / LM Studio RSS check; never fails the benchmark."""
    print("--- memory (optional) ---")
    try:
        result = subprocess.run(
            ["memory_pressure"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        out = (result.stdout or result.stderr or "").strip()
        if out:
            # Keep it short: first few non-empty lines are usually enough.
            lines = [ln for ln in out.splitlines() if ln.strip()][:8]
            print("\n".join(lines))
        else:
            print("memory_pressure: no output")
    except FileNotFoundError:
        print("memory_pressure: not available on this system")
    except Exception as exc:  # noqa: BLE001 — diagnostic only
        print(f"memory_pressure: skipped ({exc})")

    try:
        result = subprocess.run(
            ["ps", "-axo", "rss,comm"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        matches: list[tuple[int, str]] = []
        for line in result.stdout.splitlines()[1:]:
            parts = line.strip().split(None, 1)
            if len(parts) != 2:
                continue
            rss_kb_s, comm = parts
            if "lm studio" in comm.lower() or "lmstudio" in comm.lower():
                try:
                    matches.append((int(rss_kb_s), comm))
                except ValueError:
                    continue
        if matches:
            total_mb = sum(rss for rss, _ in matches) / 1024.0
            print(f"LM Studio process RSS (sum): {total_mb:.0f} MB")
            for rss, comm in sorted(matches, reverse=True)[:5]:
                print(f"  {rss / 1024.0:.0f} MB  {comm}")
        else:
            print("LM Studio process RSS: no matching processes found")
    except Exception as exc:  # noqa: BLE001 — diagnostic only
        print(f"process RSS: skipped ({exc})")
    print()


def stream_chat_completion(
    *,
    url: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    timeout: float,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "max_tokens": max_tokens,
        "temperature": temperature,
        # Ask providers that support it to include usage on the final chunk.
        "stream_options": {"include_usage": True},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t0 = time.perf_counter()
    ttft: float | None = None
    chunk_tokens = 0
    usage_completion_tokens: int | None = None
    text_parts: list[str] = []

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue

            choices = obj.get("choices") or []
            delta = choices[0].get("delta", {}) if choices else {}
            content = delta.get("content") or ""
            reasoning = delta.get("reasoning_content") or delta.get("reasoning") or ""
            if content or reasoning:
                if ttft is None:
                    ttft = time.perf_counter() - t0
                chunk_tokens += 1
            if content:
                text_parts.append(content)

            usage = obj.get("usage")
            if usage and usage.get("completion_tokens") is not None:
                usage_completion_tokens = int(usage["completion_tokens"])

    t1 = time.perf_counter()
    elapsed = t1 - t0
    tokens = (
        usage_completion_tokens
        if usage_completion_tokens is not None
        else chunk_tokens
    )
    token_source = (
        "usage.completion_tokens"
        if usage_completion_tokens is not None
        else "stream chunks (approx)"
    )

    return {
        "ttft": ttft,
        "elapsed": elapsed,
        "tokens": tokens,
        "token_source": token_source,
        "text": "".join(text_parts),
    }


def print_summary(result: dict[str, Any], *, label: str = "timed run") -> None:
    ttft = result["ttft"]
    elapsed = result["elapsed"]
    tokens = result["tokens"]
    decode_time = elapsed - (ttft or 0.0)

    print(f"--- {label} ---")
    if ttft is not None:
        print(f"TTFT:              {ttft * 1000:.0f} ms")
    else:
        print("TTFT:              n/a (no content or reasoning chunks received)")
    print(f"Total wall time:   {elapsed:.2f} s")
    print(f"Decode time:       {decode_time:.2f} s  (wall − TTFT)")
    print(f"Completion tokens: {tokens}  [{result['token_source']}]")
    if tokens > 0 and decode_time > 0:
        print(f"Decode speed:      {tokens / decode_time:.1f} tok/s (approx)")
    else:
        print("Decode speed:      n/a")


def main() -> int:
    args = parse_args()
    url = chat_completions_url(args.base_url)

    print(f"Endpoint: {url}")
    print(f"Model:    {args.model}")
    print(f"Prompt:   {args.prompt[:80]}{'…' if len(args.prompt) > 80 else ''}")
    print(f"max_tokens={args.max_tokens}  temperature={args.temperature}  warmup={args.warmup}")
    print()

    if args.check_memory:
        optional_memory_snapshot()

    try:
        for i in range(args.warmup):
            stream_chat_completion(
                url=url,
                model=args.model,
                prompt=args.prompt,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                timeout=args.timeout,
            )
            print(f"Warmup {i + 1}/{args.warmup} done (discarded)")
        if args.warmup:
            print()

        result = stream_chat_completion(
            url=url,
            model=args.model,
            prompt=args.prompt,
            max_tokens=args.max_tokens,
            temperature=args.temperature,
            timeout=args.timeout,
        )
    except urllib.error.URLError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        print(
            "Is LM Studio running with the local server enabled "
            f"at {args.base_url}?",
            file=sys.stderr,
        )
        return 1
    except TimeoutError:
        print("Request timed out.", file=sys.stderr)
        return 1

    print_summary(result)
    if args.show_response and result["text"]:
        print()
        print("--- response ---")
        print(result["text"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
