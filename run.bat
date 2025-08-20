@echo off
setlocal
chcp 65001 >nul
title Crypto Monitor (setup auto)
color 0A
pushd "%~dp0"

echo.
echo === Crypto Monitor - Setup automatico ===
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    set "PY=python"
  ) else (
    echo [ERRO] Python nao encontrado. Instale via Microsoft Store (procure por "Python") ou em https://www.python.org/downloads/
    pause
    goto :fim
  )
)

if not exist ".venv" (
  echo Criando ambiente virtual (.venv)...
  %PY% -m venv .venv
)

call ".venv\Scripts\activate.bat"

echo Instalando dependencias...
python -m pip install --upgrade pip >nul
python -m pip install requests tabulate

echo.
echo Iniciando monitor...
python monitor_crypto.py

deactivate >nul 2>nul

:fim
popd
endlocal
