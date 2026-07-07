# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Local Stack is a fully local, Docker-based AI stack that mimics the Anthropic Claude API using open-source LLMs (Ollama + LiteLLM + Open WebUI). No cloud dependency required.

## Architecture

```
[ Open WebUI ]  --(OpenAI API)--> [ LiteLLM ]  --(Ollama API)--> [ Ollama ]
    :3000                              :4000                         :11434
```

Four Docker Compose services:

| Service      | Port  | Purpose                                    |
|-------------|-------|--------------------------------------------|
| `ollama`    | 11434 | Local model runtime (hosts models)          |
| `model-init`| --    | One-shot container that pulls missing models (auto-exits) |
| `litellm`   | 4000  | Claude-compatible API proxy (model routing)  |
| `open-webui`| 3000  | Web frontend (ChatGPT/Claude-like UI)        |

Model routing (defined in `docker/litellm-config.yaml`):

| Model Name    | Backend Model            | Claude Tier    |
|--------------|--------------------------|----------------|
| `deepseek-v4`| ollama/deepseek-v4-flash | Opus ersatz    |
| `chat`       | ollama/llama3            | Sonnet         |
| `fast`       | ollama/phi3              | Haiku          |
| `coder`      | ollama/deepseek-coder    | Coding         |

The LiteLLM config is baked into the custom Docker image (`docker/litellm.Dockerfile`) to avoid bind mount complexity. **To change model routing, you must rebuild the `litellm` image** (see Adding/Changing Models below).

## Quick Start

```bat
copy env.example docker\.env
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

Open http://localhost:3000

## Common Commands

**Build and start all services:**
```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

**Rebuild a specific service after changes:**
```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build <service-name>
```

**View logs:**
```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env logs -f
docker compose -f docker\docker-compose.yml --env-file docker\.env logs -f litellm
```

**Stop services:**
```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env down
```

**Stop and delete volumes (wipes model cache and WebUI data):**
```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env down -v
```

**Verify the compose config:**
```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env config
```

**Verify Ollama is serving models:**
```bat
curl http://localhost:11434/api/tags
```

**Verify LiteLLM proxy is working:**
```bat
curl http://localhost:4000/models
curl http://localhost:4000/deepseek-v4/chat/completions -H "Content-Type: application/json" -d "{\"messages\":[{\"role\":\"user\",\"content\":\"hello\"}],\"max_tokens\":10}"
```

**Run end-to-end smoke test:**
```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-test.ps1
```

**Run pre-commit hooks manually:**
```bat
pre-commit run --all-files
```

**Install pre-commit hooks:**
```bat
pip install pre-commit commitizen
pre-commit install
pre-commit install --hook-type pre-push
```

**GPU test (requires nvidia-container-toolkit):**
```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

## Adding / Changing Models

Changing the model stack requires coordinated changes in three places:

1. **`docker/.env`** — Add/remove model names in the `MODELS` variable (space-separated). The `model-init` container pulls whichever models are listed here and missing locally.
2. **`docker/litellm-config.yaml`** — Add/update the `model_list` entries. The `model_name` is what clients request; the `model` field must match the Ollama model tag.
3. **Rebuild `litellm`** — Because the config is baked into the image:
   ```bat
   docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build litellm
   ```

After step 3, `model-init` will auto-pull new models on next `up` (it only pulls what's missing).

**To test a new model end-to-end without rebuilding**, you can temporarily call Ollama directly:
```bat
curl http://localhost:11434/api/generate -d "{\"model\":\"<model-name>\",\"prompt\":\"hello\"}"
```

## Claude Code Integration

To point Claude Code at the local stack, set env vars in `~/.claude/settings.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4000",
    "ANTHROPIC_API_KEY": "no-key",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "chat",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "fast"
  }
}
```

The project-local `claude/settings.json` ships with these defaults already set — this is the recommended approach for repo-level overrides. (The `claude/` directory follows the Claude Code convention for project-local settings.)

## Environment Variables

The compose file is fully parameterized. All variables have safe defaults — see `env.example`. Key ones:

| Variable | Default | Purpose |
|----------|---------|---------|
| `COMPOSE_PROJECT_NAME` | `claude-local-stack` | Docker project/network prefix |
| `MODELS` | `deepseek-v4-flash deepseek-coder llama3 phi3` | Models pulled by `model-init` |
| `OLLAMA_NUM_PARALLEL` | `2` | Ollama parallel request handling |
| `OLLAMA_MAX_LOADED_MODELS` | `2` | Max models kept in memory |

The file `docker/.env` is gitignored — each developer copies from `env.example` and customizes.

## Pre-commit & Commit Convention

- Uses [Commitizen](https://commitizen-tools.github.io/commitizen/) (Conventional Commits enforced on commit and pre-push).
- Commits directly to `main` are blocked by `no-commit-to-branch`.
- Pre-commit hooks check JSON/YAML/TOML validity, trailing whitespace, end-of-file fixer, large files, merge conflicts, private keys, and JSON pretty-format.
- `.pre-commit-config.yaml` previously had duplicate entries for `check-toml` and `check-symlinks` — these have been cleaned up.

## Key Files

| File | Purpose |
|------|---------|
| `docker/docker-compose.yml` | Service orchestration |
| `docker/litellm-config.yaml` | Model name routing |
| `docker/litellm.Dockerfile` | LiteLLM image with baked config |
| `env.example` | Template for `docker/.env` |
| `claude/settings.json` | Local Claude Code endpoint config |
| `.pre-commit-config.yaml` | Git hook configuration |
| `.github/workflows/ci.yml` | GitHub CI (pre-commit + compose config) |
| `.github/dependabot.yml` | Dependabot schedules and PR labeling |
| `.github/labels.json` | Source of truth for repository labels |
| `.github/workflows/label-sync.yml` | Creates/updates labels via CI |
| `scripts/smoke-test.ps1` | Local service health smoke test |
