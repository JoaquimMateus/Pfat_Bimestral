import pandas as pd
import os
import numpy as np
import yaml
import logging
import time
from datetime import datetime

CAMINHO_CONFIG_PADRAO = 'config.yaml'

CONFIG_PADRAO = {
    'diretorios': {
        'base': 'dados_base',
        'entrada': 'dados_entrada',
        'saida': 'dados_saida',
        'logs': 'logs',
    },
    'arquivos': {
        'resultados': 'dados_entrada/Compilado_resultados_PFAT_2026.xlsx',
        'identificacao': 'dados_base/BD_Identificacao_Operacional_USER.ID.xlsx',
        'saida_excel': 'dados_saida/Final_CSV.xlsx',
        'gerar_historico': True,
        'caminho_log': 'logs/automacao_pfat.log',
    },
    'banco': {
        'host': 'localhost',
        'port': 3306,
        'user': 'root',
        'password': 'root',
        'database': 'pfat_database',
        'tabela': 'contatos_pfat',
    },
    'colunas_mapeamento': [
        {"origem": "E mail", "destino_db": "email", "tipo": "string", "obrigatoria": True},
        {"origem": "Valor da string", "destino_db": "valor_string", "tipo": "string"},
        {"origem": "Criação em", "destino_db": "criacao_em", "tipo": "datetime", "obrigatoria": True},
        {"origem": "Obtido em", "destino_db": "obtido_em", "tipo": "datetime"},
        {"origem": "Grupo", "destino_db": "grupo", "tipo": "string"},
        {"origem": "Identificação Operacional (NOME)", "destino_db": "identificacao_operacional", "tipo": "string"},
    ]
}

def carregar_config(caminho_config: str = CAMINHO_CONFIG_PADRAO) -> dict:
    """
    Carrega as configurações a partir do arquivo YAML especificado.
    Caso o arquivo não exista ou ocorra erro, retorna os valores padrão com segurança.
    """
    cfg = {
        'diretorios': dict(CONFIG_PADRAO['diretorios']),
        'arquivos': dict(CONFIG_PADRAO['arquivos']),
        'banco': dict(CONFIG_PADRAO['banco']),
        'colunas_mapeamento': list(CONFIG_PADRAO['colunas_mapeamento'])
    }
    if os.path.exists(caminho_config):
        try:
            with open(caminho_config, 'r', encoding='utf-8') as f:
                dados_yaml = yaml.safe_load(f) or {}
            if 'diretorios' in dados_yaml and isinstance(dados_yaml['diretorios'], dict):
                cfg['diretorios'].update(dados_yaml['diretorios'])
            if 'arquivos' in dados_yaml and isinstance(dados_yaml['arquivos'], dict):
                cfg['arquivos'].update(dados_yaml['arquivos'])
            if 'banco' in dados_yaml and isinstance(dados_yaml['banco'], dict):
                cfg['banco'].update(dados_yaml['banco'])
            if 'colunas_mapeamento' in dados_yaml and isinstance(dados_yaml['colunas_mapeamento'], list):
                cfg['colunas_mapeamento'] = dados_yaml['colunas_mapeamento']
        except Exception as e:
            print(f"Aviso ao carregar {caminho_config}: {e}. Mantendo valores padrão.")
    return cfg

