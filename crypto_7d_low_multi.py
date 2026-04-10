import requests
import time
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

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
EMAIL_PASS = "ywrvyvhrydxvjfuc"
EMAIL_TO   = "545318@gmail.com"

# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
last_low = {coin: None for coin in COINS}
price_history = {coin: [] for coin in COINS}

# ─────────────────────────────────────────────
# PRICE FETCH
# ─────────────────────────────────────────────
def get_price(symbol):
    url = f"https://api.exchange.coinbase.com/products/{symbol}/ticker"
    r = requests.get(url, timeout=10)
    return float(r.json()["price"])

# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
def send_email(symbol, price, low7):
    msg = EmailMessage()
    msg["Subject"] = f"7-DAY LOW ALERT {symbol}"
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    msg.set_content(
        f"{symbol} hit a new 7-day low\n\n"
        f"Price: {price}\n"
        f"7-Day Low: {low7}\n"
        f"Time: {datetime.utcnow()}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASS)
        smtp.send_message(msg)

# ─────────────────────────────────────────────
# MAIN LOOP
# ─────────────────────────────────────────────
def run():
    print("🚀 BOT STARTED")

    while True:
        try:
            for coin in COINS:
                price = get_price(coin)

                # store price history (keep last 7 days worth of samples)
                price_history[coin].append((datetime.utcnow(), price))

                cutoff = datetime.utcnow() - timedelta(days=7)

                # remove old data
                price_history[coin] = [
                    x for x in price_history[coin] if x[0] >= cutoff
                ]

                # compute rolling 7-day low
                low7 = min(x[1] for x in price_history[coin])

                print(f"{coin} | Price: {price} | 7D Low: {low7}")

                # trigger ONLY on new break of 7D low
                if last_low[coin] is None or price < last_low[coin]:

                    # only alert if meaningful break
                    if price <= low7:
                        print(f"🚨 NEW 7D LOW: {coin}")
                        send_email(coin, price, low7)
                        last_low[coin] = price

            time.sleep(60)

        except Exception as e:
            print("ERROR:", e)
            time.sleep(10)

# ─────────────────────────────────────────────
if __name__ == "__main__":
    run()
