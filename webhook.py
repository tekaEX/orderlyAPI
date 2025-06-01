from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["GET"])
def verify():
    VERIFY_TOKEN = "ordenes-token"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def receive():
    print("📥 POST recibido:", request.json)
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000)
