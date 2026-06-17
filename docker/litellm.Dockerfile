FROM ghcr.io/berriai/litellm:main

# Bake project-specific routing config into the image to avoid host bind mounts.
COPY litellm-config.yaml /app/proxy_server_config.yaml
