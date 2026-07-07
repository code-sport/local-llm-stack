FROM ghcr.io/berriai/litellm:v1.74.0-stable

# Bake project-specific routing config into the image to avoid host bind mounts.
COPY litellm-config.yaml /app/proxy_server_config.yaml
