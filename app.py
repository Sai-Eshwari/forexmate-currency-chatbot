from flask import Flask, request, jsonify
import requests
import re
import traceback

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running!"

API_KEY = "6bacccc6e083e41a93b2b10f"

# 🔥 CURRENCY MAPPING
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

# ✅ Normalize currency
def normalize(curr):
    curr = str(curr).lower().strip()

    if curr in mapping:
        return mapping[curr]

    for key in mapping:
        if key in curr:
            return mapping[key]

    return curr.upper()


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    try:
        if not req:
            return jsonify({"fulfillmentText": "Invalid request"})

        # =====================================
        # ✅ CASE 1: UI INPUT
        # =====================================
        if "query" in req:
            query = req["query"].lower()

            match = re.search(
                r'(\d+)?\s*([a-zA-Z₹$€¥£]+)\s*(to|in)\s*([a-zA-Z₹$€¥£]+)',
                query
            )

            if not match:
                return jsonify({
                    "fulfillmentText": "❌ Try: 1 USD to INR"
                })

            amount = match.group(1)
            amount = float(amount) if amount else 1

            from_currency = normalize(match.group(2))
            to_currency = normalize(match.group(4))

        # =====================================
        # ✅ CASE 2: DIALOGFLOW INPUT
        # =====================================
        else:
            params = req['queryResult']['parameters']

            amount = params.get('number', 1)
            if isinstance(amount, list):
                amount = amount[0]

            from_currency = params.get('unit-currency')
            to_currency = params.get('currency-name')

            if isinstance(from_currency, list):
                from_currency = from_currency[0]
            if isinstance(to_currency, list):
                to_currency = to_currency[0]

            if isinstance(from_currency, dict):
                amount = from_currency.get('amount', amount)
                from_currency = from_currency.get('currency')

            if not from_currency or not to_currency:
                return jsonify({
                    "fulfillmentText": "❌ Please specify both currencies"
                })

            from_currency = normalize(from_currency)
            to_currency = normalize(to_currency)

        # =====================================
        # ✅ API CALL
        # =====================================
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        response = requests.get(url).json()

        if response.get("result") != "success":
            raise Exception("API failed")

        rate = response['conversion_rates'].get(to_currency)

        if rate is None:
            raise Exception("Invalid currency")

        result = float(amount) * rate

        return jsonify({
            "fulfillmentText": f"{amount} {from_currency} = {round(result, 4)} {to_currency}"
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "fulfillmentText": "⚠️ Something went wrong. Try again."
        })


if __name__ == "__main__":
    app.run(debug=True)