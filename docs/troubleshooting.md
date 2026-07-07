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

## Smoke Test

```powershell
powershell -ExecutionPolicy Bypass -File scripts\smoke-test.ps1
```
