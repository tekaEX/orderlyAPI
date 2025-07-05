from flask import Flask, request
from datetime import datetime
import re

# Asegúrate de importar o definir tus funciones para Google Sheets
from sheets import buscar_sheet_pedidos_por_pageid, agregar_pedido

app = Flask(__name__)
VERIFY_TOKEN = "ordenes-token"

CAMPO_REGEX = {
    "productos": r"Producto:\s*(.+)",
    "total": r"Total:\s*(.+)",
    "tipo_entrega": r"Entrega:\s*(.+)",
    "nombre_cliente": r"Nombre:\s*(.+)",
    "rut": r"RUT:\s*(.+)",
    "telefono": r"Tel[eé]fono:\s*(.+)",
    "correo": r"Correo:\s*(.+)",
    "direccion": r"Direcci[oó]n\s*:?\s*(.+)",
    "comuna": r"Comuna:\s*(.+)",
    "observaciones": r"Observaciones:\s*(.+)",
}

def parsear_mensaje_pedido(texto):
    resultado = {}
    for campo, regex in CAMPO_REGEX.items():
        match = re.search(regex, texto, re.IGNORECASE)
        resultado[campo] = match.group(1).strip() if match else ""
    return resultado

@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def receive():
    data = request.json
    print("📥 POST recibido:", data)

    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            page_id = entry.get("id")
            if not page_id:
                print("❌ No se encontró page_id")
                continue

            sheet_id = buscar_sheet_pedidos_por_pageid(page_id)
            if not sheet_id:
                print(f"❌ No se encontró hoja de pedidos para tienda con page_id={page_id}")
                continue

            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    message_text = messaging_event["message"].get("text")
                    if not message_text:
                        continue

                    campos = parsear_mensaje_pedido(message_text)
                    nuevo_pedido = {
                        "pedido_id": f"P_{datetime.now().timestamp()}",
                        "estado": "pendiente",
                        "tipo_entrega": campos["tipo_entrega"],
                        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "instagram_usuario": sender_id,
                        "nombre_cliente": campos["nombre_cliente"],
                        "rut": campos["rut"],
                        "telefono": campos["telefono"],
                        "correo": campos["correo"],
                        "comuna": campos["comuna"],
                        "dirección": campos["direccion"],
                        "productos": campos["productos"],
                        "total": campos["total"],
                        "observaciones": campos["observaciones"],
                    }
                    try:
                        agregar_pedido(sheet_id, nuevo_pedido)
                        print(f"✅ Pedido registrado en tienda {page_id}")
                    except Exception as e:
                        print("❌ Error al registrar el pedido:", str(e))

    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    app.run(port=5000)
