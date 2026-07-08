param(
    [string]$OllamaUrl = "http://localhost:11434/api/tags",
    [string]$LiteLlmUrl = "http://localhost:4000/models",
    [string]$WebUiUrl = "http://localhost:3000",
    [int]$MaxAttempts = 20,
    [int]$DelaySeconds = 3,
    [string]$SecretsDir,
    [switch]$SkipSecretsPrecheck
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-Endpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Url,
        [hashtable]$Headers = @{}
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -Headers $Headers -TimeoutSec 10 -UseBasicParsing
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 400) {
                Write-Host "[OK] $Name erreichbar ($($response.StatusCode))"
                return
            }
        }
        catch {
            if ($attempt -eq $MaxAttempts) {
                throw "[FAIL] $Name nicht erreichbar: $Url"
            }
        }

        Start-Sleep -Seconds $DelaySeconds
    }
}

function Get-SecretsDir {
    $repoRoot = Split-Path -Parent $PSScriptRoot

    if (-not [string]::IsNullOrWhiteSpace($SecretsDir)) {
        return $SecretsDir
    }

    if (-not [string]::IsNullOrWhiteSpace($env:SECRETS_DIR)) {
        return $env:SECRETS_DIR
    }

    $envFile = Join-Path $repoRoot "docker/.env"
    if (Test-Path -Path $envFile -PathType Leaf) {
        $line = Get-Content -Path $envFile | Where-Object { $_ -match '^\s*SECRETS_DIR\s*=' } | Select-Object -First 1
        if ($line) {
            $value = (($line -split '=', 2)[1]).Trim().Trim('"').Trim("'")
            if (-not [string]::IsNullOrWhiteSpace($value)) {
                return $value
            }
        }
    }

    return (Join-Path $repoRoot "docker/.secrets")
}

function Get-LiteLlmHeaders {
    $secretsDir = Get-SecretsDir
    $masterKeyFile = Join-Path $secretsDir "litellm_master_key"
    if (-not (Test-Path -Path $masterKeyFile -PathType Leaf)) {
        return @{}
    }

    $masterKey = (Get-Content -Path $masterKeyFile -Raw).Trim()
    if ([string]::IsNullOrWhiteSpace($masterKey)) {
        return @{}
    }

    return @{ Authorization = "Bearer $masterKey" }
}

function Test-SecretsPrecheck {
    $secretsDir = Get-SecretsDir

    $requiredFiles = @(
        (Join-Path $secretsDir "litellm_master_key"),
        (Join-Path $secretsDir "webui_secret_key")
    )

    $missingFiles = @($requiredFiles | Where-Object { -not (Test-Path -Path $_ -PathType Leaf) })
    if ($missingFiles.Count -gt 0) {
        $missingList = ($missingFiles | ForEach-Object { "`n  - $_" }) -join ""
        throw "[FAIL] Secret-Dateien fehlen:$missingList`nLege die Dateien an oder setze SECRETS_DIR auf ein gueltiges Verzeichnis."
    }

    Write-Host "[OK] Secrets vorhanden in: $secretsDir"
}

Write-Host "Starte Smoke-Test..."
if (-not $SkipSecretsPrecheck) {
    Test-SecretsPrecheck
}
Test-Endpoint -Name "Ollama" -Url $OllamaUrl
Test-Endpoint -Name "LiteLLM" -Url $LiteLlmUrl -Headers (Get-LiteLlmHeaders)
Test-Endpoint -Name "Open WebUI" -Url $WebUiUrl
Write-Host "Smoke-Test erfolgreich abgeschlossen."
