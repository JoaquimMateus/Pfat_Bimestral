# Guia de Migração para a VM Debian (192.168.1.12)

**Aviso:** Todos os desenvolvimentos e testes atuais devem ser mantidos estritamente na máquina **LOCAL**. Siga este guia *apenas* quando o script estiver validado e for o momento oficial de migrar o projeto para o servidor.

## 1. Transferência Manual de Arquivos
Quando for o momento, copie os seguintes arquivos da sua máquina local para uma pasta na VM (ex: `/home/usuario/automacao_pfat/`):
- `main_dado.py`
- `setup_db.sql`
- Os arquivos Excel originais (`Compilado...` e `BD_Identificacao...`)

*(Você pode usar um pendrive, pasta compartilhada ou qualquer ferramenta visual de transferência segura que preferir, sem necessidade de comandos automatizados agora).*

## 2. Preparação do Banco de Dados no Servidor
Acesse a VM localmente ou via SSH. Na pasta onde você salvou os arquivos, crie o banco de dados e a tabela usando o arquivo SQL gerado:
```bash
sudo mysql < setup_db.sql
```

## 3. Criação do Ambiente Virtual (venv) na VM
Para evitar o erro de ambiente gerenciado externamente (PEP 668) na VM Debian, crie um ambiente virtual isolado dentro da pasta do projeto:
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Instalação das Bibliotecas no Servidor
Com o `venv` ativado na VM, instale as dependências:
```bash
pip install pandas openpyxl mysql-connector-python sqlalchemy
```

## 5. Ajuste Finais e Execução
Antes de rodar o script no servidor, abra o `main_dado.py` e verifique se as credenciais do banco de dados (que criaremos na próxima etapa do nosso desenvolvimento local) estão corretas, apontando para `localhost` (já que o banco estará na mesma VM).
Para rodar:
```bash
python main_dado.py
```