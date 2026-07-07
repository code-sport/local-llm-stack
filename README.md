# Claude Local Stack

A fully local, Docker-based AI stack that mimics Anthropic Claude using open-source models.

This repository contains only the local AI stack and related configuration/docs — no separate application backend is included.

## ✨ Features

- ✅ Local LLM hosting (Ollama)
- ✅ Claude-compatible API (LiteLLM proxy)
- ✅ Web UI (Open WebUI - similar to ChatGPT/Claude)
- ✅ GPU acceleration (auto-detect)
- ✅ Model routing (chat / coding / fast)
- ✅ Idempotent model initialization
- ✅ Docker Compose ready

---

## 🚀 Quick Start

```bat
copy env.example docker\.env
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

Open the UI:

👉 http://localhost:3000

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
| `OLLAMA_IMAGE` | Ollama image with tag | `ollama/ollama:latest` |
| `OLLAMA_NUM_PARALLEL` | Ollama parallel request handling | `2` |
| `OLLAMA_MAX_LOADED_MODELS` | Max loaded models in memory | `2` |
| `OLLAMA_HEALTHCHECK_INTERVAL` | Healthcheck interval | `5s` |
| `OLLAMA_HEALTHCHECK_RETRIES` | Healthcheck retries | `10` |
| `MODEL_INIT_RESTART` | Restart behavior for `model-init` | `no` |
| `LITELLM_IMAGE` | LiteLLM image with tag | `claude-local-stack-litellm:local` |
| `LITELLM_HOST` | LiteLLM bind host | `0.0.0.0` |
| `LITELLM_LOG` | LiteLLM log level | `info` |
| `WEBUI_IMAGE` | Open WebUI image with tag | `ghcr.io/open-webui/open-webui:main` |
| `WEBUI_CONTAINER_PORT` | Internal container port for Open WebUI | `8080` |
| `NVIDIA_VISIBLE_DEVICES` | GPU visibility inside containers | `all` |

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

---

## 🖥 GPU Support

Requires:

- NVIDIA GPU
- nvidia-container-toolkit

Test:

```bash
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

---

## 📁 Project Structure

```
claude-local-stack/
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
