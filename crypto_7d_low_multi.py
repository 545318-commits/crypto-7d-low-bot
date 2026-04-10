import requests
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

print("🚀 BOT STARTED")

COINS = [
    "ETH-USD",
    "SOL-USD",
    "DOT-USD",
    "ATOM-USD",
    "POL-USD",
    "XTZ-USD"
]

EMAIL_FROM = "545318@gmail.com"
EMAIL_PASS = "ywrvyvhrydxvjfuc"
EMAIL_TO   = "545318@gmail.com"

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
week_low = {coin: None for coin in COINS}
week_id  = None


# ─────────────────────────────────────────────
# WEEK RESET (MONDAY LOGIC)
# ─────────────────────────────────────────────
def get_week_id():
    now = datetime.now(timezone.utc)
    return now.isocalendar().week


# ─────────────────────────────────────────────
# PRICE
# ─────────────────────────────────────────────
def get_price(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return float(r.json()["price"])


# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
def send_email(symbol, price, low):
    msg = EmailMessage()
    msg["Subject"] = f"🟢 7D LOW UPDATE {symbol}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg.set_content(
        f"{symbol} NEW WEEKLY LOW UPDATE\n\n"
        f"Price: {price}\n"
        f"Current Week Low: {low}\n"
        f"Time (UTC): {datetime.utcnow()}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)


# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
while True:
    try:
        current_week = get_week_id()

        # RESET WEEKLY STATE (MONDAY RESET LOGIC)
        global week_id
        if week_id is None or current_week != week_id:
            print("🔄 NEW WEEK RESET")
            week_id = current_week
            week_low = {coin: None for coin in COINS}

        for coin in COINS:
            price = get_price(coin)

            print(f"{coin} | Price: {price}")

            # FIRST LOW
            if week_low[coin] is None:
                week_low[coin] = price
                continue

            # NEW LOWER LOW
            if price < week_low[coin]:
                print(f"🚨 NEW WEEKLY LOW: {coin}")

                week_low[coin] = price
                send_email(coin, price, price)

        time.sleep(60)

    except Exception as e:
        print("ERROR:", e)
        time.sleep(10)
