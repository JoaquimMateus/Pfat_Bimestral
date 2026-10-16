# Automação de Dados e Gestão de Contatos - PFAT Bimestral (Dataprev)

Pipeline automatizado para consolidação bimestral de pesquisas de satisfação e dados operacionais, com persistência histórica idempotente no MariaDB e exportação para o Power BI.

---

## 📁 Estrutura Organizada do Projeto

```text
Pfat_Bimestral/
├── config.example.yaml  # Modelo de configuração (diretórios, banco e colunas)
├── config.yaml          # Configurações ativas locais (ignorado no git)
├── main_dado.py         # Script principal de execução do pipeline
├── README.md            # Este arquivo com visão geral e instruções rápidas
├── pytest.ini           # Configuração da suíte de testes
│
├── dados_base/          # Planilhas cadastrais que não mudam
├── dados_entrada/       # Planilhas de resultados bimestrais recebidas
├── dados_saida/         # Arquivo consolidado para o Power BI e histórico de rodadas
├── docs/                # Toda a documentação e especificações técnicas
│   ├── GUIA_TESTE_LOCAL_MARIADB.md        # Passo a passo completo de testes locais
│   ├── guia_de_implanta_o_futuro.md       # Guia para futura implantação na VM Debian (.12)
│   └── DESIGN_AUTOMACAO_DADOS.md          # Especificação original de automação
│
├── logs/                # Monitoramento de desempenho, tempos e auditoria
├── sql/                 # Scripts DDL para inicialização do banco de dados
│   └── setup_db.sql     # Criação do banco pfat_database e tabela contatos_pfat
│
└── tests/               # Suíte completa de testes automatizados (TDD)
    └── test_main_dado.py
```

---

## ⚙️ Configuração Inicial

Antes de executar, copie o arquivo de exemplo e ajuste suas credenciais conforme necessário:

```bash
cp config.example.yaml config.yaml
```

Todas as opções (pastas, arquivos, credenciais de banco e lista de colunas) podem ser modificadas diretamente no arquivo `config.yaml`.

---

## 🚀 Como Executar a Automação

```bash
python3 main_dado.py
```

### Para acompanhar os logs em tempo real:
```bash
tail -f logs/automacao_pfat.log
```

### Para rodar os testes automatizados (TDD):
```bash
pytest tests/ -v
```

