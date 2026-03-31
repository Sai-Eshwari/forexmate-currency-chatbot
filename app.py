from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return "Server is running!"

API_KEY = "6bacccc6e083e41a93b2b10f"

# 🔥 UNIVERSAL CURRENCY MAPPING
mapping = {
    "usd": "USD", "dollar": "USD", "dollars": "USD", "$": "USD", "us dollar": "USD",
    "inr": "INR", "rupee": "INR", "rupees": "INR", "₹": "INR", "indian rupee": "INR",
    "jpy": "JPY", "yen": "JPY", "¥": "JPY", "japanese yen": "JPY",
    "eur": "EUR", "euro": "EUR", "euros": "EUR", "€": "EUR",
    "gbp": "GBP", "pound": "GBP", "pounds": "GBP", "£": "GBP", "british pound": "GBP",
    "cny": "CNY", "yuan": "CNY", "renminbi": "CNY", "元": "CNY",
    "cad": "CAD", "canadian dollar": "CAD",
    "aud": "AUD", "australian dollar": "AUD",
    "sgd": "SGD", "singapore dollar": "SGD",
    "aed": "AED", "dirham": "AED",
    "chf": "CHF", "swiss franc": "CHF",
    "krw": "KRW", "won": "KRW", "korean won": "KRW",
    "rub": "RUB", "ruble": "RUB", "rouble": "RUB",
    "try": "TRY", "lira": "TRY", "turkish lira": "TRY",
    "zar": "ZAR", "rand": "ZAR", "south african rand": "ZAR"
}

# ✅ CORRECT NORMALIZE FUNCTION (ONLY ONE)
def normalize(curr):
    curr = str(curr).lower().strip()

    # exact match
    if curr in mapping:
        return mapping[curr]

    # match inside phrase (like "us dollars")
    for key in mapping:
        if key in curr:
            return mapping[key]

    return curr.upper()


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    try:
        params = req['queryResult']['parameters']

        # ✅ amount handling
        amount = params.get('number', 1) or 1

        from_currency = params.get('unit-currency')
        to_currency = params.get('currency-name')

        # ✅ handle Dialogflow structured input
        if isinstance(from_currency, dict):
            amount = from_currency.get('amount', amount)
            from_currency = from_currency.get('currency')

        # ❌ safety check
        if not from_currency or not to_currency:
            raise Exception("Missing currency")

        # ✅ normalize properly
        from_currency = normalize(from_currency)
        to_currency = normalize(to_currency)

        # 🔍 DEBUG (you can remove later)
        print("FROM:", from_currency, "TO:", to_currency, "AMOUNT:", amount)

        # ✅ API call
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        response = requests.get(url).json()

        if response.get("result") != "success":
            raise Exception("API failed")

        rate = response['conversion_rates'].get(to_currency)

        if not rate:
            raise Exception("Invalid currency")

        result = amount * rate

        return jsonify({
            "fulfillmentText": f"{amount} {from_currency} = {round(result, 2)} {to_currency}"
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "fulfillmentText": "⚠️ Try like: 1 USD to INR or 100 rupees to dollars"
        })


if __name__ == "__main__":
    app.run(debug=True)