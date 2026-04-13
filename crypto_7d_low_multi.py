import requests
import smtplib
import json
import os
from email.message import EmailMessage
from datetime import datetime, timezone

COINS = ["ETH-USD", "SOL-USD", "DOT-USD", "ATOM-USD", "POL-USD", "XTZ-USD"]
EMAIL_FROM = os.environ.get("EMAIL_FROM", "545318@gmail.com")
EMAIL_PASS  = os.environ.get("EMAIL_PASS", "ywrvyvhrydxvjfuc")
EMAIL_TO    = os.environ.get("EMAIL_TO", "545318@gmail.com")

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
    """Wipe state on Monday so every week starts with no known low."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    is_monday = datetime.now(timezone.utc).weekday() == 0

    if is_monday and state.get("_last_reset") != today:
        print("📅 Monday reset — starting fresh weekly lows", flush=True)
        return {"_last_reset": today}

    return state

# ── Coinbase price only — no candle endpoint ──────────────────────────────────
def get_price(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

def send_email(symbol, price, weekly_low):
    msg = EmailMessage()
    msg["Subject"] = f"🚨 WEEKLY LOW {symbol}"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    msg.set_content(
        f"{symbol} has set a new weekly low.\n\n"
        f"  Current price : {price:.4f}\n"
        f"  Weekly low    : {weekly_low:.4f}\n"
        f"  Time (UTC)    : {datetime.now(timezone.utc)}\n"
    )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)

# ── Main ──────────────────────────────────────────────────────────────────────
print("🚀 BOT STARTED", flush=True)

state = load_state()
state = reset_if_monday(state)

for coin in COINS:
    try:
        price = get_price(coin)
        coin_s = state.setdefault(coin, {"weekly_low": None})
        weekly_low = coin_s.get("weekly_low")

        print(f"{coin} | price={price:.4f} | weekly_low={weekly_low}", flush=True)

        if weekly_low is None or price < weekly_low:
            # New lowest price seen this week → alert and update
            print(f"🚨 NEW WEEKLY LOW {coin} | {price:.4f}", flush=True)
            send_email(coin, price, price)
            coin_s["weekly_low"] = price
        else:
            print(f"⏸  {coin} above weekly low ({weekly_low:.4f}), no alert", flush=True)

    except Exception as e:
        print(f"{coin} error: {e}", flush=True)

save_state(state)
print("✅ SCAN COMPLETE", flush=True)
