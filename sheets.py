import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from config import ORD_MASTER_FOLDER_ID, PEDIDOS_TEMPLATE_ID, INVENTARIO_TEMPLATE_ID, MASTER_SHEET_ID

# Autenticación
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
drive = build('drive', 'v3', credentials=creds)

def buscar_sheet_pedidos_por_pageid(page_id):
    """Busca el sheet_id de pedidos correspondiente a un page_id en el master sheet."""
    sheet = client.open_by_key(MASTER_SHEET_ID).sheet1
    registros = sheet.get_all_records()
    for row in registros:
        if str(row.get("page_id", "")) == str(page_id):
            return row.get("pedidos_id")
    return None

def crear_tienda(instagram_username, page_id):
    """Crea carpeta y archivos para una nueva tienda, y la registra en el master sheet."""
    # 1. Crear carpeta para la tienda dentro de ORDEELY_MASTER
    carpeta = drive.files().create(
        body={
            "name": instagram_username,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [ORD_MASTER_FOLDER_ID]
        },
        fields="id"
    ).execute()
    carpeta_id = carpeta["id"]

    # 2. Copiar plantillas
    pedidos = drive.files().copy(
        fileId=PEDIDOS_TEMPLATE_ID,
        body={"name": f"pedidos_{instagram_username}", "parents": [carpeta_id]}
    ).execute()
    inventario = drive.files().copy(
        fileId=INVENTARIO_TEMPLATE_ID,
        body={"name": f"inventario_{instagram_username}", "parents": [carpeta_id]}
    ).execute()
    pedidos_id = pedidos["id"]
    inventario_id = inventario["id"]

    # 3. Registrar en master_sheet
    master_sheet = client.open_by_key(MASTER_SHEET_ID).sheet1
    fila = [
        instagram_username, page_id, carpeta_id, pedidos_id, inventario_id
    ]
    master_sheet.append_row(fila)
    return pedidos_id

def buscar_sheet_pedidos_por_username(username):
    """Busca el sheet_id de pedidos correspondiente a un username en el master sheet."""
    sheet = client.open_by_key(MASTER_SHEET_ID).sheet1
    registros = sheet.get_all_records()
    for row in registros:
        if row.get("instagram_username", "").lower() == username.lower():
            return row.get("pedidos_id")
    return None


def agregar_pedido(sheet_id, datos):
    """
    Agrega un pedido nuevo al Google Sheet de pedidos (desde la fila 8 para respetar el diseño visual).
    El orden de columnas es el siguiente:
    pedido_id, estado, tipo_entrega, fecha, instagram_usuario, nombre_cliente, rut, telefono, correo,
    comuna, dirección, productos, total, observaciones
    """
    hoja = client.open_by_key(sheet_id).sheet1
    filas = hoja.get_all_values()
    fila_destino = len(filas) + 1 if len(filas) >= 8 else 8
    nueva_fila = [
        datos.get("pedido_id", ""),
        datos.get("estado", "pendiente"),
        datos.get("tipo_entrega", ""),
        datos.get("fecha", ""),
        datos.get("instagram_usuario", ""),
        datos.get("nombre_cliente", ""),
        datos.get("rut", ""),
        datos.get("telefono", ""),
        datos.get("correo", ""),
        datos.get("comuna", ""),
        datos.get("dirección", ""),
        datos.get("productos", ""),
        datos.get("total", ""),
        datos.get("observaciones", "")
    ]
    hoja.insert_row(nueva_fila, fila_destino)
