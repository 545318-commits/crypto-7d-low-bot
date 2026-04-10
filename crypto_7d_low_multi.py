import requests
import smtplib
import json
import os
from email.message import EmailMessage
from datetime import datetime, timezone

COINS = ["ETH-USD", "SOL-USD", "DOT-USD", "ATOM-USD", "POL-USD", "XTZ-USD"]
EMAIL_FROM = "545318@gmail.com"
EMAIL_PASS  = "ywrvyvhrydxvjfuc"
EMAIL_TO    = "545318@gmail.com"

STATE_FILE = "state.json"

# ── State helpers ─────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def reset_if_monday(state):
    """Wipe state on Monday (weekday 0) so every week starts clean."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    is_monday = datetime.now(timezone.utc).weekday() == 0  # 0 = Monday

    if is_monday and state.get("_last_reset") != today:
        print("📅 Monday reset — clearing all alerted lows", flush=True)
        return {"_last_reset": today}   # blank slate, keep only the reset marker

    return state

# ── Coinbase helpers ──────────────────────────────────────────────────────────
def get_price(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

def get_7d_low(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    r = requests.get(url, params={"granularity": 86400}, timeout=10)
    data = r.json()
    return min(c[1] for c in data)

def send_email(symbol, price, low7):
    msg = EmailMessage()
    msg["Subject"] = f"🚨 7D LOW {symbol}"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.set_content(
        f"{symbol} has broken its 7-day low.\n\n"
        f"  Current price : {price:.4f}\n"
        f"  7-day low     : {low7:.4f}\n"
        f"  Time (UTC)    : {datetime.now(timezone.utc)}\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)

# ── Main ──────────────────────────────────────────────────────────────────────
print("🚀 BOT STARTED", flush=True)

state = load_state()
state = reset_if_monday(state)   # ← resets once per Monday, safe to call every run

for coin in COINS:
    try:
        price = get_price(coin)
        low7  = get_7d_low(coin)

        print(f"{coin} | price={price:.4f} | 7d_low={low7:.4f}", flush=True)

        if price <= low7:
            last_alerted = state.get(coin)

            if last_alerted != low7:
                print(f"🚨 ALERT {coin} — new 7d low={low7:.4f}", flush=True)
                send_email(coin, price, low7)
                state[coin] = low7
            else:
                print(f"⏸  {coin} same 7d low ({low7:.4f}), skipping", flush=True)
        else:
            if coin in state:
                print(f"✅ {coin} recovered, resetting", flush=True)
                del state[coin]

    except Exception as e:
        print(f"{coin} error: {e}", flush=True)

save_state(state)
print("✅ SCAN COMPLETE", flush=True)
