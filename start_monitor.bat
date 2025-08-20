@echo off
REM Ativa a venv e roda com variáveis fixas (edite aqui se quiser)
call .venv\Scripts\activate

set MONITOR_PAIRS=BTCUSDT,ETHUSDT,SOLUSDT
set INTERVALO_SEG=5
set SAVE_CSV=1

python monitor_crypto.py
echo.
echo (Pressione qualquer tecla para sair)
pause >nul
