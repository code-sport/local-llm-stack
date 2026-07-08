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

---

## 🔐 Secrets Setup (Required for Production)

Two secrets **must** be set before running the stack in any shared or production environment.

### 1. Generate the secrets

Run once in your terminal:

```powershell
# LiteLLM master key — used by all API clients as Bearer token
python -c "import secrets; print('sk-' + secrets.token_hex(32))"

# Open WebUI session signing secret
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2. Set them in `docker/.env`

```dotenv
LITELLM_MASTER_KEY=sk-<your-generated-value>
WEBUI_SECRET_KEY=<your-generated-value>
```

### 3. Align `OPENAI_API_KEY` with `LITELLM_MASTER_KEY`

Open WebUI authenticates to LiteLLM using `OPENAI_API_KEY`.
Both values **must match**:

```dotenv
OPENAI_API_KEY=sk-<same-value-as-LITELLM_MASTER_KEY>
```

If they differ, Open WebUI will receive `401 Unauthorized` from LiteLLM.

### 4. Restart the stack

```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build litellm open-webui
```

> ⚠️ `LITELLM_MASTER_KEY` and `WEBUI_SECRET_KEY` are **baked into the running containers** at start time.
> A container restart (not rebuild) is sufficient after changing them.

### Why these secrets matter

| Secret | Risk without it |
|---|---|
| `LITELLM_MASTER_KEY` | Any local process can call all models without auth |
| `WEBUI_SECRET_KEY` | Sessions are invalidated on every container restart; randomised on each boot makes forging sessions easier |

---

## 🚦 Rate Limiting

LiteLLM enforces global rate limits to prevent runaway scripts from saturating your GPU/CPU.

Configure in `docker/.env`:

```dotenv
LITELLM_RPM_LIMIT=60          # max requests per minute (global)
LITELLM_TPM_LIMIT=100000      # max tokens per minute (global)
LITELLM_MAX_PARALLEL_REQUESTS=10  # max concurrent in-flight requests
```

Clients that exceed the limit receive `429 Too Many Requests`.

For teams or heavy automation, lower these values or consider per-key limits via the
[LiteLLM virtual keys feature](https://docs.litellm.ai/docs/proxy/virtual_keys).

---

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

Enable signup temporarily to create the first admin account, then disable it again.

### LiteLLM API access

- `OPENAI_API_KEY` is the shared credential used by the bundled `open-webui` container when it talks to LiteLLM.
- `ANTHROPIC_API_KEY` is provided as a matching client-side default for Claude-compatible tools.

Once `LITELLM_MASTER_KEY` is set, **all clients** (including SDK users and curl) must send it as a Bearer token:

```powershell
$headers = @{ Authorization = "Bearer $env:LITELLM_MASTER_KEY" }
Invoke-RestMethod -Uri 'http://localhost:4000/models' -Headers $headers
```

For more detail, see [API Access, Keys, and User Tokens](./api-access.md).

---

## Common Local Changes

### Change the exposed ports

Edit `docker/.env`:

```dotenv
OLLAMA_PORT=11434
LITELLM_PORT=4000
WEBUI_PORT=3000
```

### Change resource limits

```dotenv
OLLAMA_MEMORY_LIMIT=12g
OLLAMA_CPU_LIMIT=4.0
LITELLM_MEMORY_LIMIT=1g
LITELLM_CPU_LIMIT=2.0
WEBUI_MEMORY_LIMIT=512m
WEBUI_CPU_LIMIT=1.0
```

### Change which models are preloaded

Edit `MODELS` in `docker/.env`, then update `docker/litellm-config.yaml` if model routing names also change.

## See Also

- Root `README.md` → `Environment Variables (docker/.env)`
- [Model Routing](./models.md)
- [API Access, Keys, and User Tokens](./api-access.md)


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
