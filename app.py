from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Server is running!"

API_KEY = "6bacccc6e083e41a93b2b10f"


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()

    try:
        params = req['queryResult']['parameters']

        amount = params['unit-currency']['amount']
        from_currency = params['unit-currency']['currency']
        to_currency = params['currency-name']

        url = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/{from_currency}"
        response = requests.get(url).json()

        rate = response['conversion_rates'][to_currency]
        result = amount * rate

        return jsonify({
            "fulfillmentText": f"{amount} {from_currency} = {round(result, 2)} {to_currency}"
        })

    except:
        return jsonify({
            "fulfillmentText": "Something went wrong"
        })


if __name__ == "__main__":
    app.run(debug=True)