def configurar_logger(caminho_log: str = None) -> logging.Logger:
    """Configura e retorna um logger formatado tanto para arquivo de log quanto para o console."""
    if caminho_log is None:
        caminho_log = CONFIG_ATUAL.get('arquivos', {}).get('caminho_log', 'logs/automacao_pfat.log')

    dir_log = os.path.dirname(caminho_log)
    if dir_log:
        os.makedirs(dir_log, exist_ok=True)

    logger = logging.getLogger("automacao_pfat")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatador = logging.Formatter(
        fmt='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(caminho_log, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatador)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatador)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    return logger

# Inicializa variáveis globais ativas a partir do config.yaml
CONFIG_ATUAL = carregar_config()
ARQUIVO_RESULTADOS = CONFIG_ATUAL['arquivos']['resultados']
ARQUIVO_IDENTIFICACAO = CONFIG_ATUAL['arquivos']['identificacao']
ARQUIVO_SAIDA = CONFIG_ATUAL['arquivos']['saida_excel']
COLUNAS_MAPEAMENTO = CONFIG_ATUAL['colunas_mapeamento']

def transformar_dados(df_resultados: pd.DataFrame, df_identificacao: pd.DataFrame, mapeamento: list[dict] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cruza as planilhas pela chave 'E mail' e gera dois DataFrames:
    1. df_excel: colunas com nomes originais para exportação do Excel.
    2. df_db: colunas renomeadas e tipadas para inserção no banco de dados.
    """
    if mapeamento is None:
        mapeamento = COLUNAS_MAPEAMENTO

    # Cruzamento à esquerda preservando todos os resultados da pesquisa
    df_consolidado = pd.merge(df_resultados, df_identificacao, on='E mail', how='left')

    # Seleção de colunas para o Excel mantendo os nomes originais
    colunas_excel = [item['origem'] for item in mapeamento if item['origem'] in df_consolidado.columns]
    df_excel = df_consolidado[colunas_excel].copy()

    # Construção do DataFrame para o Banco de Dados com tipos e renomeação
    dados_db = {}
    for item in mapeamento:
        origem = item['origem']
        destino = item['destino_db']
        tipo = item.get('tipo', 'string')

        if origem in df_consolidado.columns:
            serie = df_consolidado[origem].copy()
            if tipo == 'datetime':
                serie = pd.to_datetime(serie, errors='coerce')
            dados_db[destino] = serie
        else:
            dados_db[destino] = None

    df_db = pd.DataFrame(dados_db)
    # Garante que valores ausentes (NaN) virem None para persistência correta como NULL no banco
    df_db = df_db.replace({np.nan: None})

    return df_excel, df_db

def obter_config_banco(cfg_banco: dict = None) -> dict:
    """Retorna as configurações de conexão mesclando config.yaml e variáveis de ambiente."""
    banco_base = cfg_banco or CONFIG_ATUAL.get('banco', CONFIG_PADRAO['banco'])
    return {
        'host': os.environ.get('DB_HOST', banco_base.get('host', 'localhost')),
        'port': int(os.environ.get('DB_PORT', banco_base.get('port', 3306))),
        'user': os.environ.get('DB_USER', banco_base.get('user', 'root')),
        'password': os.environ.get('DB_PASSWORD', banco_base.get('password', 'root')),
        'database': os.environ.get('DB_NAME', banco_base.get('database', 'pfat_database')),
        'tabela': os.environ.get('DB_TABLE', banco_base.get('tabela', 'contatos_pfat')),
    }

def criar_engine_banco(config: dict = None, url: str = None):
    """Cria e retorna uma Engine SQLAlchemy para o banco de dados."""
    from sqlalchemy import create_engine
    if url:
        return create_engine(url)
    if config is None:
        config = obter_config_banco()

    db_url = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    return create_engine(db_url)

def inserir_contatos(df_db: pd.DataFrame, engine, tabela: str = None) -> int:
    """
    Insere os contatos no banco de dados com suporte a inserção idempotente (upsert).
    Preserva o histórico baseado na chave única (email, criacao_em).
    """
    if df_db.empty:
        return 0

    if tabela is None:
        tabela = CONFIG_ATUAL.get('banco', {}).get('tabela', 'contatos_pfat')

    from sqlalchemy import text

    colunas = list(df_db.columns)
    colunas_sql = ", ".join(colunas)
    placeholders = ", ".join([f":{c}" for c in colunas])
    colunas_update = [c for c in colunas if c not in ('email', 'criacao_em')]

    is_sqlite = engine.dialect.name == "sqlite"
    if is_sqlite:
        updates = ", ".join([f"{c} = excluded.{c}" for c in colunas_update])
        sql = f"""
            INSERT INTO {tabela} ({colunas_sql})
            VALUES ({placeholders})
            ON CONFLICT(email, criacao_em) DO UPDATE SET {updates}
        """
    else:
        updates = ", ".join([f"{c} = VALUES({c})" for c in colunas_update])
        sql = f"""
            INSERT INTO {tabela} ({colunas_sql})
            VALUES ({placeholders})
            ON DUPLICATE KEY UPDATE {updates}
        """

    registros = df_db.to_dict(orient='records')
    for reg in registros:
        for k, v in reg.items():
            if pd.isna(v):
                reg[k] = None
            elif isinstance(v, (pd.Timestamp, datetime)):
                reg[k] = v.strftime('%Y-%m-%d %H:%M:%S') if is_sqlite else v.to_pydatetime()

    with engine.begin() as conn:
        conn.execute(text(sql), registros)

    return len(registros)

def processar_pipeline(caminho_resultados: str = None,
                       caminho_identificacao: str = None,
                       caminho_saida_excel: str = None,
                       engine=None,
                       caminho_config: str = None,
                       caminho_log: str = None,
                       gerar_historico: bool = None) -> dict:
    """
    Executa o pipeline completo:
    1. Carrega parâmetros do config.yaml (ou argumentos passados).
    2. Inicializa o sistema de logging com métricas de tempo.
    3. Lê e valida os arquivos Excel de entrada.
    4. Cruza e transforma os dados respeitando o mapeamento de colunas configurado.
    5. Gera o arquivo consolidado Excel e opcionalmente uma cópia histórica com timestamp.
    6. Conecta e insere no MariaDB de forma idempotente, preservando histórico.
    """
    inicio_geral = time.time()
    cfg = carregar_config(caminho_config) if caminho_config else CONFIG_ATUAL

    caminho_resultados = caminho_resultados or cfg['arquivos']['resultados']
    caminho_identificacao = caminho_identificacao or cfg['arquivos']['identificacao']
    caminho_saida_excel = caminho_saida_excel or cfg['arquivos']['saida_excel']
    caminho_log = caminho_log or cfg['arquivos'].get('caminho_log', 'logs/automacao_pfat.log')
    if gerar_historico is None:
        gerar_historico = cfg['arquivos'].get('gerar_historico', True)
    mapeamento = cfg['colunas_mapeamento']

    logger = configurar_logger(caminho_log)
    logger.info("=== Iniciando execução da automação PFAT 2026 ===")

    resultado = {
        'excel_gerado': False,
        'banco_atualizado': False,
        'linhas_banco': 0,
        'erro_banco': None,
        'arquivo_excel': caminho_saida_excel,
        'arquivo_historico': None
    }

    # Resolução de caminhos com fallback para diretório local se necessário
    if not os.path.exists(caminho_resultados) and os.path.exists(os.path.basename(caminho_resultados)):
        caminho_resultados = os.path.basename(caminho_resultados)
    if not os.path.exists(caminho_identificacao) and os.path.exists(os.path.basename(caminho_identificacao)):
        caminho_identificacao = os.path.basename(caminho_identificacao)

    if not os.path.exists(caminho_resultados):
        msg = f"Arquivo de resultados não encontrado: {caminho_resultados}"
        logger.error(msg)
        raise FileNotFoundError(msg)
    if not os.path.exists(caminho_identificacao):
        msg = f"Arquivo de identificação não encontrado: {caminho_identificacao}"
        logger.error(msg)
        raise FileNotFoundError(msg)

    # 1. Leitura
    t0 = time.time()
    logger.info(f"Lendo planilha de resultados: {caminho_resultados}")
    df_resultados = pd.read_excel(caminho_resultados)
    logger.info(f"Lendo planilha de identificação: {caminho_identificacao}")
    df_identificacao = pd.read_excel(caminho_identificacao)
    logger.info(f"Leitura concluída em {time.time() - t0:.2f}s ({len(df_resultados)} resultados, {len(df_identificacao)} cadastros)")

    # 2. Transformação
    t0 = time.time()
    logger.info("Realizando cruzamento e transformação dos dados...")
    df_excel, df_db = transformar_dados(df_resultados, df_identificacao, mapeamento=mapeamento)
    logger.info(f"Transformação concluída em {time.time() - t0:.2f}s ({len(df_excel)} registros prontos)")

    # 3. Geração do Excel pontual e histórico
    t0 = time.time()
    dir_saida = os.path.dirname(caminho_saida_excel)
    if dir_saida:
        os.makedirs(dir_saida, exist_ok=True)

    logger.info(f"Gerando arquivo Excel atual: {caminho_saida_excel}")
    df_excel.to_excel(caminho_saida_excel, index=False)
    resultado['excel_gerado'] = True

    if gerar_historico:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_nome, ext = os.path.splitext(caminho_saida_excel)
        caminho_historico = f"{base_nome}_{timestamp_str}{ext}"
        df_excel.to_excel(caminho_historico, index=False)
        resultado['arquivo_historico'] = caminho_historico
        logger.info(f"Cópia histórica preservada: {caminho_historico}")

    logger.info(f"Exportação Excel concluída em {time.time() - t0:.2f}s")

    # 4. Carga no MariaDB
    t0 = time.time()
    try:
        if engine is None:
            engine = criar_engine_banco(config=obter_config_banco(cfg.get('banco')))
        logger.info("Conectando ao banco de dados e gravando registros...")
        tabela = cfg.get('banco', {}).get('tabela', 'contatos_pfat')
        linhas = inserir_contatos(df_db, engine, tabela=tabela)
        resultado['banco_atualizado'] = True
        resultado['linhas_banco'] = linhas
        logger.info(f"Persistência no banco concluída em {time.time() - t0:.2f}s: {linhas} registros inseridos/atualizados na tabela '{tabela}'")
    except Exception as e:
        resultado['erro_banco'] = str(e)
        logger.warning(f"O arquivo Excel foi gerado com sucesso, mas a inserção no banco falhou: {e}")
        logger.warning("Verifique se o serviço/container do MariaDB está em execução.")

    tempo_total = time.time() - inicio_geral
    logger.info(f"=== Pipeline finalizado em {tempo_total:.2f}s (Excel: OK | Banco: {'OK' if resultado['banco_atualizado'] else 'FALHA'}) ===\n")
    return resultado

def processar_dados():
    """Função de compatibilidade para chamadas legadas."""
    return processar_pipeline()

if __name__ == "__main__":
    cfg = carregar_config()
    res_path = cfg['arquivos']['resultados']
    id_path = cfg['arquivos']['identificacao']

    # Valida caminhos (incluindo fallback local)
    res_ok = os.path.exists(res_path) or os.path.exists(os.path.basename(res_path))
    id_ok = os.path.exists(id_path) or os.path.exists(os.path.basename(id_path))

    if res_ok and id_ok:
        processar_pipeline()
    else:
        print("Erro: Certifique-se de que os arquivos de entrada estão nas pastas configuradas em config.yaml.")
