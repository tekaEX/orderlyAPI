from flask import Flask, request
import os
from sheets import agregar_pedido, obtener_id_pedidos_por_page_id, registrar_debug
from datetime import datetime
import json

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "orden_ordely_verification_token")
DEBUG_LOG = "orderly_debug.log"

def log_debug(data):
    with open(DEBUG_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

@app.route("/", methods=["GET"])
def home():
    return "OrderlyBot corriendo 🚀", 200

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
    log_debug(data)  # Logging local

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            page_id = entry.get("id")
            sheet_id = obtener_id_pedidos_por_page_id(page_id)
            if not sheet_id:
                print(f"❌ No se encontró hoja de pedidos para tienda con page_id={page_id}")
                continue

            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    message_text = messaging_event["message"].get("text")
                    if not message_text:
                        continue  # Solo texto

                    nuevo_pedido = {
                        "pedido_id": f"P_{datetime.now().timestamp()}",
                        "instagram_usuario": sender_id,
                        "productos": message_text,
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "observaciones": "Mensaje directo recopilado automáticamente",
                        "total": "",
                        "tipo_entrega": "",
                        "direccion_envio": "",
                        "nombre_cliente": "",
                        "dirección": ""
                    }

                    try:
                        agregar_pedido(sheet_id, nuevo_pedido)
                        print(f"✅ Pedido registrado en tienda {page_id}")
                        registrar_debug(page_id, sender_id, message_text, "OK")
                    except Exception as e:
                        print("❌ Error al registrar el pedido:", str(e))
                        registrar_debug(page_id, sender_id, message_text, "ERROR", str(e))

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


