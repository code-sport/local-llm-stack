# Claude Local Stack

A fully local, Docker-based AI stack that mimics Anthropic Claude using open-source models.

This repository contains only the local AI stack and related configuration/docs — no separate application backend is included.

## ✨ Features

- ✅ Local LLM hosting (Ollama)
- ✅ Claude-compatible API (LiteLLM proxy)
- ✅ Web UI (Open WebUI - similar to ChatGPT/Claude)
- ✅ Optional GPU acceleration (explicit opt-in)
- ✅ Model routing (chat / coding / fast)
- ✅ Idempotent model initialization
- ✅ Docker Compose ready
- ✅ Gist-friendly config sharing workflow

---

## 🚀 Quick Start

```bat
copy env.example docker\.env
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

Open the UI:

👉 http://localhost:3000

---

## 📚 Documentation

- [Documentation Index](docs/README.md)
- [GitHub Gist Usage](docs/gist-usage.md)
- [Configuration](docs/configuration.md)
- [Model Routing](docs/models.md)
- [Troubleshooting](docs/troubleshooting.md)

---

## 📝 Share Config via GitHub Gist

For the complete guide, see [GitHub Gist Usage](docs/gist-usage.md).

---

## 🧠 Architecture

```
[ Open WebUI ]
        │
        ▼
[ LiteLLM (API Proxy) ]
        │
        ▼
[ Ollama (Local Models) ]
```

---

## 📦 Included Services

| Service      | Port  | Description |
|-------------|------|------------|
| Ollama       | 11434 | Local model runtime |
| LiteLLM      | 4000  | Claude/OpenAI compatible API |
| Open WebUI   | 3000  | Web frontend |

---

## 🤖 Model Overview

| Model Name        | Purpose |
|-----------------|--------|
| chat            | General chat (Llama 3) |
| coder           | Coding tasks (DeepSeek Coder) |
| fast            | Lightweight / fast responses (Phi-3) |
| deepseek-v4     | Advanced reasoning |

---

## 🔁 Model Initialization

Models are automatically downloaded on first startup using a dedicated init container.

- ✅ Only missing models are downloaded
- ✅ Stored in Docker volume
- ✅ Survive restarts

---

## 🔧 Environment Variables (`docker/.env`)

`docker/docker-compose.yml` is fully parameterized via environment variables.

### Required (fast start)

| Variable | Description | Default |
|---|---|---|
| `COMPOSE_PROJECT_NAME` | Compose project name (containers/network/volumes) | `claude-local-stack` |
| `OLLAMA_PORT` | External/internal Ollama port | `11434` |
| `LITELLM_PORT` | External/internal LiteLLM port | `4000` |
| `WEBUI_PORT` | External Open WebUI port | `3000` |
| `OPENAI_API_BASE_URL` | Open WebUI target URL (usually LiteLLM service) | `http://litellm:4000` |
| `OPENAI_API_KEY` | API key used by Open WebUI against LiteLLM | `dummy` |
| `MODELS` | Space-separated models pulled/checked by `model-init` | `deepseek-v4-flash deepseek-coder llama3 phi3` |

### Optional (tuning and overrides)

| Variable | Description | Default |
|---|---|---|
| `RESTART_POLICY` | Restart policy for long-running services | `unless-stopped` |
| `OLLAMA_IMAGE` | Ollama image with tag | `ollama/ollama:0.11.6` |
| `OLLAMA_NUM_PARALLEL` | Ollama parallel request handling | `2` |
| `OLLAMA_MAX_LOADED_MODELS` | Max loaded models in memory | `2` |
| `OLLAMA_HEALTHCHECK_INTERVAL` | Healthcheck interval | `5s` |
| `OLLAMA_HEALTHCHECK_RETRIES` | Healthcheck retries | `10` |
| `MODEL_INIT_RESTART` | Restart behavior for `model-init` | `no` |
| `LITELLM_IMAGE` | LiteLLM image with tag | `claude-local-stack-litellm:local` |
| `LITELLM_HEALTHCHECK_INTERVAL` | Healthcheck interval for LiteLLM | `10s` |
| `LITELLM_HEALTHCHECK_TIMEOUT` | Healthcheck timeout for LiteLLM | `5s` |
| `LITELLM_HEALTHCHECK_RETRIES` | Healthcheck retries for LiteLLM | `12` |
| `WEBUI_IMAGE` | Open WebUI image with tag | `ghcr.io/open-webui/open-webui:v0.6.27` |
| `WEBUI_CONTAINER_PORT` | Internal container port for Open WebUI | `8080` |
| `WEBUI_HEALTHCHECK_INTERVAL` | Healthcheck interval for Open WebUI | `10s` |
| `WEBUI_HEALTHCHECK_TIMEOUT` | Healthcheck timeout for Open WebUI | `5s` |
| `WEBUI_HEALTHCHECK_RETRIES` | Healthcheck retries for Open WebUI | `12` |
| `NVIDIA_VISIBLE_DEVICES` | GPU visibility inside containers (leave empty for CPU-only) | `` |

### Fast start from template

```bat
copy env.example docker\.env
docker compose -f docker\docker-compose.yml --env-file docker\.env config
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

## ⚙️ Claude Code Integration

Configure:

`~/.claude/settings.json`

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4000",
    "ANTHROPIC_API_KEY": "dummy",

    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "chat",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "fast"
  }
}
```

## ✅ Smoke Test

After startup, run a quick end-to-end availability check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-test.ps1
```

Optional retries/timing override:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-test.ps1 -MaxAttempts 40 -DelaySeconds 2
```

---

## 🖥 GPU Support

Requires:

- NVIDIA GPU
- nvidia-container-toolkit

Test:

```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

Start stack with GPU reservation enabled:

```bat
copy env.example docker\.env
docker compose -f docker\docker-compose.yml -f docker\docker-compose.gpu.yml --env-file docker\.env up -d --build
```

---

## 📁 Project Structure

```
claude-local-stack/
├── docs/
│   ├── README.md
│   ├── gist-usage.md
│   ├── configuration.md
│   ├── models.md
│   └── troubleshooting.md
├── env.example
├── .pre-commit-config.yaml
├── CLAUDE.md
├── docker/
│   ├── docker-compose.yml
│   ├── litellm-config.yaml
│   ├── litellm.Dockerfile
│   └── .env
├── claude/
│   └── settings.json
├── README.md
```

---

## 🧹 Pre-commit Integration

This repository uses pre-commit hooks for file hygiene and Commitizen checks.

Install and activate hooks:

```bat
pip install pre-commit commitizen
pre-commit install
pre-commit install --hook-type pre-push
```

Run all hooks manually:

```bat
pre-commit run --all-files
```

Notes:

- `no-commit-to-branch` blocks direct commits to `main`.
- Commitizen checks run on commit and branch checks run on pre-push/post-commit.

## 🔁 GitHub CI

GitHub Actions validates pull requests and pushes to `main` with:

- `pre-commit run --all-files`
- `docker compose ... config` validation

Repository labels are also managed in CI:

- Source of truth: `.github/labels.json`
- Sync workflow: `.github/workflows/label-sync.yml`

---

## ✅ Requirements

- Docker
- Docker Compose
- (Optional) NVIDIA GPU

---

## 🚀 Future Improvements

- Helm chart (Kubernetes / OpenShift)
- Multi-user authentication
- Monitoring (Prometheus + Grafana)
- VS Code integration (Continue.dev)

---

## 📜 License

Use at your own risk. Models are subject to their respective licenses.
