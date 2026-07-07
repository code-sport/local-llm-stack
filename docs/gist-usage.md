# GitHub Gist Usage (Optional)

This project does not require GitHub, but GitHub Gist is useful for sharing setup snippets with teammates.

## What to Share

- Share sanitized snippets only.
- Prefer sharing `env.example` instead of a real `docker/.env` file.
- Remove tokens, credentials, and any other secrets before uploading.
- Prefer secret/private gists for team-internal collaboration.

## Recommended Team Flow

1. Create a gist with safe snippets (for example, selected values from `env.example`).
2. Share the gist URL with your teammate.
3. Your teammate copies values into local files:
   - `docker/.env`
   - `claude/settings.json`
4. Validate the local setup with Docker Compose.

## Quick Local Copy Step (PowerShell)

```powershell
Copy-Item env.example docker\.env
# Paste values from your gist into docker\.env and claude\settings.json
```

## Troubleshooting Sharing Issues

- Share only the minimal logs needed for reproduction.
- Avoid posting full environment files.
- Rotate any credential immediately if it is accidentally exposed.
