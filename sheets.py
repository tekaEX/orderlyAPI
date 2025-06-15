import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURACIÓN ===
CREDENTIALS_FILE = "credentials.json"
MASTER_SHEET_ID = "1HoliJ9KPNud6N8ap8_nmYnWWH1pUpz-h5AwnIUVqCH8"  # El archivo 'ordeely_master' (no el de pedidos)
# O puedes obtenerlo por nombre:
# MASTER_SHEET_NAME = "ordeely_master"

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# === 1. Buscar sheet de pedidos por page_id ===
def buscar_sheet_pedidos_por_pageid(page_id):
    """
    Busca el ID del archivo de pedidos asociado al page_id en la hoja principal de tiendas.
    """
    sheet = client.open_by_key(MASTER_SHEET_ID).sheet1
    filas = sheet.get_all_records()
    for row in filas:
        # Puede ser que tu hoja lo guarde como 'id_tienda' o como 'carpeta_id', revisa el nombre correcto
        # page_id puede estar en 'id_tienda' o 'instagram_username', revisa tus columnas
        if str(row.get("id_tienda")) == str(page_id) or str(row.get("carpeta_id")) == str(page_id):
            return row.get("pedidos_id")
    return None

# === 2. Agregar pedido al archivo de pedidos ===
def agregar_pedido(sheet_id, datos_pedido):
    """
    Agrega un nuevo pedido a la hoja de pedidos (sheet_id).
    Espera un diccionario con los campos apropiados.
    """
    hoja = client.open_by_key(sheet_id).sheet1

    # Ajusta el orden y nombres de las columnas a las de tu plantilla real de pedidos:
    fila = [
        datos_pedido.get("pedido_id", ""),
        datos_pedido.get("estado", "pendiente"),
        datos_pedido.get("fecha", ""),
        datos_pedido.get("instagram_usuario", ""),
        datos_pedido.get("productos", ""),
        datos_pedido.get("total", ""),
        datos_pedido.get("tipo_entrega", ""),
        datos_pedido.get("direccion_envio", ""),
        datos_pedido.get("nombre_cliente", ""),
        datos_pedido.get("dirección", ""),
        datos_pedido.get("observaciones", "")
    ]

    # Puedes definir la fila inicial si tu plantilla tiene encabezados o formato visual
    # Por ejemplo, si tienes 7 filas decorativas/encabezado, inicia en la 8:
    hoja.insert_row(fila, 8)
    print(f"✅ Pedido agregado a la hoja {sheet_id}")

# === Ejemplo de prueba ===
if __name__ == "__main__":
    # Simula un pedido
    ejemplo = {
        "pedido_id": "P123",
        "estado": "pendiente",
        "fecha": "2025-06-14",
        "instagram_usuario": "@prueba",
        "productos": "Chaqueta L",
        "total": "29990",
        "tipo_entrega": "envío",
        "direccion_envio": "Calle Falsa 123",
        "nombre_cliente": "Juan Pérez",
        "dirección": "Santiago",
        "observaciones": "Mensaje directo"
    }
    sheet_id = "ID_DE_LA_HOJA_DE_PEDIDOS_DE_PRUEBA"
    agregar_pedido(sheet_id, ejemplo)
