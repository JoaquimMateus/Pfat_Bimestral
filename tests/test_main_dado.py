import pandas as pd
import numpy as np
import pytest
from datetime import datetime

# Importações do módulo alvo
from main_dado import transformar_dados, COLUNAS_MAPEAMENTO

def test_transformar_dados_sucesso():
    # Dados simulados para resultados
    df_resultados = pd.DataFrame([
        {
            'Número': 1,
            'E mail': 'usuario1@dataprev.gov.br',
            'Valor da string': 'Positivo',
            'Criação em': '2026-06-17 09:49:49',
            'Obtido em': '2026-06-17 12:40:11'
        },
        {
            'Número': 2,
            'E mail': 'usuario2@dataprev.gov.br',
            'Valor da string': 'Neutro',
            'Criação em': '2026-06-17 10:00:00',
            'Obtido em': '2026-06-17 13:00:00'
        }
    ])

    # Dados simulados para identificação operacional (apenas usuario1 possui correspondência)
    df_identificacao = pd.DataFrame([
        {
            'E mail': 'usuario1@dataprev.gov.br',
            'Grupo': 'Operação A',
            'Identificação Operacional (NOME)': 'João Silva',
            'Cliente': 'Cliente X',
            'Contrato': '123'
        }
    ])

    df_excel, df_db = transformar_dados(df_resultados, df_identificacao, COLUNAS_MAPEAMENTO)

    # 1. Validações do DataFrame para Excel
    assert list(df_excel.columns) == [
        'E mail',
        'Valor da string',
        'Criação em',
        'Obtido em',
        'Grupo',
        'Identificação Operacional (NOME)'
    ]
    assert len(df_excel) == 2
    assert df_excel.loc[0, 'Identificação Operacional (NOME)'] == 'João Silva'

    # 2. Validações do DataFrame para Banco de Dados
    assert list(df_db.columns) == [
        'email',
        'valor_string',
        'criacao_em',
        'obtido_em',
        'grupo',
        'identificacao_operacional'
    ]
    assert len(df_db) == 2
    
    # Validação de conversão para Datetime
    assert isinstance(df_db.loc[0, 'criacao_em'], (datetime, pd.Timestamp))
    assert df_db.loc[0, 'criacao_em'] == pd.Timestamp('2026-06-17 09:49:49')
    
    # Validação de substituição de NaN por None para usuario2 (sem match em identificacao)
    assert df_db.loc[1, 'grupo'] is None or pd.isna(df_db.loc[1, 'grupo'])
    assert df_db.loc[1, 'identificacao_operacional'] is None or pd.isna(df_db.loc[1, 'identificacao_operacional'])

def test_transformar_dados_coluna_ausente():
    df_resultados = pd.DataFrame([
        {'E mail': 'a@b.com', 'Criação em': '2026-01-01 10:00:00'}
    ])
    df_identificacao = pd.DataFrame([
        {'E mail': 'a@b.com'}
    ])
    # Passando mapeamento com colunas que não constam nas planilhas de entrada
    mapeamento_custom = [
        {"origem": "E mail", "destino_db": "email", "tipo": "string"},
        {"origem": "Criação em", "destino_db": "criacao_em", "tipo": "datetime"},
        {"origem": "Coluna Inexistente", "destino_db": "coluna_inexistente", "tipo": "string"}
    ]
    df_excel, df_db = transformar_dados(df_resultados, df_identificacao, mapeamento_custom)
    assert "Coluna Inexistente" not in df_excel.columns
    assert "coluna_inexistente" in df_db.columns
    assert df_db.loc[0, "coluna_inexistente"] is None

