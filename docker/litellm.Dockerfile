FROM ghcr.io/berriai/litellm:v1.83.14-stable

# Bake project-specific routing config into the image to avoid host bind mounts.
COPY litellm-config.yaml /app/proxy_server_config.yaml

# Secret-aware entrypoint: reads LITELLM_MASTER_KEY from /run/secrets/ if present.
COPY entrypoint-litellm.sh /entrypoint-litellm.sh
RUN chmod +x /entrypoint-litellm.sh

ENTRYPOINT ["/entrypoint-litellm.sh"]
CMD ["litellm", "--config", "/app/proxy_server_config.yaml", "--port", "4000"]
