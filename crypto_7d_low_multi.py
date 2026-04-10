import requests
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime

COINS = ["ETH-USD","SOL-USD","DOT-USD","ATOM-USD","POL-USD","XTZ-USD"]

EMAIL_FROM = "545318@gmail.com"
EMAIL_PASS = "ywrvyvhrydxvjfuc"
EMAIL_TO = "545318@gmail.com"

last_low = {coin: None for coin in COINS}

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
    msg["Subject"] = f"7D LOW {symbol}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg.set_content(
        f"{symbol} 7D LOW\nPrice: {price}\nLow: {low7}\nTime: {datetime.utcnow()}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)

print("🚀 BOT STARTED", flush=True)

while True:
    for coin in COINS:
        try:
            price = get_price(coin)
            low7 = get_7d_low(coin)

            print(f"{coin} | {price} | {low7}", flush=True)

            if last_low[coin] is None or price < last_low[coin]:
                print(f"🚨 NEW LOW {coin}", flush=True)
                send_email(coin, price, low7)
                last_low[coin] = price

        except Exception as e:
            print(f"{coin} error: {e}", flush=True)

    time.sleep(60)
