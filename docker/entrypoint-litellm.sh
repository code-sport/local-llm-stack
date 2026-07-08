#!/bin/sh
# Load LITELLM_MASTER_KEY from Docker secret file if present.
# Falls back to the env var already set (e.g. in dev without Docker secrets).
SECRET_FILE=/run/secrets/litellm_master_key
if [ -f "$SECRET_FILE" ]; then
  export LITELLM_MASTER_KEY
  LITELLM_MASTER_KEY=$(cat "$SECRET_FILE")
fi
exec "$@"
