# 🚀 Crypto Monitor Simple

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Um monitor simples e privado de criptomoedas no terminal, usando a **API pública da Binance**.  
Feito em Python com suporte a execução direta no Windows via `.bat`.

---
![CI](https://github.com/therunnas/crypto-monitor-simple/actions/workflows/ci.yaml/badge.svg)


## 📸 Preview

> Exemplo ilustrativo de saída (valores fictícios):

| Par     | Preço (USDT) | Var 24h | Máx 24h | Mín 24h | Vol (USDT) |
|:--------|-------------:|--------:|--------:|--------:|-----------:|
| BTCUSDT | 113.227,95   | +0,27%  | 115.000 | 111.500 | 2.453.000  |
| ETHUSDT | 4.100,78     | +0,57%  | 4.250   | 3.950   |   856.000  |

### Exemplo real (terminal rodando):
<p align="center">
  <img src="docs/cripto-visual.jpg" width="600">
</p>

---

## ⚙️ Instalação e uso

### Requisitos
- [Python 3.9+](https://www.python.org/downloads/)
- Dependências:
  ```bash
  pip install requests tabulate

```bash
python -m venv .venv && source .venv/Scripts/activate && pip install -r requirements.txt


*(no Windows CMD use `.\.venv\Scripts\activate`)*

---

## 3) Script de exemplo com variáveis (rodar com ENV)
Ajuda quem quer customizar sem editar o .py.

**Git Bash:**
```bash
cd "/c/Users/vinicius.macaneiro/Documents/GitHub/crypto-monitor-simple"
cat > examples.sh << 'EOF'
# Exemplo: pares customizados, intervalo 5s, salvar CSV
export MONITOR_PAIRS="BTCUSDT,SOLUSDT,PEPEUSDT"
export INTERVALO_SEG=5
export SAVE_CSV=1
python monitor_crypto.py
EOF
git add examples.sh
git commit -m "Add examples.sh with ENV usage"
git push
