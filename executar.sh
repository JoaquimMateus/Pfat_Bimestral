#!/usr/bin/env bash
# =====================================================================
# Atalho para executar a automação PFAT Bimestral (Linux/Mac)
# =====================================================================

if [ ! -d "venv" ]; then
    echo "⚠️ Ambiente virtual não encontrado. Executando configuração inicial primeiro..."
    ./setup_ambiente.sh
fi

./venv/bin/python main_dado.py "$@"
