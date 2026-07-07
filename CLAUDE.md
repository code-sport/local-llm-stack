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

Claude Code is JetBrains' AI assistant for code. You can configure it to use your local Claude Local Stack instead of the cloud API, enabling private, fully offline AI-assisted development.

### Prerequisites

- Claude Code plugin installed in your JetBrains IDE (IntelliJ, PyCharm, WebStorm, etc.)
- Claude Local Stack running locally (`docker compose up -d`)
- LiteLLM service accessible at `http://localhost:4000`

### Option 1: Global Configuration (All Projects)

For all your projects to use the local stack, configure your **global** Claude settings:

1. **Locate the settings file:**
   - Windows: `%USERPROFILE%\.claude\settings.json`
   - macOS/Linux: `~/.claude/settings.json`

2. **Create or edit the file** with these environment variables:

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

3. **Restart your IDE** to apply the changes.

### Option 2: Project-Level Configuration (Recommended)

For development on this project, use the **project-local** `claude/settings.json` file. This repository already ships with the correct settings:

**File: `claude/settings.json`**
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

The `claude/` directory follows the Claude Code convention for project-level settings and overrides any global configuration.

### Model Tier Mapping

The local stack routes Claude Code's model requests as follows:

| Claude Tier | Model Name   | Backend Model         | Use Case                          |
|-------------|--------------|----------------------|-----------------------------------|
| **Opus**    | `deepseek-v4`| deepseek-v4-flash    | Complex reasoning, advanced tasks |
| **Sonnet**  | `chat`       | llama3                | General purpose coding            |
| **Haiku**   | `fast`       | phi3                  | Quick completions, lightweight    |

You can customize these mappings by editing:
1. `docker/litellm-config.yaml` (model routing)
2. Your `claude/settings.json` or `~/.claude/settings.json` (model selection)

### Verifying the Connection

**From the IDE:**
1. Open Claude Code in your JetBrains IDE (Command Palette / Ctrl+Shift+A → "Claude Code")
2. Ask a simple question: `What is 2+2?`
3. If it works, you're connected to the local stack
4. If it fails, check the IDE logs and troubleshooting tips below

**From the command line:**
```powershell
# Verify LiteLLM is running
curl http://localhost:4000/models

# Verify a model is responding
curl http://localhost:4000/chat/completions `
  -H "Content-Type: application/json" `
  -d '{"messages":[{"role":"user","content":"test"}],"max_tokens":10,"model":"chat"}'
```

### Using Different Model Tiers

Once connected, Claude Code automatically selects the appropriate tier:

- **For complex tasks:** Use "More" or high-complexity queries → defaults to `deepseek-v4` (Opus)
- **For standard tasks:** Normal queries → defaults to `chat` (Sonnet)
- **For quick completions:** Use "Fast" or lightweight requests → defaults to `fast` (Haiku)

Note: You cannot explicitly choose models in Claude Code's UI, but the configured defaults control which backend processes your request.

### Switching Between Local and Cloud Claude

**To use the cloud Claude API temporarily:**

1. Delete or rename your `claude/settings.json` or `~/.claude/settings.json`
2. Restart your IDE
3. Claude Code will use default cloud credentials (if set up)

**To return to local:**

1. Restore the `claude/settings.json` file
2. Restart your IDE

**Alternative: Environment Variables**

You can also control this via IDE environment variables without editing files:

```powershell
# Use local stack
$env:ANTHROPIC_BASE_URL = "http://localhost:4000"
$env:ANTHROPIC_API_KEY = "no-key"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "deepseek-v4"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "chat"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "fast"

# Then restart the IDE
```

### Troubleshooting

**"Connection refused" or "timeout":**
- Verify the stack is running: `docker compose -f docker\docker-compose.yml --env-file docker\.env ps`
- Check LiteLLM logs: `docker compose -f docker\docker-compose.yml --env-file docker\.env logs litellm`
- Ensure port 4000 is accessible: `curl http://localhost:4000/models`

**"Invalid API key" or "authorization failed":**
- The `ANTHROPIC_API_KEY` value does not matter for local use; any non-empty string works
- Verify `ANTHROPIC_BASE_URL` is exactly `http://localhost:4000` (not `https` or a different port)

**IDE shows old configuration:**
- Fully restart the IDE (not just close and reopen)
- Check IDE logs: Help → Show Log in Explorer/Finder
- Verify the `settings.json` file is valid JSON (no trailing commas, etc.)

**Models are slow or timing out:**
- Check available models: `curl http://localhost:11434/api/tags`
- Verify model is loaded: `docker compose -f docker\docker-compose.yml --env-file docker\.env logs ollama`
- Adjust `OLLAMA_MAX_LOADED_MODELS` in `docker/.env` to load fewer models if memory is constrained
- Ensure sufficient CPU/GPU resources are available to Docker

### Performance Tips

1. **Keep only frequently-used models loaded** — Edit `docker/.env` and reduce the `MODELS` list to save memory
2. **Use GPU acceleration** — See "GPU test" in Common Commands if you have NVIDIA GPU
3. **Monitor resource usage** — Run `docker stats` to see CPU/memory consumption
4. **Pre-warm models** — Make a quick request to each model before heavy development sessions

### Related Documentation

- [API Access & Keys](./docs/api-access.md) — API authentication and token management
- [Models & Configuration](./docs/models.md) — Model routing and customization
- [Troubleshooting](./docs/troubleshooting.md) — Common issues and solutions

## GitHub Gist Usage (Optional)

This project can be documented/shared through GitHub Gist when teammates need quick setup help.

Recommended approach:

- Share sanitized snippets only.
- Prefer sharing `env.example` instead of a real `docker/.env` file.
- Remove tokens, credentials, and any other secrets before uploading.
- Prefer secret/private gists for team-internal collaboration.
- Ask users to copy gist values into local files such as `docker/.env` and `claude/settings.json`.
- If troubleshooting, include only the minimal logs/config needed for reproduction.

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
| `docs/README.md` | Documentation index for detailed guides |
| `docs/claude-code-setup.md` | Complete Claude Code setup and usage guide |
| `docs/architecture.md` | Architecture overview and component descriptions |
| `docs/gist-usage.md` | Safe GitHub Gist sharing workflow |
| `docs/configuration.md` | Configuration guidance and variable references |
| `docs/models.md` | Model routing and rebuild workflow |
| `docs/troubleshooting.md` | Validation checks and diagnostics |
| `env.example` | Template for `docker/.env` |
| `claude/settings.json` | Local Claude Code endpoint config |
| `.pre-commit-config.yaml` | Git hook configuration |
| `.github/workflows/ci.yml` | GitHub CI (pre-commit + compose config) |
| `.github/dependabot.yml` | Dependabot schedules and PR labeling |
| `.github/labels.json` | Source of truth for repository labels |
| `.github/workflows/label-sync.yml` | Creates/updates labels via CI |
| `scripts/smoke-test.ps1` | Local service health smoke test |
