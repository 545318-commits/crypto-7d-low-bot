import requests
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ─────────────────────────────────────────────
# COINS
# ─────────────────────────────────────────────
COINS = [
    "ETH-USD",
    "SOL-USD",
    "DOT-USD",
    "ATOM-USD",
    "POL-USD",
    "XTZ-USD"
]

# ─────────────────────────────────────────────
# EMAIL CONFIG
# ─────────────────────────────────────────────
EMAIL_FROM = "545318@gmail.com"
EMAIL_PASS = "ywrvyvhrydxvjfuc"   # Gmail App Password
EMAIL_TO   = "545318@gmail.com"

# ─────────────────────────────────────────────
# STATE (prevents duplicate alerts on same low)
# ─────────────────────────────────────────────
last_low_event = {coin: None for coin in COINS}

# ─────────────────────────────────────────────
# COINBASE PRICE
# ─────────────────────────────────────────────
def get_price(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

# ─────────────────────────────────────────────
# TRUE 7-DAY LOW (DAILY CANDLES)
# ─────────────────────────────────────────────
def get_7d_low(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/candles"
    params = {"granularity": 86400}

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    lows = [c[1] for c in data]
    return min(lows)

# ─────────────────────────────────────────────
# EMAIL FUNCTION (FIXED)
# ─────────────────────────────────────────────
def send_email(symbol, price, low7):
    msg = EmailMessage()
    msg["Subject"] = f"🟢 7-DAY LOW EVENT {symbol}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    body = (
        f"{symbol} hit a NEW 7-day LOW event\n\n"
        f"Price: {price}\n"
        f"7-Day Low: {low7}\n"
        f"Time (UTC): {datetime.utcnow()}"
    )

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.sendmail(
            EMAIL_FROM,
            EMAIL_TO,
            msg.as_string()
        )

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
while True:
    for coin in COINS:
        try:
            price = get_price(coin)
            low7 = get_7d_low(coin)

            print(f"{coin} | Price: {price} | 7D Low: {low7}")

            # ONLY TRIGGER ON NEW LOWER LOW
            if last_low_event[coin] is None or low7 < last_low_event[coin]:

                print(f"🚨 NEW 7D LOW EVENT: {coin}")

                send_email(coin, price, low7)

                last_low_event[coin] = low7

        except Exception as e:
            print(f"{coin} error: {e}")

    time.sleep(60)