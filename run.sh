#!/bin/bash

echo "================================================"
echo "  AquaPath - Sistema de Optimización Hídrica  "
echo "================================================"
echo ""
echo "Iniciando aplicación web..."
echo ""
echo "La aplicación se abrirá en: http://localhost:8501"
echo ""
echo "Presiona Ctrl+C para detener la aplicación"
echo ""
echo "================================================"

cd "$(dirname "$0")"
streamlit run app.py
