#!/usr/bin/env python3
"""
Crypto Monitor (Terminal) - simples e privado (v2)
Melhorias: env para pares/intervalo, cooldown de alertas, beep, backoff, cores ANSI, log CSV opcional.

Dependências: requests, tabulate
pip install requests tabulate
"""

import os
import time
import csv
from datetime import datetime, timezone
from typing import List, Dict

import requests
from tabulate import tabulate

# ===================== Config =====================
PARES_ENV = os.getenv("MONITOR_PAIRS", "").strip()
if PARES_ENV:
    PARES: List[str] = [s.strip().upper() for s in PARES_ENV.split(",") if s.strip()]
else:
    PARES: List[str] = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT",
        "XRPUSDT", "DOGEUSDT", "LINKUSDT", "DOTUSDT",
    ]

INTERVALO_SEG = int(os.getenv("INTERVALO_SEG", "10"))

ALERTAS: Dict[str, Dict[str, float]] = {
    "BTCUSDT": {"alto": 120000.0, "var_pct": 3.0},
    "ETHUSDT": {"alto": 4500.0, "var_pct": 3.0},
}

ALERT_COOLDOWN_SEC = 300

CASAS_DECIMAIS: Dict[str, int] = {
    "BTCUSDT": 2, "ETHUSDT": 2, "SOLUSDT": 2, "ADAUSDT": 4,
    "XRPUSDT": 4, "DOGEUSDT": 5, "LINKUSDT": 2, "DOTUSDT": 2,
}

SAVE_CSV = os.getenv("SAVE_CSV", "0") == "1"
CSV_PATH = os.getenv("CSV_PATH", "monitor_log.csv")
# ==================================================

BINANCE_24H_URL = "https://api.binance.com/api/v3/ticker/24hr"
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CryptoMonitor/1.1"})

ANSI = {
    "reset": "\033[0m",
    "green": "\033[92m",
    "red": "\033[91m",
    "yellow": "\033[93m",
}

def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")

def formata_numero(valor: float, casas: int = 2) -> str:
    try:
        return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(valor)

def color_pct(p: float) -> str:
    s = f"{p:+.2f}%"
    if p > 0.0:
        return f"{ANSI['green']}{s}{ANSI['reset']}"
    if p < 0.0:
        return f"{ANSI['red']}{s}{ANSI['reset']}"
    return f"{ANSI['yellow']}{s}{ANSI['reset']}"

def beep() -> None:
    try:
        if os.name == "nt":
            import winsound
            winsound.Beep(1200, 180)
        else:
            print("\a", end="", flush=True)
    except Exception:
        pass

def fetch_24h_tickers(max_retries: int = 5, base_wait: float = 1.0):
    wait = base_wait
    for tent in range(max_retries):
        try:
            resp = SESSION.get(BINANCE_24H_URL, timeout=15)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            if tent == max_retries - 1:
                raise
            time.sleep(wait)
            wait = min(wait * 2, 15)

def extrai_ticker(dados, symbol: str):
    for d in dados:
        if d.get("symbol") == symbol:
            return d
    return {}

def checa_alertas(symbol: str, preco: float, var_pct: float) -> List[str]:
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

def maybe_write_csv(rows: List[List[str]]) -> None:
    if not SAVE_CSV:
        return
    newfile = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        if newfile:
            w.writerow(["timestamp", "par", "preco_usdt", "var_24h_pct", "max_24h", "min_24h", "vol_usdt"])
        ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        for par, preco, var, maxp, minp, vol in rows:
            var_plain = var.replace(ANSI["green"], "").replace(ANSI["red"], "").replace(ANSI["yellow"], "").replace(ANSI["reset"], "")
            w.writerow([ts, par, preco, var_plain, maxp, minp, vol])

def main_loop():
    ultimo_alerta_por_msg: Dict[str, float] = {}

    while True:
        try:
            dados = fetch_24h_tickers()
        except Exception as e:
            clear_screen()
            print("[ERRO] Falha ao consultar API da Binance:", e)
            time.sleep(INTERVALO_SEG)
            continue

        linhas = []
        alertas_disparados: List[str] = []

        for symbol in PARES:
            t = extrai_ticker(dados, symbol)
            if not t:
                linhas.append([symbol, "-", "-", "-", "-", "-"])
                continue

            last = float(t.get("lastPrice", 0.0))
            var_pct = float(t.get("priceChangePercent", 0.0))
            high = float(t.get("highPrice", 0.0))
            low = float(t.get("lowPrice", 0.0))
            vol = float(t.get("quoteVolume", 0.0))

            casas = CASAS_DECIMAIS.get(symbol, 4)
            linhas.append([
                symbol,
                formata_numero(last, casas),
                color_pct(var_pct),
                formata_numero(high, casas),
                formata_numero(low, casas),
                formata_numero(vol, 0),
            ])

            for msg in checa_alertas(symbol, last, var_pct):
                now = time.time()
                last_ts = ultimo_alerta_por_msg.get(msg, 0.0)
                if now - last_ts >= ALERT_COOLDOWN_SEC:
                    alertas_disparados.append(msg)
                    ultimo_alerta_por_msg[msg] = now

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
            beep()
            print()

        try:
            maybe_write_csv(linhas)
        except Exception:
            pass

        time.sleep(INTERVALO_SEG)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nSaindo...")
