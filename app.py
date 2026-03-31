from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Home route (for testing)
@app.route("/")
def home():
    return "Server is running!"

# Your API Key
API_KEY = "6bacccc6e083e41a93b2b10f"

# Webhook route for Dialogflow
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    try:
        params = req['queryResult']['parameters']

        amount = 1  # default if user doesn't specify

        from_currency = params.get('unit-currency')
        to_currency = params.get('currency-name')

        # If Dialogflow sends structured input
        if isinstance(from_currency, dict):
            amount = from_currency.get('amount', 1)
            from_currency = from_currency.get('currency')

        # Convert to uppercase (important for API)
        from_currency = str(from_currency).upper()
        to_currency = str(to_currency).upper()

        # API call
        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        response = requests.get(url).json()

        # Check API response
        if response.get("result") != "success":
            return jsonify({
                "fulfillmentText": "API error. Please try again later."
            })

        rate = response['conversion_rates'].get(to_currency)

        if rate is None:
            return jsonify({
                "fulfillmentText": "Currency not supported."
            })

        result = amount * rate

        return jsonify({
            "fulfillmentText": f"{amount} {from_currency} = {round(result, 2)} {to_currency}"
        })

    except Exception as e:
        print("Error:", e)  # useful for Render logs
        return jsonify({
            "fulfillmentText": "Something went wrong. Try again."
        })


if __name__ == "__main__":
    app.run(debug=True)