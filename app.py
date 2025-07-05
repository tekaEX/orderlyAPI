from flask import Flask, request
import os
from sheets import agregar_pedido, buscar_sheet_pedidos_por_username, crear_tienda
from datetime import datetime

app = Flask(__name__)
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "orden_ordely_verification_token")

@app.route("/", methods=["GET"])
def home():
    return "OrderlyBot corriendo 🚀", 200

@app.route("/webhook", methods=["POST"])
def receive_message():
    data = request.get_json()
    print("📩 Mensaje recibido:", data)

    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            page_id = entry.get("id")
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                # Si tienes una función que obtiene el username real, úsala. Si no, usa page_id
                instagram_username = None
                # instagram_username = obtener_username_desde_api(sender_id) # Implementa si tienes la API
                if not instagram_username:
                    instagram_username = f"tienda_{page_id}"

                # Buscar hoja de pedidos, si no existe la tienda la crea automáticamente
                sheet_id = buscar_sheet_pedidos_por_username(instagram_username)
                if not sheet_id:
                    print(f"🆕 No existe tienda para {instagram_username}, creando...")
                    sheet_id = crear_tienda(instagram_username, page_id)

                if "message" in messaging_event:
                    message_text = messaging_event["message"].get("text")
                    if not message_text:
                        continue

                    nuevo_pedido = {
                        "pedido_id": f"P_{datetime.now().timestamp()}",
                        "estado": "pendiente",
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "instagram_usuario": sender_id,
                        "productos": message_text,
                        "total": "",
                        "tipo_entrega": "",
                        "direccion_envio": "",
                        "nombre_cliente": "",
                        "dirección": "",
                        "observaciones": "Mensaje directo recopilado automáticamente"
                    }

                    try:
                        agregar_pedido(sheet_id, nuevo_pedido)
                        print(f"✅ Pedido registrado en tienda {instagram_username}")
                    except Exception as e:
                        print("❌ Error al registrar el pedido:", str(e))

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
