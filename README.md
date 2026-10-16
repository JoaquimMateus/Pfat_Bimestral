# Automação de Dados e Gestão de Contatos - PFAT Bimestral (Dataprev)

Pipeline automatizado para consolidação bimestral de pesquisas de satisfação e dados operacionais, com persistência histórica idempotente no MariaDB e exportação para o Power BI.

---

## 📁 Estrutura Organizada do Projeto

```text
Pfat_Bimestral/
├── config.example.yaml     # Modelo de configuração (diretórios, banco e colunas)
├── config.yaml             # Configurações ativas locais (ignorado no git)
├── main_dado.py            # Script principal de execução do pipeline
├── README.md               # Visão geral e instruções rápidas
├── requirements.txt        # Dependências do projeto (pandas, sqlalchemy, etc.)
├── setup_ambiente.sh       # Script de configuração automática (Linux/Mac)
├── setup_ambiente.bat      # Script de configuração automática (Windows)
├── executar.sh             # Script de execução rápida (Linux/Mac)
├── executar.bat            # Script de execução rápida (Windows)
├── gerar_pacote_empresa.sh # Empacota config e planilhas para levar a outro PC
├── pytest.ini              # Configuração da suíte de testes
│
├── dados_base/             # Planilhas cadastrais que não mudam
├── dados_entrada/          # Planilhas de resultados bimestrais recebidas
├── dados_saida/            # Arquivo consolidado para o Power BI e histórico de rodadas
├── docs/                   # Toda a documentação e especificações técnicas
│   ├── GUIA_OUTRO_COMPUTADOR.md     # Passo a passo para rodar no PC da empresa
│   ├── GUIA_TESTE_LOCAL_MARIADB.md   # Passo a passo completo de testes locais
│   ├── guia_de_implanta_o_futuro.md  # Guia para futura implantação na VM Debian (.12)
│   └── DESIGN_AUTOMACAO_DADOS.md     # Especificação original de automação
│
├── logs/                   # Monitoramento de desempenho, tempos e auditoria
├── sql/                    # Scripts DDL para inicialização do banco de dados
│   └── setup_db.sql        # Criação do banco pfat_database e tabela contatos_pfat
│
└── tests/                  # Suíte completa de testes automatizados (TDD)
    └── test_main_dado.py
```

---

## ⚙️ Configuração Rápida do Ambiente

### No Windows:
Dê duplo clique em `setup_ambiente.bat` ou execute no terminal.

### No Linux / macOS:
```bash
./setup_ambiente.sh
```

---

## 🚀 Como Executar a Automação

### No Windows:
Dê duplo clique em `executar.bat` ou execute no terminal.

### No Linux / macOS:
```bash
./executar.sh
```

### Para acompanhar os logs em tempo real:
```bash
tail -f logs/automacao_pfat.log
```

### Para rodar os testes automatizados (TDD):
```bash
./venv/bin/pytest tests/ -v
```

---

## 🏢 Usando em Outro Computador (Empresa)
Consulte o guia detalhado em [`docs/GUIA_OUTRO_COMPUTADOR.md`](file:///home/mateus/Área%20de%20trabalho/Pfat_Bimestral/docs/GUIA_OUTRO_COMPUTADOR.md).


