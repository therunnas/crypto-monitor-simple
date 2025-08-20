#!/usr/bin/env bash
# Exemplo: pares customizados, intervalo 5s, salvar CSV
export MONITOR_PAIRS="BTCUSDT,ETHUSDT,SOLUSDT"
export INTERVALO_SEG=5
export SAVE_CSV=1
python monitor_crypto.py
