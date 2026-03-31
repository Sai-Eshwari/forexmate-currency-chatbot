from flask import Flask, request, jsonify, render_template
import requests
import re
import traceback

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

API_KEY = "6bacccc6e083e41a93b2b10f"

mapping = {
    "usd": "USD", "dollar": "USD", "dollars": "USD", "$": "USD",
    "inr": "INR", "rupee": "INR", "rupees": "INR", "₹": "INR",
    "jpy": "JPY", "yen": "JPY", "¥": "JPY",
    "eur": "EUR", "euro": "EUR", "€": "EUR",
    "gbp": "GBP", "pound": "GBP", "£": "GBP",
    "cny": "CNY", "yuan": "CNY",
    "cad": "CAD", "aud": "AUD", "sgd": "SGD",
    "aed": "AED", "chf": "CHF", "krw": "KRW",
}

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
    try:
        req = request.get_json(force=True)

        # ================= UI MODE =================
        if "query" in req:
            query = req["query"].lower().strip()

            import re
            match = re.search(r'(\d+(?:\.\d+)?)\s*([a-zA-Z₹$€¥£]+)\s*(to|in)\s*([a-zA-Z₹$€¥£]+)', query)

            if not match:
                return jsonify({
                    "fulfillmentText": "❌ Try: 1 USD to INR"
                })

            amount = float(match.group(1))
            from_currency = normalize(match.group(2))
            to_currency = normalize(match.group(4))

        # ================= DIALOGFLOW MODE =================
        else:
            params = req.get('queryResult', {}).get('parameters', {})

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
                    "fulfillmentText": "⚠️ Missing currency. Try again."
                })

            from_currency = normalize(from_currency)
            to_currency = normalize(to_currency)

        # ================= API =================
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        response = requests.get(url).json()

        if response.get("result") != "success":
            return jsonify({
                "fulfillmentText": "⚠️ API error. Try again later."
            })

        rate = response['conversion_rates'].get(to_currency)

        if not rate:
            return jsonify({
                "fulfillmentText": "⚠️ Invalid currency"
            })

        result = float(amount) * rate

        return jsonify({
            "fulfillmentText": f"{amount} {from_currency} = {round(result, 4)} {to_currency}"
        })

    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()

        return jsonify({
            "fulfillmentText": "⚠️ Something went wrong. Try again."
        })


if __name__ == "__main__":
    app.run(debug=True)