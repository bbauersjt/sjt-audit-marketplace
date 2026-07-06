# install.ps1 — install the SJT loose skills locally, and print the plugin commands.
# Loose skills are copied into %USERPROFILE%\.claude\skills\ (personal skills).
# The plugins are installed via /plugin commands inside Claude Code (printed at the end).

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $env:USERPROFILE '.claude\skills'

# Marketplace plugin names (for the printed /plugin install commands).
$plugins = @('fs-review', 'suralink-binder', 'cch-axcess-suite', 'chrome-bridge')
# Folders to skip when discovering loose skills (plugin dirs + the marketplace dir).
$skip    = @('fs-review', 'suralink-binder', 'cch-axcess-suite', 'chrome-bridge-plugin', '.claude-plugin')

New-Item -ItemType Directory -Force -Path $target | Out-Null

# Loose skills = top-level folders that are NOT plugin folders, NOT the marketplace dir,
# and that actually contain a SKILL.md.
$loose = Get-ChildItem -Path $here -Directory |
    Where-Object { $skip -notcontains $_.Name } |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }

Write-Host "Installing $($loose.Count) loose skills to $target" -ForegroundColor Cyan
foreach ($s in $loose) {
    $dest = Join-Path $target $s.Name
    if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
    Copy-Item -Recurse -Force $s.FullName $dest
    Write-Host "  + $($s.Name)"
}

Write-Host ""
Write-Host "Loose skills done. Now install the plugins inside Claude Code:" -ForegroundColor Cyan
Write-Host "  /plugin marketplace add `"$here`""
foreach ($p in $plugins) { Write-Host "  /plugin install $p@sjt-skills" }
Write-Host ""
Write-Host "Note: chrome-bridge also needs 'pip install -r requirements.txt' and the unpacked" -ForegroundColor DarkGray
Write-Host "      Chrome extension loaded — see chrome-bridge-plugin\README.md." -ForegroundColor DarkGray
