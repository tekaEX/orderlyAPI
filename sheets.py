import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

# Autenticación Google
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
drive_service = build("drive", "v3", credentials=creds)

# Carpeta raíz
ORDERLY_FOLDER_ID = "1BmTLDkJyvuCaxWPViwdMjqfUyf55Cx_q"

def crear_carpeta_y_archivos_tienda(nombre_tienda, id_tienda):
    try:
        # Crear subcarpeta con el ID de la tienda (ej: T001)
        subcarpeta_metadata = {
            "name": id_tienda,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [ORDERLY_FOLDER_ID]
        }
        subcarpeta = drive_service.files().create(body=subcarpeta_metadata, fields="id").execute()
        subcarpeta_id = subcarpeta["id"]
        print(f"📁 Subcarpeta creada: {id_tienda} (ID: {subcarpeta_id})")

        # ===== Crear archivo de Inventario (ej: Inventario_Timelezz) =====
        archivo_inventario_metadata = {
            "name": f"Inventario_{nombre_tienda}",
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [subcarpeta_id]
        }
        inventario_file = drive_service.files().create(body=archivo_inventario_metadata, fields="id").execute()
        inventario_id = inventario_file["id"]

        sheet_inv = client.open_by_key(inventario_id)
        hoja_inv = sheet_inv.sheet1
        hoja_inv.update_title("Inventario")
        hoja_inv.append_row(["codigo", "nombre", "precio", "stock", "estado", "media_id_post", "talla", "color", "categoria", "observaciones"])
        print(f"📄 Archivo Inventario creado: Inventario_{nombre_tienda}")

        # ===== Crear archivo de Pedidos (ej: Pedidos_Timelezz) =====
        archivo_pedidos_metadata = {
            "name": f"Pedidos_{nombre_tienda}",
            "mimeType": "application/vnd.google-apps.spreadsheet",
            "parents": [subcarpeta_id]
        }
        pedidos_file = drive_service.files().create(body=archivo_pedidos_metadata, fields="id").execute()
        pedidos_id = pedidos_file["id"]

        sheet_ped = client.open_by_key(pedidos_id)
        hoja_ped = sheet_ped.sheet1
        hoja_ped.update_title("Pedidos")
        hoja_ped.append_row(["id_pedido", "fecha", "cliente_nombre", "instagram_usuario", "productos", "total", "tipo_entrega", "direccion_envio", "contacto", "estado", "observaciones"])
        print(f"📄 Archivo Pedidos creado: Pedidos_{nombre_tienda}")

        return {
            "carpeta_id": subcarpeta_id,
            "inventario_id": inventario_id,
            "pedidos_id": pedidos_id
        }

    except HttpError as error:
        print(f"❌ Error al crear carpeta o archivos: {error}")
        return None

def registrar_tienda_en_master(id_tienda, nombre_tienda, carpeta_id, inventario_id, pedidos_id, instagram_username="-", plan="Gratis", estado="activa"):
    try:
        hoja = client.open("Orderly_Master").worksheet("Tiendas")
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")

        hoja.append_row([
            id_tienda,
            nombre_tienda,
            carpeta_id,
            inventario_id,
            pedidos_id,
            instagram_username,
            plan,
            estado,
            fecha_hoy
        ])
        print(f"✅ Tienda {id_tienda} registrada correctamente en hoja Tiendas.")
        return True

    except Exception as e:
        import traceback
        print("❌ Error al registrar tienda en hoja Tiendas:")
        traceback.print_exc()
        return False
