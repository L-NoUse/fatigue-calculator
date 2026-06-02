$ErrorActionPreference = "Stop"

$python = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
$env:MPLCONFIGDIR = Join-Path $PSScriptRoot ".matplotlib-cache"

if (-not (Test-Path $python)) {
    py -m venv (Join-Path $PSScriptRoot ".venv")
}

& $python -m pip install -r (Join-Path $PSScriptRoot "requirements.txt")
& $python -m pip install pyinstaller
& $python -m PyInstaller --noconfirm --onefile --windowed --name "FatigueCalculator" (Join-Path $PSScriptRoot "gui_app.py")

Write-Host ""
Write-Host "打包完成:"
Write-Host (Join-Path $PSScriptRoot "dist\FatigueCalculator.exe")
