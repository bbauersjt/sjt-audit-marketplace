# install.ps1 — print the /plugin install commands, and copy any loose skills (currently none).
# Every skill now ships inside a plugin, installed via /plugin inside Claude Code.
# The loose-skill copy is kept as a no-op safety net in case a loose skill is added later.

$ErrorActionPreference = 'Stop'
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = Join-Path $env:USERPROFILE '.claude\skills'

# Marketplace plugin names (for the printed /plugin install commands).
$plugins = @('fs-review', 'suralink-binder', 'cch-axcess-suite', 'audit-sampling', 'trial-balance-prep')
# Folders to skip when discovering loose skills (plugin dirs + the marketplace dir).
$skip    = $plugins + @('.claude-plugin')

New-Item -ItemType Directory -Force -Path $target | Out-Null

# Loose skills = top-level folders that are NOT plugin folders, NOT the marketplace dir,
# and that actually contain a SKILL.md. (Currently none.)
$loose = Get-ChildItem -Path $here -Directory |
    Where-Object { $skip -notcontains $_.Name } |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }

if ($loose.Count -gt 0) {
    Write-Host "Installing $($loose.Count) loose skills to $target" -ForegroundColor Cyan
    foreach ($s in $loose) {
        $dest = Join-Path $target $s.Name
        if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
        Copy-Item -Recurse -Force $s.FullName $dest
        Write-Host "  + $($s.Name)"
    }
    Write-Host ""
}

Write-Host "Install the plugins inside Claude Code:" -ForegroundColor Cyan
Write-Host "  /plugin marketplace add `"$here`""
foreach ($p in $plugins) { Write-Host "  /plugin install $p@sjt-skills" }
Write-Host ""
Write-Host "Note: the suralink-binder and cch-axcess-suite plugins need the Chrome bridge," -ForegroundColor DarkGray
Write-Host "      which lives in its own repo: github.com/bbauersjt/sjt-chrome-bridge" -ForegroundColor DarkGray
