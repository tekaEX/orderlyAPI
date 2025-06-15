import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from datetime import datetime

# CONFIGURACIÓN: Pega tus datos aquí
CREDENTIALS_FILE = "credentials.json"
MASTER_SHEET_ID = "1HoliJ9KPNud6N8ap8_nmYnWWH1pUpz-h5AwnIUVqCH8"
MASTER_FOLDER_ID = "1Va40ZB1BhznklLWQeAYEmvAdX05nLnHZ"  # Carpeta content
PEDIDOS_TEMPLATE_ID = "1cd2qKua65r-rHQ6BysXdRrV6sRobb--b8-LzK_A-SKs"

# Columnas esperadas en la hoja "tiendas"
CAMPOS = [
    "id_tienda", "nombre_tienda", "carpeta_id", "inventario_id", "pedidos_id",
    "instagram_username", "plan", "estado", "fecha_registro"
]

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
drive_service = build("drive", "v3", credentials=creds)

def tienda_existe(instagram_username):
    sheet = client.open_by_key(MASTER_SHEET_ID).sheet1
    records = sheet.get_all_records()
    return any(row['instagram_username'] == instagram_username for row in records)

def crear_carpeta_drive(id_tienda):
    carpeta_metadata = {
        "name": id_tienda,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [MASTER_FOLDER_ID]
    }
    carpeta = drive_service.files().create(body=carpeta_metadata, fields="id").execute()
    return carpeta["id"]

def copiar_plantilla(nombre_archivo, plantilla_id, carpeta_id):
    body = {
        'name': nombre_archivo,
        'parents': [carpeta_id],
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }
    archivo_copiado = drive_service.files().copy(fileId=plantilla_id, body=body).execute()
    return archivo_copiado['id']

def registrar_nueva_tienda(nombre_tienda, instagram_username):
    if tienda_existe(instagram_username):
        print("🚫 La tienda ya existe")
        return

    id_tienda = f"T{int(datetime.now().timestamp())}"
    carpeta_id = crear_carpeta_drive(id_tienda)
    pedidos_id = copiar_plantilla(f"Pedidos_{nombre_tienda}", PEDIDOS_TEMPLATE_ID, carpeta_id)

    fila = [
        id_tienda, nombre_tienda, carpeta_id, "", pedidos_id,
        instagram_username, "gratuito", "activo", datetime.now().strftime("%Y-%m-%d %H:%M")
    ]
    sheet = client.open_by_key(MASTER_SHEET_ID).sheet1
    sheet.append_row(fila)
    print(f"✅ Tienda registrada: {nombre_tienda} ({instagram_username})")
    print(f"📁 Carpeta creada: {carpeta_id}")
    print(f"📄 Hoja de pedidos creada: {pedidos_id}")

if __name__ == "__main__":
    # MODIFICA ESTO para registrar la tienda que quieras
    nombre_tienda = input("Nombre de la tienda: ")
    instagram_username = input("Instagram (sin @): ")
    registrar_nueva_tienda(nombre_tienda, instagram_username)