def test_inserir_contatos_idempotente():
    from main_dado import criar_engine_banco, inserir_contatos
    from sqlalchemy import text

    # Usando SQLite em memória para teste unitário
    engine = criar_engine_banco(url="sqlite:///:memory:")

    # Cria tabela contatos_pfat com a mesma estrutura de setup_db.sql
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE contatos_pfat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                valor_string TEXT,
                criacao_em DATETIME NOT NULL,
                obtido_em DATETIME,
                grupo TEXT,
                identificacao_operacional TEXT,
                UNIQUE (email, criacao_em)
            );
        """))

    # Lote 1: Duas respostas de pesquisas diferentes (Janeiro e Março)
    df_lote1 = pd.DataFrame([
        {
            'email': 'joao@dataprev.gov.br',
            'valor_string': 'Bom',
            'criacao_em': datetime(2026, 1, 15, 10, 0, 0),
            'obtido_em': datetime(2026, 1, 15, 12, 0, 0),
            'grupo': 'Grupo A',
            'identificacao_operacional': 'João'
        },
        {
            'email': 'maria@dataprev.gov.br',
            'valor_string': 'Excelente',
            'criacao_em': datetime(2026, 3, 10, 8, 30, 0),
            'obtido_em': datetime(2026, 3, 10, 9, 0, 0),
            'grupo': 'Grupo B',
            'identificacao_operacional': 'Maria'
        }
    ])

    linhas_processadas = inserir_contatos(df_lote1, engine)
    assert linhas_processadas == 2

    # Verifica se 2 registros foram salvos
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM contatos_pfat")).scalar()
        assert total == 2

    # Lote 2: Reprocessando o Lote 1 (com atualização do valor_string de João)
    df_lote1_reprocessado = df_lote1.copy()
    df_lote1_reprocessado.loc[0, 'valor_string'] = 'Ótimo'

    linhas_reprocessadas = inserir_contatos(df_lote1_reprocessado, engine)
    assert linhas_reprocessadas == 2

    # Verifica que NÃO duplicou registros (total continua 2) e atualizou o valor
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM contatos_pfat")).scalar()
        assert total == 2
        valor_joao = conn.execute(text("SELECT valor_string FROM contatos_pfat WHERE email = 'joao@dataprev.gov.br'")).scalar()
        assert valor_joao == 'Ótimo'

    # Lote 3: Nova rodada bimestral (Maio) para o mesmo usuário João (Preservação de Histórico)
    df_lote3 = pd.DataFrame([
        {
            'email': 'joao@dataprev.gov.br',
            'valor_string': 'Regular',
            'criacao_em': datetime(2026, 5, 20, 14, 0, 0),
            'obtido_em': datetime(2026, 5, 20, 15, 0, 0),
            'grupo': 'Grupo A',
            'identificacao_operacional': 'João'
        }
    ])
    inserir_contatos(df_lote3, engine)

    # Verifica que agora existem 3 registros (João tem Janeiro e Maio preservados!)
    with engine.connect() as conn:
        total = conn.execute(text("SELECT COUNT(*) FROM contatos_pfat")).scalar()
        assert total == 3
        registros_joao = conn.execute(text("SELECT COUNT(*) FROM contatos_pfat WHERE email = 'joao@dataprev.gov.br'")).scalar()
        assert registros_joao == 2

def test_processar_pipeline_sucesso(tmp_path):
    from main_dado import processar_pipeline, criar_engine_banco
    from sqlalchemy import text

    # Cria arquivos temporários de teste
    caminho_res = tmp_path / "res.xlsx"
    caminho_id = tmp_path / "id.xlsx"
    caminho_out = tmp_path / "out.xlsx"

    df_res = pd.DataFrame([
        {'Número': 1, 'E mail': 'teste@dp.gov.br', 'Valor da string': '10', 'Criação em': '2026-06-01 10:00:00', 'Obtido em': '2026-06-01 11:00:00'}
    ])
    df_id = pd.DataFrame([
        {'E mail': 'teste@dp.gov.br', 'Grupo': 'G1', 'Identificação Operacional (NOME)': 'Tester'}
    ])
    df_res.to_excel(caminho_res, index=False)
    df_id.to_excel(caminho_id, index=False)

    engine = criar_engine_banco(url="sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE contatos_pfat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                valor_string TEXT,
                criacao_em DATETIME NOT NULL,
                obtido_em DATETIME,
                grupo TEXT,
                identificacao_operacional TEXT,
                UNIQUE (email, criacao_em)
            );
        """))

    resultado = processar_pipeline(
        caminho_resultados=str(caminho_res),
        caminho_identificacao=str(caminho_id),
        caminho_saida_excel=str(caminho_out),
        engine=engine
    )

    assert resultado['excel_gerado'] is True
    assert resultado['banco_atualizado'] is True
    assert resultado['linhas_banco'] == 1
    assert caminho_out.exists()

def test_processar_pipeline_banco_indisponivel(tmp_path):
    from main_dado import processar_pipeline, criar_engine_banco

    caminho_res = tmp_path / "res.xlsx"
    caminho_id = tmp_path / "id.xlsx"
    caminho_out = tmp_path / "out.xlsx"

    df_res = pd.DataFrame([
        {'Número': 1, 'E mail': 'teste@dp.gov.br', 'Valor da string': '10', 'Criação em': '2026-06-01 10:00:00', 'Obtido em': '2026-06-01 11:00:00'}
    ])
    df_id = pd.DataFrame([
        {'E mail': 'teste@dp.gov.br', 'Grupo': 'G1', 'Identificação Operacional (NOME)': 'Tester'}
    ])
    df_res.to_excel(caminho_res, index=False)
    df_id.to_excel(caminho_id, index=False)

    # Engine apontando para porta inexistente / inacessível para simular banco offline
    engine_offline = criar_engine_banco(url="mysql+pymysql://root:root@127.0.0.1:59999/pfat_database?connect_timeout=1")

    resultado = processar_pipeline(
        caminho_resultados=str(caminho_res),
        caminho_identificacao=str(caminho_id),
        caminho_saida_excel=str(caminho_out),
        engine=engine_offline
    )

    # O arquivo Excel DEVE ser gerado com sucesso mesmo com o banco offline
    assert resultado['excel_gerado'] is True
    assert resultado['banco_atualizado'] is False
    assert resultado['linhas_banco'] == 0
    assert resultado['erro_banco'] is not None
    assert caminho_out.exists()

