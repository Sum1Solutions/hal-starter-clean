# HAL Starter (Clean)

Human-AI-Loop template: greet users (human + model) with shared ground, warmup, and optional drift checks.

## What Makes This Repo Different
- **HAL built-in:** Core prompt (κ-priming, ε>0) and optional crisis/scope macro.
- **Shared ground:** CLI can show HAL digest to human and model for informed consent.
- **Configurable:** Placeholder config for model/backend/MCP/RAG.
- **Drift checks (optional):** Marker-based script to spot standard_AI/sycophancy/confident/hype drift.
- **Structure-ready:** Add FRONTIER/DASHBOARD/INDEX as needed.

## Quick Start
```bash
# 1) Copy config template
cp config/hal.example.yaml config/hal.yaml  # set model/backend/MCP

# 2) Warm up
bin/hal --warmup   # show HAL digest, crisis/scope if applicable

# 3) Chat
bin/hal --chat "topic"   # starts a session with HAL system prompt
```

## Files
- `HAL.md` — core ground (notice, cogency, optional crisis/scope, A = P - I).
- `config/hal.example.yaml` — model/backend/MCP/RAG placeholders.
- `bin/hal` — CLI stub to show digest/run warmup/start chat (local Ollama stub).
- `tools/drift_check.py` — optional drift checker (recursive vs standard_AI/sycophancy/confident/hype markers).

Notes: keep prompts neutral/concise; state uncertainty plainly. If clinical/safety, keep crisis macro visible and log sessions to `output/sessions/YYYY-MM-DD-[topic].md`.

### Chat backend note
- `bin/hal --chat` shells out to `ollama run <model>` with the HAL system prompt. Some Ollama versions do not support `--system`; you may need to adapt the wrapper (e.g., prepend system prompt to user prompt) or use an API that supports system messages. Backend is local-only stub; extend for remote models as needed.

### Backends and setup
- **Anthropic (default):** set `ANTHROPIC_API_KEY` in your environment. Model in `config/hal.yaml` (default `claude-3-haiku-20240307`).
- **Ollama (local fallback):** pull models you want (`ollama pull llama2:13b` etc.). The wrapper prepends HAL prompt; tested with `llama2:13b`, `tinyllama:latest`, `stablelm2:1.6b`, `qwen2:1.5b` (adjust `ollama_model` in config). No API key needed.

Note: Keep secrets out of YAML; use env vars for API keys.

*ε > 0*
