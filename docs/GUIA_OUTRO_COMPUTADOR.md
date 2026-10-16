# Guia: Como Executar o Projeto em Outro Computador (Empresa)

Este guia prático mostra como configurar e rodar o projeto rapidamente no seu outro computador.

---

## 📋 O que você precisa:

1. **Repositório Git clonado** (contém todo o código e scripts).
2. **Arquivo de configuração e planilhas de entrada:**
   - O arquivo `config.yaml`
   - Planilha base: `dados_base/BD_Identificacao_Operacional_USER.ID.xlsx`
   - Planilha de resultados: `dados_entrada/Compilado_resultados_PFAT_2026.xlsx`

> 💡 **Dica Prática:** Você pode levar o arquivo `pacote_empresa_pfat.zip` em um pendrive ou transferência interna. Ele já contém os 3 arquivos organizados nas pastas certas.

---

## 🚀 Passo a Passo

### 1. Clonar o Repositório no Novo Computador
Abra o terminal (Linux) ou Prompt/PowerShell/Git Bash (Windows) e clone o repositório:
```bash
git clone https://github.com/JoaquimMateus/Pfat_Bimestral.git
cd Pfat_Bimestral
```

---

### 2. Copiar as Configurações e Planilhas
- Se você levou o arquivo `pacote_empresa_pfat.zip`, basta colocá-lo dentro da pasta `Pfat_Bimestral` e descompactar:
  - **Linux:** `unzip pacote_empresa_pfat.zip`
  - **Windows:** Clique com o botão direito em `pacote_empresa_pfat.zip` -> *Extrair Tudo Aqui* (ou abra e copie os arquivos para a raiz do projeto).
- Se preferir copiar manualmente:
  - Copie seu `config.yaml` para a raiz do projeto.
  - Coloque `BD_Identificacao_Operacional_USER.ID.xlsx` dentro de `dados_base/`.
  - Coloque `Compilado_resultados_PFAT_2026.xlsx` dentro de `dados_entrada/`.

---

### 3. Configurar o Ambiente com 1 Clique / Comando

#### No Windows:
Basta dar **duplo clique** no arquivo:
```cmd
setup_ambiente.bat
```
*(Ou execute no Prompt de Comando: `setup_ambiente.bat`)*

#### No Linux / macOS:
No terminal, execute:
```bash
./setup_ambiente.sh
```

O script cuidará de:
1. Criar o ambiente virtual isolado (`venv`).
2. Instalar todas as bibliotecas necessárias (`pandas`, `openpyxl`, `sqlalchemy`, `pymysql`, etc.).
3. Verificar a presença dos diretórios e do `config.yaml`.

---

### 4. Executar a Automação

#### No Windows:
Basta dar **duplo clique** em:
```cmd
executar.bat
```

#### No Linux / macOS:
```bash
./executar.sh
```

---

### 5. Ajustes no `config.yaml` (se necessário)
Caso o banco de dados no outro computador esteja em outro IP ou porta (por exemplo, na VM Debian `192.168.1.12`), basta abrir o `config.yaml` no bloco `banco:` e alterar:

```yaml
banco:
  host: "192.168.1.12"      # IP do banco na rede da empresa
  port: 3306
  user: "seu_usuario"
  password: "sua_senha"
  database: "pfat_database"
  tabela: "contatos_pfat"
```
