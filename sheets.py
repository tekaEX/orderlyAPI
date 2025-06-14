import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Autenticación Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Nombre y estructura de la hoja maestra
NOMBRE_MAESTRO = "Orderly_Master"
NOMBRE_HOJA_TIENDAS = "Tiendas"
COLUMNA_PAGE_ID = "page_id"
COLUMNA_ID_PEDIDOS = "id_sheet_pedidos"

# Columnas visuales del sheet de pedidos (ajusta aquí si cambias la plantilla)
CAMPOS = [
    "id_pedido", "fecha", "cliente_nombre", "instagram_usual", "productos", "total",
    "tipo_entrega", "direccion_envio", "contacto", "estado", "observaciones"
]

def obtener_id_pedidos_por_page_id(page_id):
    """
    Busca el ID del archivo de pedidos de la tienda según page_id en la hoja maestra.
    """
    hoja = client.open(NOMBRE_MAESTRO).worksheet(NOMBRE_HOJA_TIENDAS)
    datos = hoja.get_all_records()
    for tienda in datos:
        if str(tienda[COLUMNA_PAGE_ID]) == str(page_id):
            return tienda[COLUMNA_ID_PEDIDOS]
    return None

def agregar_pedido(sheet_id, datos):
    """
    Agrega un pedido a la hoja de pedidos especificada por sheet_id, respetando el formato visual (desde fila 8 en adelante).
    """
    hoja = client.open_by_key(sheet_id).sheet1

    # Encontrar la siguiente fila disponible, empezando desde la fila 8
    filas = hoja.get_all_values()
    fila_destino = len(filas) + 1 if len(filas) >= 8 else 8

    # Armar la fila según el orden de tu plantilla
    nueva_fila = [
        datos.get("id_pedido", ""),
        datos.get("fecha", datetime.now().strftime("%Y-%m-%d %H:%M")),
        datos.get("cliente_nombre", ""),
        datos.get("instagram_usual", ""),
        datos.get("productos", ""),
        datos.get("total", ""),
        datos.get("tipo_entrega", ""),
        datos.get("direccion_envio", ""),
        datos.get("contacto", ""),
        datos.get("estado", "pendiente"),
        datos.get("observaciones", "")
    ]

    hoja.insert_row(nueva_fila, fila_destino)
    print(f"✅ Pedido agregado en fila {fila_destino} (hoja {sheet_id})")

# Ejemplo de uso aislado
if __name__ == "__main__":
    # page_id de ejemplo
    page_id = "1234567890"
    sheet_id = obtener_id_pedidos_por_page_id(page_id)
    if not sheet_id:
        print("No se encontró la hoja de pedidos para este page_id.")
    else:
        pedido_demo = {
            "id_pedido": "P001",
            "cliente_nombre": "Juan Pérez",
            "instagram_usual": "@ejemplo",
            "productos": "Chaqueta L, Zapatillas 42",
            "total": "59990",
            "tipo_entrega": "Envío",
            "direccion_envio": "Calle Falsa 123",
            "contacto": "+56 9 1234 5678",
            "estado": "pendiente",
            "observaciones": "Cliente habitual"
        }
        agregar_pedido(sheet_id, pedido_demo)
        
def registrar_debug(page_id, sender_id, message_text, estado, observaciones=""):
    """
    Registra un log simple en la hoja Debug de Orderly_Master.
    """
    try:
        hoja = client.open(NOMBRE_MAESTRO).worksheet("Debug")
        nueva_fila = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            page_id,
            sender_id,
            message_text,
            estado,
            observaciones
        ]
        hoja.append_row(nueva_fila)
        print("📝 Debug registrado correctamente.")
    except Exception as e:
        print("❌ Error al registrar debugging en hoja:", str(e))
