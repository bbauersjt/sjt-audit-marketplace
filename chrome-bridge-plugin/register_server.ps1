# Registers the chrome-bridge MCP server in the Claude desktop app config.
# Portable: auto-detects Python, the server path, and the config location
# (packaged/Store build vs regular installer). Run from PowerShell:
#   powershell -ExecutionPolicy Bypass -File "<path>\chrome-bridge\register_server.ps1"

$ErrorActionPreference = "Stop"

# --- server.py lives next to this script ---
$serverPath = Join-Path $PSScriptRoot "server.py"
if (-not (Test-Path $serverPath)) {
    Write-Host "Can't find server.py next to this script ($serverPath)." -ForegroundColor Red
    exit 1
}

# --- resolve a REAL python.exe (not the Microsoft Store alias stub) ---
$py = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $py -or $py -like "*WindowsApps*") {
    Write-Host "Could not resolve a real python.exe. Install Python (winget install Python.Python.3.12), reopen the terminal, and check 'where python'." -ForegroundColor Red
    exit 1
}

# --- locate the Claude config: packaged/Store build first, else regular ---
$cfg = $null
$pkg = Get-ChildItem "$env:LOCALAPPDATA\Packages" -Directory -Filter "Claude_*" -ErrorAction SilentlyContinue |
       Select-Object -First 1
if ($pkg) {
    $cfg = Join-Path $pkg.FullName "LocalCache\Roaming\Claude\claude_desktop_config.json"
} else {
    $cfg = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
}

# --- load existing config (or start fresh) and add chrome-bridge ---
if (Test-Path $cfg) {
    $j = Get-Content $cfg -Raw | ConvertFrom-Json
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path $cfg) | Out-Null
    $j = [pscustomobject]@{}
}
if (-not $j.PSObject.Properties['mcpServers']) {
    $j | Add-Member mcpServers ([pscustomobject]@{})
}
$j.mcpServers | Add-Member "chrome-bridge" ([pscustomobject]@{
    command = $py
    args    = @($serverPath)
}) -Force

# --- write UTF-8 WITHOUT a BOM (a BOM makes the app reject the JSON) ---
$json = $j | ConvertTo-Json -Depth 20
[System.IO.File]::WriteAllText($cfg, $json, (New-Object System.Text.UTF8Encoding($false)))

Write-Host "`nRegistered chrome-bridge." -ForegroundColor Green
Write-Host "Config :" $cfg
Write-Host "Python :" $py
Write-Host "Server :" $serverPath
Write-Host "`nFully quit and reopen the Claude app to load it.`n"
Write-Host "--- current config ---`n"
Get-Content $cfg -Raw
