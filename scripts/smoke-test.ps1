param(
    [string]$OllamaUrl = "http://localhost:11434/api/tags",
    [string]$LiteLlmUrl = "http://localhost:4000/models",
    [string]$WebUiUrl = "http://localhost:3000",
    [int]$MaxAttempts = 20,
    [int]$DelaySeconds = 3
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Test-Endpoint {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [string]$Url
    )

    for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
        try {
            $response = Invoke-WebRequest -Uri $Url -Method Get -TimeoutSec 10 -UseBasicParsing
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

Write-Host "Starte Smoke-Test..."
Test-Endpoint -Name "Ollama" -Url $OllamaUrl
Test-Endpoint -Name "LiteLLM" -Url $LiteLlmUrl
Test-Endpoint -Name "Open WebUI" -Url $WebUiUrl
Write-Host "Smoke-Test erfolgreich abgeschlossen."
