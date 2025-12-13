@echo off
TITLE ESTACAO DE SOLO - CUBESAT V3
COLOR 0A

echo ==================================================
echo      INICIANDO SISTEMAS DE SOLO - CUBESAT
echo ==================================================
echo.

:: --- 1. VERIFICAÇÃO DO DOCKER ---
echo [1/5] Verificando Docker Engine...
docker info >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] O Docker nao esta rodando!
    echo Por favor, abra o Docker Desktop e tente novamente.
    pause
    exit
)

:: --- 2. INICIAR SERVIÇOS (InfluxDB + Grafana) ---
echo [2/5] Subindo conteineres de Telemetria...
docker-compose up -d
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao subir Docker Compose.
    pause
    exit
)

:: Aguarda 5 segundos para o banco de dados acordar
echo ... Aguardando inicializacao dos servicos ...
timeout /t 2 /nobreak >nul

:: --- 3. HOSPEDAR ARQUIVOS 3D (Servidor HTTP em Background) ---
echo [3/5] Iniciando servidor de Assets 3D (Porta 8000)...
:: O comando 'start /min' abre uma janela minimizada para nao atrapalhar
start /min "Servidor 3D (Nao Feche)" python -m http.server 8000 --bind 127.0.0.1

:: --- 4. ABRIR DASHBOARD (Modo Kiosk) ---
echo [4/5] Abrindo Mission Control...
:: Substitua a URL abaixo pelo link exato do seu dashboard importado
:: O parametro '&kiosk' força a tela cheia
for /f "delims=" %%i in ('powershell -Command "(Get-Content config/config.json | ConvertFrom-Json).dashboard.url"') do set DASHBOARD_URL=%%i
:: set DASHBOARD_URL="http://localhost:3000/d/cubesat_v3_blue/mission-control-final-v3-blue?orgId=1&refresh=1s&kiosk"
for /f "delims=" %%i in ('powershell -Command "(Get-Content config/config.json | ConvertFrom-Json).mission.name"') do set MISSION_NAME=%%i
set "FULL_URL=%DASHBOARD_URL%&var-missao=%MISSION_NAME%"
start "" "%FULL_URL%"

:: --- 5. RODAR CÓDIGO PRINCIPAL (Python) ---
echo [5/5] Executando Station Core (main.py)...
echo.
echo --------------------------------------------------
echo   SISTEMA PRONTO. PRESSIONE CTRL+C PARA SAIR.
echo --------------------------------------------------
echo.

:: Ativa o VENV (ajuste o caminho se sua pasta chamar '.venv' ou outra coisa)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo [AVISO] VENV nao encontrado. Tentando rodar com Python global...
)

:: Executa o código principal
python main.py

:: --- LIMPEZA AO FECHAR ---
:: Quando você fechar o Python, o script chega aqui
echo.
echo Encerrando servidor 3D...
taskkill /F /FI "WINDOWTITLE eq Servidor 3D (Nao Feche)" >nul 2>&1
echo Encerrando Docker
docker-compose stop
pause