# Design de Automação de Dados - PFAT 2026

## Objetivo
Automatizar o cruzamento de duas planilhas Excel para o COPILOT/Painel, consolidando as informações através da chave "E mail".

## Entradas
1. `Compilado_resultados_PFAT_2026.xlsx`
2. `BD_Identificacao_Operacional_USER.ID.xlsx`

## Processamento
- **Chave de Cruzamento (Merge):** Coluna "E mail"
- **Colunas a Manter:**
  - E mail
  - Valor da string
  - Criação em
  - Obtido em
- **Colunas a Adicionar (vindas da segunda planilha):**
  - Grupo
  - Identificação Operacional (NOME)

## Saída
- **Nome do Arquivo Gerado:** `Final_CSV.xlsx` (pode ser ajustado na variável do script).
- **Destino:** Banco de Dados MariaDB (VM HCSO Debian - IP: 192.168.1.12).
