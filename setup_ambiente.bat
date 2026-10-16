@echo off
REM =====================================================================
REM Script de Configuração Inicial do Ambiente - PFAT Bimestral (Windows)
REM =====================================================================

echo ==========================================================
echo   Iniciando configuracao do ambiente PFAT Bimestral...
echo ==========================================================

REM 1. Verificar Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERRO] Python nao foi encontrado no PATH do sistema.
    echo Por favor, instale o Python 3.10+ marcando 'Add python.exe to PATH'.
    pause
    exit /b 1
)

echo [OK] Python detectado.

REM 2. Criar pastas necessárias
if not exist dados_base mkdir dados_base
if not exist dados_entrada mkdir dados_entrada
if not exist dados_saida mkdir dados_saida
if not exist logs mkdir logs
echo [OK] Pastas do projeto verificadas.

REM 3. Criar ambiente virtual
if not exist venv (
    echo [INFO] Criando ambiente virtual Python (venv)...
    python -m venv venv
    echo [OK] Ambiente virtual criado.
) else (
    echo [OK] Ambiente virtual (venv) ja existe.
)

REM 4. Instalar dependências
echo [INFO] Instalando dependencias de requirements.txt...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo [OK] Dependencias instaladas com sucesso.

REM 5. Verificar config.yaml
if not exist config.yaml (
    if exist config.example.yaml (
        echo [AVISO] 'config.yaml' nao encontrado. Copiando de 'config.example.yaml'...
        copy config.example.yaml config.yaml >nul
        echo [OK] 'config.yaml' criado. Ajuste suas credenciais se necessario.
    )
) else (
    echo [OK] 'config.yaml' detectado.
)

echo.
echo ==========================================================
echo [SUCESSO] Ambiente configurado com sucesso!
echo Para rodar a automacao, execute: executar.bat
echo ==========================================================
pause
