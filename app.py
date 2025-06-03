from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# 🔐 Carga de variables de entorno
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "orden_ordely_verification_token")
PAGE_ACCESS_TOKEN = os.environ.get("page_access_token")  # asegúrate de que esté bien en Render

# ✅ Ruta de verificación para Meta
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

# ✅ Ruta que procesa los eventos POST de mensajes
@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("📩 Mensaje recibido:", data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    message_text = messaging_event["message"].get("text")
                    print(f"🧾 Nuevo mensaje de {sender_id}: {message_text}")

                    responder_a_usuario(sender_id, "¡Gracias por tu mensaje! 🚀")

    return "EVENT_RECEIVED", 200

# 📬 Función para enviar un mensaje de vuelta por la API de Messenger
def responder_a_usuario(recipient_id, mensaje):
    if not PAGE_ACCESS_TOKEN:
        print("❌ ERROR: Falta PAGE_ACCESS_TOKEN")
        return

    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Content-Type": "application/json"}
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": mensaje}
    }

    response = requests.post(url, headers=headers, params=params, json=payload)
    print("📤 Respuesta enviada:", response.json())

# ✅ Este bloque asegura que solo Flask se ejecute localmente (no en gunicorn)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


