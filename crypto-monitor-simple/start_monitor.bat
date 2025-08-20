@echo off
chcp 65001 >nul
title Crypto Monitor (terminal)
pushd "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
  py monitor_crypto.py
  goto :fim
)
where python >nul 2>nul
if %errorlevel%==0 (
  python monitor_crypto.py
  goto :fim
)

echo [ERRO] Python nao encontrado. Instale pelo Microsoft Store (py) ou python.org.
pause

:fim
popd
