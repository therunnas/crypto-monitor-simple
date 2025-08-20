Crypto Monitor (Terminal) — Pacote simples
Data: 2025-08-20 01:30

Arquivos:
- monitor_crypto.py  -> script principal (API pública Binance)
- start_monitor.bat  -> executa usando Python do sistema (se já tiver Python)
- run.bat            -> cria venv, instala dependências e executa automaticamente

Como usar (recomendado):
1) Extraia o ZIP em qualquer pasta (ex.: C:\CryptoMonitor).
2) Dê 2 cliques em "run.bat". Na primeira vez ele cria a pasta ".venv" e instala:
   - requests
   - tabulate
3) A janela vai abrir e começar a atualizar a cada 10s.
4) Para parar, feche a janela ou pressione Ctrl+C.

Configurações rápidas no monitor_crypto.py:
- PARES: edite a lista de ativos (sempre em USDT, ex.: BTCUSDT, ETHUSDT).
- INTERVALO_SEG: intervalo de atualização (segundos).
- ALERTAS: defina pontos "baixo"/"alto" e "var_pct" por ativo.
- CASAS_DECIMAIS: ajuste de casas por par.

Dúvidas? É só falar com o ChatGPT :)