def test_carregar_config_yaml(tmp_path):
    from main_dado import carregar_config

    yaml_conteudo = """
arquivos:
  resultados: custom_res.xlsx
  identificacao: custom_id.xlsx
  saida_excel: custom_out.xlsx

banco:
  host: 192.168.1.100
  port: 3307
  user: my_user
  password: my_password
  database: my_db
  tabela: my_table

colunas_mapeamento:
  - origem: "E mail"
    destino_db: email
    tipo: string
    obrigatoria: true
  - origem: "Grupo"
    destino_db: grupo
    tipo: string
"""
    caminho_yaml = tmp_path / "config.yaml"
    caminho_yaml.write_text(yaml_conteudo, encoding="utf-8")

    cfg = carregar_config(str(caminho_yaml))
    assert cfg['arquivos']['resultados'] == 'custom_res.xlsx'
    assert cfg['banco']['host'] == '192.168.1.100'
    assert cfg['banco']['port'] == 3307
    assert len(cfg['colunas_mapeamento']) == 2
    assert cfg['colunas_mapeamento'][0]['origem'] == "E mail"

def test_carregar_config_arquivo_inexistente():
    from main_dado import carregar_config
    # Deve retornar a configuração padrão sem lançar exceção
    cfg = carregar_config("caminho_inexistente_qualquer.yaml")
    assert 'arquivos' in cfg
    assert 'banco' in cfg
    assert 'colunas_mapeamento' in cfg

def test_processar_pipeline_com_historico_e_log(tmp_path):
    from main_dado import processar_pipeline, criar_engine_banco
    from sqlalchemy import text
    import glob

    dir_base = tmp_path / "dados_base"
    dir_entrada = tmp_path / "dados_entrada"
    dir_saida = tmp_path / "dados_saida"
    dir_logs = tmp_path / "logs"

    dir_base.mkdir()
    dir_entrada.mkdir()
    dir_saida.mkdir()
    dir_logs.mkdir()

    caminho_res = dir_entrada / "res.xlsx"
    caminho_id = dir_base / "id.xlsx"
    caminho_out = dir_saida / "Final_CSV.xlsx"
    caminho_log = dir_logs / "automacao.log"

    df_res = pd.DataFrame([
        {'Número': 1, 'E mail': 'log@dp.gov.br', 'Valor da string': '10', 'Criação em': '2026-06-01 10:00:00', 'Obtido em': '2026-06-01 11:00:00'}
    ])
    df_id = pd.DataFrame([
        {'E mail': 'log@dp.gov.br', 'Grupo': 'G1', 'Identificação Operacional (NOME)': 'Log Tester'}
    ])
    df_res.to_excel(caminho_res, index=False)
    df_id.to_excel(caminho_id, index=False)

    engine = criar_engine_banco(url="sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE contatos_pfat (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                valor_string TEXT,
                criacao_em DATETIME NOT NULL,
                obtido_em DATETIME,
                grupo TEXT,
                identificacao_operacional TEXT,
                UNIQUE (email, criacao_em)
            );
        """))

    resultado = processar_pipeline(
        caminho_resultados=str(caminho_res),
        caminho_identificacao=str(caminho_id),
        caminho_saida_excel=str(caminho_out),
        caminho_log=str(caminho_log),
        gerar_historico=True,
        engine=engine
    )

    # 1. Arquivo pontual Final_CSV.xlsx deve existir
    assert caminho_out.exists()

    # 2. Arquivo com timestamp de histórico deve ter sido criado em dados_saida/
    arquivos_saida = list(dir_saida.glob("Final_CSV_*.xlsx"))
    assert len(arquivos_saida) >= 1

    # 3. Arquivo de LOG deve existir e conter métricas de tempo e registros
    assert caminho_log.exists()
    conteudo_log = caminho_log.read_text(encoding="utf-8")
    assert "INFO" in conteudo_log
    assert "concluído" in conteudo_log.lower() or "registros" in conteudo_log.lower()





