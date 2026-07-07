# Architecture & Components

This document explains the three core components of Claude Local Stack and how they work together.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Open WebUI (Port 3000)                     │
│              ChatGPT/Claude-like Web Interface               │
│              Talks to: LiteLLM (Claude API proxy)            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ (OpenAI/Claude API calls)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  LiteLLM (Port 4000)                         │
│         Claude-compatible API proxy + model routing          │
│         Converts: OpenAI API format → Ollama API format      │
│         Talks to: Ollama (local model runtime)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ (Ollama API)
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  Ollama (Port 11434)                         │
│            Local LLM Runtime (models in memory)              │
│              Runs: LLaMA, DeepSeek, Phi, etc.               │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔍 Component Details

### 1️⃣ **Ollama** — Local Model Runtime

**What it does:**
- Hosts and runs large language models locally on your machine
- Manages GPU/CPU inference
- Handles model memory and context windows
- Provides REST API for model inference

**Key Features:**
- 🚀 Fast inference (optimized for different hardware)
- 📦 Automatic model management (download, cache, unload)
- 🎯 Simple REST API (`/api/generate`, `/api/chat`)
- 🖥️ CPU or GPU support (NVIDIA CUDA or Apple Metal)

**Official Resources:**
- 📖 [Ollama Documentation](https://github.com/ollama/ollama#readme)
- 🐳 [Ollama Docker Hub](https://hub.docker.com/r/ollama/ollama)
- 🤖 [Available Models](https://ollama.ai/library)

**In this stack:**
- Runs in Docker container on port `11434`
- Loads models: `llama3`, `deepseek-coder`, `phi3`, `deepseek-v4-flash`
- Connected to LiteLLM via internal Docker network

---

### 2️⃣ **LiteLLM** — Claude-Compatible API Proxy

**What it does:**
- Acts as a "translation layer" between different LLM APIs
- Converts OpenAI/Claude-style API calls → Ollama API format
- Routes requests to the right model based on the request
- Provides cost tracking and logging

**Key Features:**
- 🔌 Supports 100+ LLM providers (OpenAI, Anthropic, Hugging Face, etc.)
- 🎯 Model routing (map friendly names to actual models)
- 📊 Usage tracking and analytics
- ⚡ Load balancing and fallbacks
- 🔑 Consistent API regardless of backend

**Official Resources:**
- 📖 [LiteLLM Documentation](https://docs.litellm.ai/)
- 🐙 [LiteLLM GitHub](https://github.com/BerriAI/litellm)
- 📦 [LiteLLM Docker Hub](https://hub.docker.com/r/litellm/litellm)

**In this stack:**
- Runs in Docker container on port `4000`
- Configured via `docker/litellm-config.yaml`
- Routes requests:
  - `chat` → Ollama's `llama3` (general chat)
  - `coder` → Ollama's `deepseek-coder` (coding tasks)
  - `fast` → Ollama's `phi3` (fast/lightweight)
  - `deepseek-v4` → Ollama's `deepseek-v4-flash` (reasoning)

---

### 3️⃣ **Open WebUI** — Web Chat Interface

**What it does:**
- Provides a ChatGPT/Claude-like chat interface
- Manages conversation history and user sessions
- Sends requests to LiteLLM (via OpenAI API format)
- Renders model responses in the browser

**Key Features:**
- 💬 Familiar chat interface (ChatGPT-style)
- 📝 Conversation history and export
- 🎨 Dark/light theme
- 👥 Multi-user support (optional)
- 🔐 RAG integration (document search)
- 🧪 Model switching without reloading

**Official Resources:**
- 📖 [Open WebUI Documentation](https://docs.openwebui.com/)
- 🐙 [Open WebUI GitHub](https://github.com/open-webui/open-webui)
- 🐳 [Open WebUI Docker Hub](https://hub.docker.com/r/ghcr.io/open-webui/open-webui)

**In this stack:**
- Runs in Docker container on port `3000`
- Configured to use LiteLLM as backend (`http://litellm:4000`)
- All data stored in Docker volume (survives restarts)

---

## 🔗 How They Work Together

### **Request Flow:**

```
1. User types message in Open WebUI (browser)
   ↓
2. Open WebUI sends OpenAI-compatible API call to LiteLLM
   POST http://litellm:4000/v1/chat/completions
   ↓
3. LiteLLM receives request, looks up model mapping in config
   (e.g., "chat" → "ollama/llama3")
   ↓
4. LiteLLM converts format and calls Ollama API
   POST http://ollama:11434/api/chat
   ↓
5. Ollama loads model into memory (if not already loaded)
   and generates response via GPU/CPU inference
   ↓
6. Response flows back: Ollama → LiteLLM → Open WebUI → Browser
```

### **Key Design Principles:**

| Principle | Benefit |
|-----------|---------|
| **Separation of Concerns** | Each component has one job; easy to replace/upgrade |
| **API Standardization** | LiteLLM translates to OpenAI API (industry standard) |
| **Model Routing** | Clients don't care which backend; just request by role |
| **Local-First** | No cloud dependency; everything runs on your hardware |
| **Docker Networking** | Services communicate securely via internal Docker network |

---

## 🎯 Use Cases

### Open WebUI
- **Use for:** Chatting with models, testing prompts, exploring conversations
- **Good for:** General knowledge, coding help, creative writing

### LiteLLM
- **Use for:** Building applications that need LLM access
- **Can use:** Curl, Python, JavaScript SDKs (all support OpenAI API format)

### Ollama
- **Use for:** Fine-tuning, custom models, model management
- **Advanced users:** Direct API calls for specific use cases

---

## 🚀 Quick Reference

**Stop/restart a single component:**
```bash
docker compose -f docker\docker-compose.yml --env-file docker\.env restart litellm
```

**View component logs:**
```bash
# All components
docker compose -f docker\docker-compose.yml --env-file docker\.env logs -f

# Specific component
docker compose -f docker\docker-compose.yml --env-file docker\.env logs -f ollama
```

**Check component health:**
```bash
# Ollama is running and has models?
curl http://localhost:11434/api/tags

# LiteLLM is running?
curl http://localhost:4000/models

# Open WebUI is running?
curl http://localhost:3000
```

---

## 📚 Further Reading

- [Model Routing](./models.md) — How to add/change models
- [Configuration](./configuration.md) — Environment variables and tuning
- [Troubleshooting](./troubleshooting.md) — Common issues and fixes
