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
    # USD
    "usd": "USD", "dollar": "USD", "dollars": "USD", "$": "USD", "us dollar": "USD",

    # INR
    "inr": "INR", "rupee": "INR", "rupees": "INR", "₹": "INR", "indian rupee": "INR",

    # JPY
    "jpy": "JPY", "yen": "JPY", "¥": "JPY", "japanese yen": "JPY",

    # EUR
    "eur": "EUR", "euro": "EUR", "euros": "EUR", "€": "EUR",

    # GBP
    "gbp": "GBP", "pound": "GBP", "pounds": "GBP", "£": "GBP", "british pound": "GBP",

    # CNY
    "cny": "CNY", "yuan": "CNY", "renminbi": "CNY", "元": "CNY",

    # CAD
    "cad": "CAD", "canadian dollar": "CAD",

    # AUD
    "aud": "AUD", "australian dollar": "AUD",

    # SGD
    "sgd": "SGD", "singapore dollar": "SGD",

    # AED
    "aed": "AED", "dirham": "AED",

    # CHF
    "chf": "CHF", "swiss franc": "CHF",

    # KRW
    "krw": "KRW", "won": "KRW", "korean won": "KRW",

    # RUB
    "rub": "RUB", "ruble": "RUB", "rouble": "RUB",

    # TRY
    "try": "TRY", "lira": "TRY", "turkish lira": "TRY",

    # ZAR
    "zar": "ZAR", "rand": "ZAR", "south african rand": "ZAR"
}


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    try:
        params = req['queryResult']['parameters']

        amount = 1

        from_currency = params.get('unit-currency')
        to_currency = params.get('currency-name')

        # Handle structured input
        if isinstance(from_currency, dict):
            amount = from_currency.get('amount', 1)
            from_currency = from_currency.get('currency')

        # 🔥 NORMALIZATION (MOST IMPORTANT)
        from_currency = str(from_currency).lower()
        to_currency = str(to_currency).lower()

        from_currency = mapping.get(from_currency, from_currency.upper())
        to_currency = mapping.get(to_currency, to_currency.upper())

        # API call
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        response = requests.get(url).json()

        if response["result"] != "success":
            raise Exception("API failed")

        rate = response['conversion_rates'][to_currency]
        result = amount * rate

        return jsonify({
            "fulfillmentText": f"{amount} {from_currency} = {round(result, 2)} {to_currency}"
        })

    except Exception as e:
        return jsonify({
            "fulfillmentText": "Sorry 😔 I couldn't process that. Try like: 1 USD to INR"
        })


if __name__ == "__main__":
    app.run(debug=True)