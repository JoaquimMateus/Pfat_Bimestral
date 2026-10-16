@echo off
REM =====================================================================
REM Atalho para executar a automação PFAT Bimestral (Windows)
REM =====================================================================

if not exist venv (
    echo [AVISO] Ambiente virtual nao encontrado. Rodando setup inicial...
    call setup_ambiente.bat
)

call venv\Scripts\activate.bat
python main_dado.py %*
pause
