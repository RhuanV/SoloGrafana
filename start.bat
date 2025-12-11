@echo off
TITLE CUBESAT GROUND STATION - LAUNCHER
COLOR 0B

:: 1. Garante que o script rode na pasta correta (mesmo se executado como Admin)
cd /d "%~dp0"

echo =================================================
echo   INICIANDO SISTEMA DE SOLO (SOLO GRAFANA)
echo =================================================

:: 2. Verifica se a pasta venv existe
if not exist "venv\Scripts\activate.bat" (
    echo [ERRO] Ambiente virtual 'venv' nao encontrado!
    echo Por favor, rode: python -m venv venv
    pause
    exit
)

:: 3. Ativa o ambiente virtual
call venv\Scripts\activate

:: 4. Passa a bola para o Python (que vai abrir Docker e Grafana)
python SoloV1.py

:: 5. Se o Python fechar por erro, segura a tela para você ler
if %errorlevel% neq 0 (
    echo.
    echo [ERRO CRITICO] O script Python encerrou com erro.
    pause
)