#!/usr/bin/env bash
# =====================================================================
# Gera o arquivo zip com os dados e configuração para levar à empresa
# =====================================================================

NOME_PACOTE="pacote_empresa_pfat.zip"

echo "📦 Compactando config.yaml e planilhas de entrada em $NOME_PACOTE..."

rm -f "$NOME_PACOTE"

zip -r "$NOME_PACOTE" \
    config.yaml \
    dados_base/BD_Identificacao_Operacional_USER.ID.xlsx \
    dados_entrada/Compilado_resultados_PFAT_2026.xlsx

echo "✔ Pacote gerado com sucesso: $NOME_PACOTE"
echo "Basta copiar este arquivo para o outro computador e descompactá-lo dentro da pasta do projeto clonado."
