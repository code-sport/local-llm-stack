# API Access, Keys, and User Tokens

This guide explains how users access the local LLM API in this repository and how the existing key/token settings behave.

## Quick Summary

- `http://localhost:3000` = **Open WebUI** browser app with user login support.
- `http://localhost:4000` = **LiteLLM** API endpoint for tools, scripts, and SDKs.
- The repository ships with placeholder client credentials such as `dummy` so local clients can connect quickly.
- The current Compose setup does **not** mint or manage separate per-user API tokens for LiteLLM.

If you need user-by-user API access control, keep reading the [Need real per-user tokens?](#need-real-per-user-tokens) section.

## Two Different Auth Layers

### 1. Browser users in Open WebUI

Open WebUI has its own sign-in layer controlled by:

- `WEBUI_AUTH=true`
- `ENABLE_SIGNUP=true` or `false`

This controls who can log in to the web app on port `3000`.

### 2. API clients talking to LiteLLM

Scripts, SDKs, editors, and other apps usually talk directly to LiteLLM on port `4000`.

In this repository, clients are configured with shared placeholder values such as:

- `OPENAI_API_KEY=dummy`
- `ANTHROPIC_API_KEY=dummy`

These values are suitable for local development and for clients that require a non-empty key field.

## Important Behavior of `OPENAI_API_KEY`

`OPENAI_API_KEY` in `docker/.env` is used by the bundled `open-webui` container when it calls LiteLLM.

It is best understood as a **shared client credential** in this repo.

It does **not by itself** create a multi-user API key system for LiteLLM.

So, today:

- Open WebUI users can sign in to the browser app if `WEBUI_AUTH=true`.
- External API clients can send a bearer token like `dummy` if their SDK expects one.
- LiteLLM is still effectively a trusted local endpoint unless you add another auth layer in front of it.

## Recommended Local Usage

For local-only usage on your own machine:

1. Keep LiteLLM on `localhost:4000`.
2. Use a simple shared token such as `dummy` or another local-only value.
3. Share that value only with trusted local clients.

## PowerShell Examples

### List available models

```powershell
$headers = @{ Authorization = 'Bearer dummy' }
Invoke-RestMethod -Uri 'http://localhost:4000/models' -Headers $headers -Method Get
```

### Send a chat completion request

```powershell
$headers = @{
    Authorization = 'Bearer dummy'
    'Content-Type' = 'application/json'
}

$body = @{
    messages = @(
        @{
            role = 'user'
            content = 'Hello from PowerShell'
        }
    )
    max_tokens = 64
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Uri 'http://localhost:4000/deepseek-v4/chat/completions' -Headers $headers -Method Post -Body $body
```

If you changed the shared token in `docker/.env`, replace `dummy` with your chosen value.

## Using SDKs and Developer Tools

### OpenAI-style clients

Use:

- Base URL: `http://localhost:4000`
- API key: `dummy` or your shared local token

### Claude-style clients

Use:

- Base URL: `http://localhost:4000`
- API key: `dummy` or your shared local token
- Model names from this stack such as `deepseek-v4`, `chat`, or `fast`

For Claude Code-style local configuration, see the root `README.md` and `claude/settings.json`.

## Changing the Shared Token

If you want something better than `dummy`, set a new shared token in your local `docker/.env` and in any clients that call LiteLLM.

Example:

```dotenv
OPENAI_API_KEY=my-local-shared-token
ANTHROPIC_API_KEY=my-local-shared-token
```

Then restart the stack:

```powershell
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build
```

## Open WebUI User Access Tips

If you want browser users to authenticate before using the UI:

- Keep `WEBUI_AUTH=true`
- Set `ENABLE_SIGNUP=false` after initial setup if you do not want open self-registration

Example:

```dotenv
WEBUI_AUTH=true
ENABLE_SIGNUP=false
```

This helps control UI access, but it still does not create separate API tokens for every LiteLLM user.

## Need Real Per-User Tokens?

This repository does not currently provide built-in per-user API token issuance for LiteLLM.

If you need true user-by-user API protection, the safest approach is to place LiteLLM behind an auth-aware gateway or reverse proxy and keep the direct API private.

Practical options:

- bind the API to localhost only
- expose it only through a VPN or trusted network
- add a reverse proxy with authentication in front of port `4000`
- use Open WebUI user accounts for browser access and keep direct API access limited to admins/tools

## Related Docs

- [Configuration](./configuration.md)
- [Architecture & Components](./architecture.md)
- [Troubleshooting](./troubleshooting.md)
