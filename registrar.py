from sheets import crear_carpeta_y_archivos_tienda, registrar_tienda_en_master

nombre_tienda = "Timelezz"
id_tienda = "T001"
instagram_username = "@timelezz"

resultado = crear_carpeta_y_archivos_tienda(nombre_tienda, id_tienda)

if resultado:
    exito = registrar_tienda_en_master(
        id_tienda=id_tienda,
        nombre_tienda=nombre_tienda,
        carpeta_id=resultado["carpeta_id"],
        inventario_id=resultado["inventario_id"],
        pedidos_id=resultado["pedidos_id"],
        instagram_username=instagram_username
    )
    if exito:
        print("✅ Registro completo.")
    else:
        print("⚠️ Se creó la tienda pero no se pudo registrar.")
else:
    print("❌ Falló la creación de archivos.")
