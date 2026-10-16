#!/usr/bin/env bash
# =====================================================================
# Script de Configuração Inicial do Ambiente - PFAT Bimestral (Linux/Mac)
# =====================================================================

set -e

echo "=========================================================="
echo "  Iniciando configuração do ambiente PFAT Bimestral..."
echo "=========================================================="

# 1. Verificar Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Erro: python3 não foi encontrado. Por favor, instale o Python 3.10+."
    exit 1
fi

PYTHON_VERSAO=$(python3 --version)
echo "✔ Python detectado: $PYTHON_VERSAO"

# 2. Criar diretórios necessários caso não existam
mkdir -p dados_base dados_entrada dados_saida logs
echo "✔ Diretórios do projeto verificados."

# 3. Criar ambiente virtual se não existir
if [ ! -d "venv" ]; then
    echo "📦 Criando ambiente virtual Python (venv)..."
    python3 -m venv venv
    echo "✔ Ambiente virtual criado com sucesso."
else
    echo "✔ Ambiente virtual (venv) já existe."
fi

# 4. Ativar ambiente e instalar dependências
echo "📥 Instalando / Atualizando dependências de requirements.txt..."
./venv/bin/python -m pip install --upgrade pip
./venv/bin/pip install -r requirements.txt
echo "✔ Dependências instaladas com sucesso."

# 5. Verificar config.yaml
echo ""
if [ ! -f "config.yaml" ]; then
    if [ -f "config.example.yaml" ]; then
        echo "⚠️  AVISO: 'config.yaml' não encontrado!"
        echo "   Criando 'config.yaml' a partir de 'config.example.yaml'..."
        cp config.example.yaml config.yaml
        echo "✔ 'config.yaml' criado. Lembre-se de ajustar credenciais e caminhos."
    fi
else
    echo "✔ 'config.yaml' detectado e pronto para uso."
fi

# 6. Verificar planilhas de entrada
if [ ! -f "dados_base/BD_Identificacao_Operacional_USER.ID.xlsx" ]; then
    echo "ℹ️  Nota: Coloque a planilha base em: dados_base/BD_Identificacao_Operacional_USER.ID.xlsx"
fi

if [ ! -f "dados_entrada/Compilado_resultados_PFAT_2026.xlsx" ]; then
    echo "ℹ️  Nota: Coloque a planilha de resultados em: dados_entrada/Compilado_resultados_PFAT_2026.xlsx"
fi

echo ""
echo "=========================================================="
echo "🎉 Ambiente configurado com sucesso!"
echo "Para executar a automação, use:"
echo "   ./executar.sh   (ou ./venv/bin/python main_dado.py)"
echo "=========================================================="
