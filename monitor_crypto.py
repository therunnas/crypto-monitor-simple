#!/usr/bin/env python3
"""
Crypto Monitor (Terminal) - simples e privado
Autor: você (com uma ajudinha do ChatGPT)

Funciona no terminal e consulta preços/variação 24h direto da API pública da Binance (sem chave).
Atualiza em loop com intervalo configurável.
Dependências: requests, tabulate

Instalação (Windows / macOS / Linux):
  pip install requests tabulate

Uso:
  python monitor_crypto.py
  (Opcional) Edite a lista PARES e ALERTAS abaixo.

Saída: tabela com Preço USDT, Var% 24h, Máx/Min 24h, Volume e Alertas simples.
"""

import os
import time
from datetime import datetime, timezone
from typing import List, Dict

import requests
from tabulate import tabulate

# ===================== Config =====================
# Pares que você quer monitorar (sempre em USDT)
PARES: List[str] = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "ADAUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "LINKUSDT",
    "DOTUSDT",
]

# Intervalo entre atualizações (segundos)
INTERVALO_SEG = 10

# Alertas: defina por par. Exemplos:
#   - "baixo": alerta se preço cair para <= valor
#   - "alto": alerta se preço subir para >= valor
#   - "var_pct": alerta se variação absoluta em 24h for >= valor (ex.: 5 -> ±5%)
ALERTAS: Dict[str, Dict[str, float]] = {
    "BTCUSDT": {"alto": 120000.0, "var_pct": 3.0},
    "ETHUSDT": {"alto": 4500.0, "var_pct": 3.0},
    # Adicione mais se quiser
}

# Formatação de casas decimais por ativo (opcional)
CASAS_DECIMAIS: Dict[str, int] = {
    "BTCUSDT": 2,
    "ETHUSDT": 2,
    "SOLUSDT": 2,
    "ADAUSDT": 4,
    "XRPUSDT": 4,
    "DOGEUSDT": 5,
    "LINKUSDT": 2,
    "DOTUSDT": 2,
}

# ==================================================

BINANCE_24H_URL = "https://api.binance.com/api/v3/ticker/24hr"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CryptoMonitor/1.0"})


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def formata_numero(valor: float, casas: int = 2) -> str:
    try:
        return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor)


def fetch_24h_tickers():
    """Busca todos os tickers 24h e retorna a lista completa."""
    resp = SESSION.get(BINANCE_24H_URL, timeout=15)
    resp.raise_for_status()
    return resp.json()


def extrai_ticker(dados, symbol: str):
    """Localiza um symbol na lista de tickers e retorna o dict correspondente ou {}."""
    for d in dados:
        if d.get("symbol") == symbol:
            return d
    return {}


def checa_alertas(symbol: str, preco: float, var_pct: float):
    """Retorna lista de mensagens de alertas disparados para um par."""
    msgs = []
    cfg = ALERTAS.get(symbol, {})
    if not cfg:
        return msgs

    alvo_baixo = cfg.get("baixo")
    alvo_alto = cfg.get("alto")
    alvo_var = cfg.get("var_pct")

    if alvo_baixo is not None and preco <= alvo_baixo:
        msgs.append(f"{symbol}: preço tocou alvo BAIXO <= {alvo_baixo}")
    if alvo_alto is not None and preco >= alvo_alto:
        msgs.append(f"{symbol}: preço tocou alvo ALTO >= {alvo_alto}")
    if alvo_var is not None and abs(var_pct) >= alvo_var:
        msgs.append(f"{symbol}: variação 24h atingiu ±{alvo_var}% (atual {var_pct:.2f}%)")

    return msgs


def main_loop():
    ultimos_alertas = {}  # evita repetir alerta igual em cada ciclo

    while True:
        try:
            dados = fetch_24h_tickers()
        except Exception as e:
            clear_screen()
            print("[ERRO] Falha ao consultar API da Binance:", e)
            time.sleep(INTERVALO_SEG)
            continue

        linhas = []
        alertas_disparados = []

        for symbol in PARES:
            t = extrai_ticker(dados, symbol)
            if not t:
                linhas.append([symbol, "-", "-", "-", "-", "-"])
                continue

            # Extração segura
            last = float(t.get("lastPrice", 0.0))
            var_pct = float(t.get("priceChangePercent", 0.0))
            high = float(t.get("highPrice", 0.0))
            low = float(t.get("lowPrice", 0.0))
            vol = float(t.get("quoteVolume", 0.0))  # volume em USDT (quote)

            casas = CASAS_DECIMAIS.get(symbol, 4)
            linhas.append([
                symbol,
                formata_numero(last, casas),
                f"{var_pct:+.2f}%",
                formata_numero(high, casas),
                formata_numero(low, casas),
                formata_numero(vol, 0),
            ])

            # Alertas
            for msg in checa_alertas(symbol, last, var_pct):
                # Evitar repetir a mesma mensagem a cada ciclo
                if ultimos_alertas.get(symbol) != msg:
                    alertas_disparados.append(msg)
                    ultimos_alertas[symbol] = msg

        clear_screen()
        agora = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        print(f"CRYPTO MONITOR — {agora}\n")

        headers = ["Par", "Preço (USDT)", "Var 24h", "Máx 24h", "Mín 24h", "Vol (USDT)"]
        print(tabulate(linhas, headers=headers, tablefmt="fancy_grid", floatfmt=".2f"))
        print(f"\nAtualiza em {INTERVALO_SEG}s — Fonte: Binance 24h Ticker\n")

        if alertas_disparados:
            print("Alertas:")
            for m in alertas_disparados:
                print(" -", m)
            print()

        time.sleep(INTERVALO_SEG)


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nSaindo...")
