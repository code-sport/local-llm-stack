# Troubleshooting

Use these checks to validate the local stack quickly.

## Useful Checks

```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env config
docker compose -f docker\docker-compose.yml --env-file docker\.env logs -f
```

## Service Health Checks

```bat
curl http://localhost:11434/api/tags
curl http://localhost:4000/models
```

## API Key / Token Checks

If your SDK, editor, or script asks for an API key, use the same shared local value configured for your client, typically `dummy` unless you changed it.

PowerShell example:

```powershell
$headers = @{ Authorization = 'Bearer dummy' }
Invoke-RestMethod -Uri 'http://localhost:4000/models' -Headers $headers -Method Get
```

If you changed the token in `docker/.env`, update your client config to match.

For a fuller explanation of user login vs API tokens, see [API Access, Keys, and User Tokens](./api-access.md).

## Smoke Test

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-test.ps1
```
