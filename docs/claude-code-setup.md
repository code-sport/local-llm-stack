# Claude Code Setup & Usage Guide

This guide provides step-by-step instructions for using JetBrains Claude Code with the local Claude Local Stack.

## Table of Contents

1. [What is Claude Code?](#what-is-claude-code)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Configuration Options](#configuration-options)
5. [Quick Start](#quick-start)
6. [Model Tiers Explained](#model-tiers-explained)
7. [Advanced Configuration](#advanced-configuration)
8. [Keyboard Shortcuts](#keyboard-shortcuts)
9. [Common Workflows](#common-workflows)
10. [Troubleshooting](#troubleshooting)
11. [Performance Optimization](#performance-optimization)

## What is Claude Code?

Claude Code is an AI-powered coding assistant available as a plugin for JetBrains IDEs (IntelliJ, PyCharm, WebStorm, CLion, Rider, etc.). By default, it connects to Anthropic's cloud API. However, you can configure it to use the local Claude Local Stack for:

- **Privacy:** Code stays on your machine
- **Offline work:** No internet connection required
- **No API costs:** Use local models
- **Full control:** Customize models and behavior

## Prerequisites

Before starting, ensure you have:

1. **JetBrains IDE installed** (IntelliJ IDEA, PyCharm, WebStorm, etc.)
2. **Claude Code plugin** installed via Settings → Plugins → Marketplace → Search "Claude Code" → Install
3. **Docker Desktop running** on your machine
4. **Claude Local Stack cloned** from GitHub
5. **The stack running locally:**
   ```powershell
   cd D:\github\code-sport\claude-local-stack
   docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
   ```

## Installation & Setup

### Step 1: Install Claude Code Plugin

1. Open your JetBrains IDE
2. Go to **Settings → Plugins → Marketplace**
3. Search for **"Claude Code"**
4. Click **Install** and restart the IDE

### Step 2: Configure the Local Endpoint

Choose one of two approaches:

#### **Option A: Project-Level (Recommended)**

This repository already includes `claude/settings.json` configured for local use.

1. Clone or open the `claude-local-stack` repository in your IDE
2. The project automatically uses the local stack configuration
3. Verify: Open Claude Code (Cmd+Shift+A → "Claude Code") and test

#### **Option B: Global Configuration**

To use the local stack for ALL projects:

1. Create or edit `~/.claude/settings.json`:

   **Windows:**
   ```powershell
   $settingsPath = "$env:USERPROFILE\.claude\settings.json"
   if (-not (Test-Path (Split-Path $settingsPath))) {
       New-Item -ItemType Directory -Path (Split-Path $settingsPath) -Force | Out-Null
   }
   ```

   **macOS/Linux:**
   ```bash
   mkdir -p ~/.claude
   ```

2. Add this content to `settings.json`:

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

3. **Restart the IDE completely** (exit and reopen)

### Step 3: Verify the Connection

1. Open Claude Code in the IDE (Command Palette → "Claude Code")
2. Ask a simple question: `What is 2 + 2?`
3. If it responds, you're connected!
4. If it fails, see [Troubleshooting](#troubleshooting) below

## Configuration Options

### Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `ANTHROPIC_BASE_URL` | Local API endpoint | `http://localhost:4000` |
| `ANTHROPIC_API_KEY` | API key (any value works locally) | `no-key` or `dummy` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | High-capability model | `deepseek-v4` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | General-purpose model | `chat` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Fast model | `fast` |

### Understanding Model Selection

Claude Code has three "tiers" of models internally:

- **Opus** (complex reasoning) → Used for deep analysis
- **Sonnet** (general purpose) → Used for standard requests
- **Haiku** (fast) → Used for simple/quick requests

Each maps to a local model:

| Tier | Local Model | Backend | Strengths |
|------|-------------|---------|-----------|
| Opus | `deepseek-v4` | deepseek-v4-flash | Best reasoning, largest context |
| Sonnet | `chat` | llama3 | Balanced speed/quality |
| Haiku | `fast` | phi3 | Very fast, lightweight |

## Quick Start

### Minimal Setup (5 minutes)

1. **Start the stack:**
   ```powershell
   cd D:\github\code-sport\claude-local-stack
   docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
   ```

2. **Create/edit `claude/settings.json` in your project:**
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

3. **Open your project in the IDE and restart it**

4. **Test:** Ask Claude Code a question

## Model Tiers Explained

### When to Use Which Model

**Use `deepseek-v4` (Opus) for:**
- Complex algorithmic problems
- Architecture design decisions
- Debugging multi-file issues
- Refactoring large codebases
- Detailed code reviews

**Use `chat` (Sonnet) for:**
- General coding help
- Function implementations
- Bug fixes
- Code explanations
- Most day-to-day work

**Use `fast` (Haiku) for:**
- Quick completions
- Simple questions
- Type hints and documentation
- Syntax checks
- When speed is critical

### How Claude Code Selects Models

Claude Code automatically selects the appropriate model based on request complexity:

- Complex queries or "deep analysis" → Opus
- Standard requests → Sonnet
- Quick operations or "fast mode" → Haiku

You cannot manually override the model tier in Claude Code's UI, but you control the backend model for each tier via `settings.json`.

## Advanced Configuration

### Custom Model Mappings

To use different models, edit your local `docker/litellm-config.yaml` and rebuild:

```yaml
# Example: Use a larger model for Opus
- model_name: deepseek-v4
  litellm_params:
    model: ollama/neural-chat
    api_base: http://ollama:11434
```

Then rebuild LiteLLM:
```powershell
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build litellm
```

### Using Different API Keys

If you've set a custom shared token in `docker/.env`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4000",
    "ANTHROPIC_API_KEY": "my-custom-token",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "deepseek-v4",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "chat",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "fast"
  }
}
```

### Environment-Specific Configuration

Create separate configs for different environments:

**`.env.local` (for local development):**
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

**`.env.cloud` (for Anthropic cloud API):**
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "<your-actual-api-key>",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "claude-3-5-opus-20241022",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "claude-3-5-sonnet-20241022",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "claude-3-5-haiku-20241022"
  }
}
```

## Keyboard Shortcuts

Common Claude Code shortcuts (may vary by IDE and OS):

| Action | Shortcut (Windows/Linux) | Shortcut (macOS) |
|--------|--------------------------|------------------|
| Open Claude Code | Ctrl+Shift+A | Cmd+Shift+A |
| Submit message | Ctrl+Enter | Cmd+Enter |
| Clear conversation | N/A | N/A |
| Insert at cursor | Tab | Tab |

## Common Workflows

### Workflow 1: Get Code Suggestions

1. Open Claude Code (Cmd+Shift+A)
2. Describe what you want: `Create a function that validates email addresses`
3. Review the suggestion and insert it into your file

### Workflow 2: Explain Code

1. Select code in your editor
2. Open Claude Code
3. Ask: `Explain what this code does`

### Workflow 3: Debug an Issue

1. Open Claude Code
2. Paste your error message
3. Ask: `Why am I getting this error?`
4. Claude Code can sometimes suggest fixes directly

### Workflow 4: Generate Tests

1. Select a function/method
2. Open Claude Code
3. Ask: `Generate unit tests for this function`

## Troubleshooting

### Problem: "Connection Refused"

**Cause:** The local stack is not running.

**Solution:**
```powershell
# Check if services are running
docker compose -f docker\docker-compose.yml --env-file docker\.env ps

# Start the stack if not running
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

### Problem: "Authorization Failed" or "Invalid API Key"

**Cause:** Misconfigured settings.

**Solution:**
1. Verify `ANTHROPIC_BASE_URL` is `http://localhost:4000` (not `https` or different port)
2. Verify `ANTHROPIC_API_KEY` is set to any non-empty string (e.g., `no-key` or `dummy`)
3. Restart the IDE completely

### Problem: "Unknown Model" or "Model Not Found"

**Cause:** Model doesn't exist or isn't loaded.

**Solution:**
```powershell
# Check available models
curl http://localhost:11434/api/tags

# Check model in LiteLLM config
curl http://localhost:4000/models

# Verify model name matches docker/litellm-config.yaml
```

### Problem: Claude Code Not Responding / Timeout

**Cause:** Model is slow or resource-constrained.

**Solution:**
```powershell
# Check resource usage
docker stats

# Check model logs
docker compose -f docker\docker-compose.yml --env-file docker\.env logs ollama

# Reduce loaded models to free memory
# Edit docker/.env and decrease OLLAMA_MAX_LOADED_MODELS
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

### Problem: IDE Shows Old Configuration

**Cause:** IDE is caching old settings.

**Solution:**
1. Completely close the IDE
2. Restart it (don't just minimize/reopen)
3. Clear IDE cache if still broken:
   - **IntelliJ:** Invalidate Caches → Restart
   - **PyCharm:** File → Invalidate Caches → Restart

### Problem: Settings File Not Found

**Cause:** Wrong path or file permissions.

**Solution:**
```powershell
# Create the directory if missing
$settingsDir = "$env:USERPROFILE\.claude"
if (-not (Test-Path $settingsDir)) {
    New-Item -ItemType Directory -Path $settingsDir -Force
}

# Verify the file exists and is readable
Get-Item "$settingsDir\settings.json"

# Check file permissions
icacls "$settingsDir\settings.json"
```

## Performance Optimization

### For Faster Responses

1. **Use `fast` model (Haiku) for simple tasks:**
   ```json
   {
     "env": {
       "ANTHROPIC_DEFAULT_HAIKU_MODEL": "fast"
     }
   }
   ```

2. **Reduce context size** — Ask shorter, more specific questions

3. **Use GPU acceleration** — See GPU setup in main README

4. **Monitor resource usage:**
   ```powershell
   docker stats
   ```

### For Better Quality Responses

1. **Use `deepseek-v4` (Opus) for complex tasks**
2. **Provide more context** — Paste relevant code snippets
3. **Ask specific questions** — Instead of "explain this", ask "why does this crash?"
4. **Break complex requests into smaller questions** — Iteratively refine

### For Long-Term Reliability

1. **Keep models updated:**
   ```powershell
   docker pull ollama
   docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build ollama
   ```

2. **Monitor disk space** — LLMs can consume significant storage
   ```powershell
   docker system df
   ```

3. **Clean up occasionally:**
   ```powershell
   # Remove unused images
   docker image prune -a

   # Remove unused containers
   docker container prune
   ```

## Related Documentation

- [Main README](../README.md) — Project overview
- [CLAUDE.md](../CLAUDE.md) — Quick reference for Claude Code
- [Configuration](./configuration.md) — Environment variables
- [Models](./models.md) — Model routing details
- [API Access](./api-access.md) — Authentication and API keys
- [Troubleshooting](./troubleshooting.md) — General troubleshooting
