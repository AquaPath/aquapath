#!/usr/bin/env pwsh
Write-Host "================================================"
Write-Host "  AquaPath - Sistema de Optimización Hídrica  "
Write-Host "================================================"
Write-Host ""
Write-Host "Iniciando aplicación web..."
Write-Host ""
Write-Host "La aplicación se abrirá en: http://localhost:8501"
Write-Host "Presiona Ctrl+C para detener la aplicación"
Write-Host ""
Write-Host "================================================"

$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $scriptDir

if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activando entorno virtual .venv..."
    . .\.venv\Scripts\Activate.ps1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python no está disponible en PATH. Instale Python 3.8+ y vuelva a intentarlo."
    exit 1
}

Write-Host "Comprobando si 'streamlit' está instalado..."
$check = & python -c 'import importlib,sys; sys.exit(0 if importlib.util.find_spec("streamlit") else 1)'

if ($LASTEXITCODE -ne 0) {
    Write-Host "Streamlit no está instalado. Instalando dependencias desde requirements.txt..."
    & python -m pip install --upgrade pip
    & python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "La instalación de dependencias falló. Instale manualmente con: python -m pip install -r requirements.txt"
        exit 1
    }
}

Write-Host "Ejecutando Streamlit..."
& python -m streamlit run app.py
