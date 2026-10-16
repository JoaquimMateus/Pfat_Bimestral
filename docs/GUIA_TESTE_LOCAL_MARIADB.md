# Guia de Teste Local: MariaDB e Automação de Dados (PFAT 2026)

Este guia orienta como testar e operar a automação na sua máquina local antes de qualquer implantação na VM de monitoramento.

---

## 1. Status Atual do Ambiente Local
- **Container MariaDB Local:** Criado e em execução com o nome `mariadb-local`.
- **Porta:** `3306` mapeada para `localhost`.
- **Banco de Dados:** `pfat_database`.
- **Tabela:** `contatos_pfat` com chave única composta `(email, criacao_em)` para preservar o histórico de rodadas bimestrais e dados retroativos.
- **Credenciais Padrão:**
  - Usuário: `root`
  - Senha: `root`
  - Host: `localhost`
  - Porta: `3306`

---

## 2. Estrutura de Pastas Organizada

A arquitetura de arquivos foi separada por responsabilidades:

- 📁 **`dados_base/`**: Guarda a planilha base cadastral que não muda (`BD_Identificacao_Operacional_USER.ID.xlsx`).
- 📁 **`dados_entrada/`**: Local onde você coloca a planilha de resultados de cada rodada da pesquisa (`Compilado_resultados_PFAT_2026.xlsx`).
- 📁 **`dados_saida/`**:
  - `Final_CSV.xlsx`: Arquivo fixo atualizado a cada execução (apontado pelo seu Power BI).
  - `Final_CSV_YYYYMMDD_HHMMSS.xlsx`: Cópias históricas carimbadas com data e hora de cada rodada.
- 📁 **`logs/`**:
  - `automacao_pfat.log`: Registra início, fim, tempo gasto em cada etapa, quantidade de linhas e diagnósticos detalhados.

---

## 3. Como Executar e Monitorar a Automação

Abra o terminal na pasta do projeto (`Pfat_Bimestral`) e execute:

```bash
python3 main_dado.py
```

### Para acompanhar os logs em tempo real:
```bash
tail -f logs/automacao_pfat.log
```

---

## 3. Como Customizar Tudo pelo Arquivo `config.yaml`

Agora todas as definições da automação estão centralizadas no arquivo `config.yaml`:

```yaml
arquivos:
  resultados: "Compilado_resultados_PFAT_2026.xlsx"
  identificacao: "BD_Identificacao_Operacional_USER.ID.xlsx"
  saida_excel: "Final_CSV.xlsx"

banco:
  host: "localhost"           # Altere para o IP da VM (ex: 192.168.1.12) na futura implantação
  port: 3306
  user: "root"
  password: "root"
  database: "pfat_database"
  tabela: "contatos_pfat"

colunas_mapeamento:
  - origem: "E mail"
    destino_db: "email"
    tipo: "string"
    obrigatoria: true

  - origem: "Valor da string"
    destino_db: "valor_string"
    tipo: "string"

  - origem: "Criação em"
    destino_db: "criacao_em"
    tipo: "datetime"
    obrigatoria: true

  - origem: "Obtido em"
    destino_db: "obtido_em"
    tipo: "datetime"

  - origem: "Grupo"
    destino_db: "grupo"
    tipo: "string"

  - origem: "Identificação Operacional (NOME)"
    destino_db: "identificacao_operacional"
    tipo: "string"
```

- **Para alterar credenciais ou host do banco:** mude os campos na seção `banco` (quando for migrar para a VM, basta colocar o IP `192.168.1.12` e usuário/senha da VM).
- **Para alterar nomes de arquivos:** mude a seção `arquivos`.
- **Para adicionar ou remover colunas:** adicione ou remova blocos dentro de `colunas_mapeamento`. Não precisa encostar no código Python!

---

## 4. Comandos Úteis do MariaDB Local (Docker)

### Iniciar o container (caso tenha sido parado):
```bash
docker start mariadb-local
```

### Parar o container:
```bash
docker stop mariadb-local
```

### Consultar a quantidade de registros no banco:
```bash
docker exec -it mariadb-local mariadb -uroot -proot -e "SELECT COUNT(*) AS total FROM pfat_database.contatos_pfat;"
```

### Visualizar os últimos contatos inseridos:
```bash
docker exec -it mariadb-local mariadb -uroot -proot -e "SELECT email, criacao_em, grupo, identificacao_operacional FROM pfat_database.contatos_pfat LIMIT 10;"
```

### Reaplicar o esquema do banco do zero (se desejar resetar):
```bash
docker exec -i mariadb-local mariadb -uroot -proot pfat_database < sql/setup_db.sql
```

---

## 5. Como Rodar a Suíte de Testes Automatizados (TDD)

Para verificar a integridade de todas as regras de negócio (cruzamento, conversão de datas, upsert idempotente e tolerância a falhas de conexão):

```bash
pytest tests/ -v
```
