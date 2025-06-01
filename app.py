from flask import Flask, request, jsonify
import os

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "orden_ordely_verification_token")

@app.route("/", methods=["GET"])
def home():
    return "OrderlyBot está corriendo 🚀", 200

@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Token de verificación inválido", 403

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("📩 Mensaje recibido:", data)

    # Aquí se llamará al flujo conversacional más adelante
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(debug=True)
