# Model Routing

Model routing is defined in `docker/litellm-config.yaml`.

Important notes:

- The config is baked into the custom LiteLLM image (`docker/litellm.Dockerfile`).
- After changing routing entries, rebuild `litellm`.

```bat
docker compose -f docker\docker-compose.yml --env-file docker\.env up -d --build litellm
```

Keep `MODELS` in `docker/.env` aligned with the Ollama models you expect `model-init` to pull.
