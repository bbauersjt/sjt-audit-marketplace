# install.ps1 — everything in this repo is now a plugin; this just prints the commands.
# (Loose-skill copying removed 2026-07-06 when audit-sampling and trial-balance-prep
# were wrapped as plugins. Run the /plugin commands inside Claude Code.)

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$plugins = @('fs-review', 'suralink-binder', 'cch-axcess-suite', 'audit-sampling', 'audit-workspace')

Write-Host "Install the plugins inside Claude Code:" -ForegroundColor Cyan
Write-Host "  /plugin marketplace add `"$here`""
foreach ($p in $plugins) { Write-Host "  /plugin install $p@sjt-skills" }
