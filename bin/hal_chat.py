#!/usr/bin/env python3
"""
Simple chat wrapper for HAL starter.
- Loads HAL system prompt from HAL.md
- Loads model from config/hal.yaml (fallback to hal.example.yaml or default)
- Sends prompt to local Ollama via subprocess (if available)

Usage:
    bin/hal --chat "your prompt"
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:  # minimal fallback
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
HAL_PATH = ROOT / "HAL.md"
CONFIG_PATH = ROOT / "config" / "hal.yaml"
CONFIG_EXAMPLE = ROOT / "config" / "hal.example.yaml"


def load_config():
    cfg = {
        "backend": "anthropic",
        "anthropic_model": "claude-3-haiku-20240307",
        "ollama_model": "llama2:13b",
    }
    path = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_EXAMPLE
    if yaml and path.exists():
        with open(path) as f:
            data = yaml.safe_load(f) or {}
            if isinstance(data, dict):
                cfg.update(data)
    return cfg


def load_system_prompt():
    return HAL_PATH.read_text(encoding="utf-8")


def run_ollama(model: str, system: str, prompt: str):
    # For ollama versions without --system, prepend system prompt.
    combined = system.strip() + "\n\n" + prompt.strip()
    cmd = ["ollama", "run", model]
    try:
        res = subprocess.run(cmd, input=combined, check=True, capture_output=True, text=True)
        return res.stdout.strip()
    except FileNotFoundError:
        return "[error] ollama not found; install or set backend differently"
    except subprocess.CalledProcessError as e:
        return f"[error] ollama failed: {e.stderr.strip()}"


def run_anthropic(model: str, system: str, prompt: str):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "[error] ANTHROPIC_API_KEY not set"
    import http.client
    import json

    body = {
        "model": model,
        "max_tokens": 512,
        "system": system,
        "messages": [{"role": "user", "content": prompt}]
    }

    conn = http.client.HTTPSConnection("api.anthropic.com")
    conn.request(
        "POST",
        "/v1/messages",
        body=json.dumps(body),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
    )
    resp = conn.getresponse()
    data = resp.read()
    if resp.status != 200:
        return f"[error] anthropic {resp.status}: {data.decode()}"
    parsed = json.loads(data)
    # Expect content as list of blocks with type 'text'
    chunks = []
    for block in parsed.get("content", []):
        if block.get("type") == "text":
            chunks.append(block.get("text", ""))
    return "\n".join(chunks).strip()


def main():
    if len(sys.argv) < 2:
        print("Usage: bin/hal --chat \"prompt\"")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    cfg = load_config()
    system = load_system_prompt()
    backend = cfg.get("backend", "anthropic")

    if backend == "ollama":
        model = cfg.get("ollama_model", "llama2:13b")
        response = run_ollama(model, system, user_prompt)
        print(response)
    elif backend == "anthropic":
        model = cfg.get("anthropic_model", "claude-3-haiku-20240307")
        response = run_anthropic(model, system, user_prompt)
        print(response)
    else:
        print(f"[info] Unsupported backend '{backend}'. Set backend: anthropic|ollama in config/hal.yaml")


if __name__ == "__main__":
    main()
