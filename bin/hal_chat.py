#!/usr/bin/env python3
"""
Simple chat wrapper for HAL starter.
- Loads HAL system prompt from HAL.md
- Loads model from config/hal.yaml (fallback to hal.example.yaml or default)
- Sends prompt to local Ollama via subprocess (if available)

Usage:
    bin/hal --chat "your prompt"
"""

import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # minimal fallback
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
HAL_PATH = ROOT / "HAL.md"
CONFIG_PATH = ROOT / "config" / "hal.yaml"
CONFIG_EXAMPLE = ROOT / "config" / "hal.example.yaml"


def load_config():
    cfg = {"backend": "local", "model": "llama2:13b"}
    path = CONFIG_PATH if CONFIG_PATH.exists() else CONFIG_EXAMPLE
    if yaml and path.exists():
        with open(path) as f:
            cfg.update(yaml.safe_load(f) or {})
    return cfg


def load_system_prompt():
    return HAL_PATH.read_text(encoding="utf-8")


def run_ollama(model: str, system: str, prompt: str):
    cmd = ["ollama", "run", model, "--system", system, prompt]
    try:
        res = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return res.stdout.strip()
    except FileNotFoundError:
        return "[error] ollama not found; install or set backend differently"
    except subprocess.CalledProcessError as e:
        return f"[error] ollama failed: {e.stderr.strip()}"


def main():
    if len(sys.argv) < 2:
        print("Usage: bin/hal --chat \"prompt\"")
        sys.exit(1)

    user_prompt = " ".join(sys.argv[1:])
    cfg = load_config()
    system = load_system_prompt()

    if cfg.get("backend") == "local":
        model = cfg.get("model", "llama2:13b")
        response = run_ollama(model, system, user_prompt)
        print(response)
    else:
        print("[info] Only local (ollama) backend stubbed; set backend: local in config/hal.yaml")


if __name__ == "__main__":
    main()
