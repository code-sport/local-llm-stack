# Configuration

Configuration in this project is centered around:

- `env.example` — template values for local setup
- `docker/.env` — local overrides, gitignored
- `docker/docker-compose.yml` — service wiring and environment injection
- `claude/settings.json` — optional local Claude-compatible client defaults

## Main Configuration Files

| File | Purpose |
|---|---|
| `env.example` | Starting template for local environment variables |
| `docker/.env` | Real values used by Docker Compose on your machine |
| `docker/docker-compose.yml` | Service definitions, ports, env vars, health checks |
| `docker/litellm-config.yaml` | Model routing names exposed by LiteLLM |
| `claude/settings.json` | Example client config for Claude-style local access |

## User Access and Authentication Settings

The stack has two different access layers:

### Open WebUI login

- `WEBUI_AUTH` controls whether browser users sign in to Open WebUI.
- `ENABLE_SIGNUP` controls whether new browser users can self-register.

Typical locked-down UI setup:

```dotenv
WEBUI_AUTH=true
ENABLE_SIGNUP=false
```

### LiteLLM API access

- `OPENAI_API_KEY` is the shared credential used by the bundled `open-webui` container when it talks to LiteLLM.
- `ANTHROPIC_API_KEY` is provided as a matching client-side default for Claude-compatible tools.

In this repository, these values are intended for local client configuration and quick-start compatibility.

They do **not** by themselves create a per-user API token system on LiteLLM.

For concrete examples and guidance, see [API Access, Keys, and User Tokens](./api-access.md).

## Common Local Changes

### Change the exposed ports

Edit `docker/.env`:

```dotenv
OLLAMA_PORT=11434
LITELLM_PORT=4000
WEBUI_PORT=3000
```

### Change the shared local API token used by clients

Edit `docker/.env`:

```dotenv
OPENAI_API_KEY=my-local-shared-token
ANTHROPIC_API_KEY=my-local-shared-token
```

Then restart the stack so clients pick up the new values.

### Change which models are preloaded

Edit `MODELS` in `docker/.env`, then update `docker/litellm-config.yaml` if model routing names also change.

## See Also

- Root `README.md` → `Environment Variables (docker/.env)`
- [Model Routing](./models.md)
- [API Access, Keys, and User Tokens](./api-access.md)
