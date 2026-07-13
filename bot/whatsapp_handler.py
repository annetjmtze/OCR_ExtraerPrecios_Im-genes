@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    resp = MessagingResponse()
    msg = resp.message()
    try:
        incoming_msg = request.form.get("Body", "").strip()
        sender = request.form.get("From", "desconocido")
        logging.info(f"Mensaje de {sender}: {incoming_msg}")

        if not incoming_msg:
            msg.body("Por favor, envía el nombre de un medicamento.")
            return Response(str(resp), mimetype="application/xml")

        # Quitar /medicamento si está presente (compatibilidad)
        if incoming_msg.lower().startswith("/medicamento"):
            incoming_msg = incoming_msg[len("/medicamento"):].strip()

        # 1. Normalizar con LLM
        resultado = normalizer.normalizar(incoming_msg)
        if "error" in resultado:
            msg.body(f"❌ Error: {resultado['error']}")
            return Response(str(resp), mimetype="application/xml")

        nombre_generico = resultado.get('nombre_generico', '').lower()
        nombre_ingresado = resultado.get('nombre_ingresado', incoming_msg)

        # 2. Buscar precios en BD (get_resumen usa últimas 24h)
        precios = get_resumen(nombre_generico)

        if precios:
            # 3a. Hay precios → responder con ranking
            respuesta = f" *{nombre_generico.title()}*\n\n"
            respuesta += " *Precios en farmacias:*\n"
            for i, p in enumerate(precios, 1):
                linea = f"{i}. {p['farmacia']} — ${p['precio']:.2f}"
                if p.get('precio_promo'):
                    linea += f"\n ️ Promo: ${p['precio_promo']:.2f} (antes)"
                if p.get('vigencia'):
                    linea += f"\n Válido hasta: {p['vigencia']}"
                respuesta += linea + "\n"
            # Calcular antigüedad del precio más reciente
            if precios and precios[0].get('fecha'):
                try:
                    ts = datetime.fromisoformat(precios[0]['fecha'])
                    delta = datetime.now() - ts
                    horas = int(delta.total_seconds() // 3600)
                    respuesta += f"\n Precios actualizados hace {horas} horas"
                except:
                    pass
            respuesta += "\n↩️ Escribe otro medicamento para comparar"
            msg.body(respuesta)
        else:
            # 3b. No hay precios → responder inmediatamente sin prometer precios
            ficha = (
                f"📋 *Ficha de {nombre_ingresado}*\n\n"
                f"• *Nombre genérico:* {resultado.get('nombre_generico', 'N/D')}\n"
                f"• *Uso principal:* {resultado.get('uso_principal', 'N/D')}\n"
                f"• *¿Requiere receta?:* {'Sí' if resultado.get('requiere_receta') else 'No'}\n\n"
                "⚠️ *Aún no tenemos precios registrados para este medicamento.*\n\n"
                "Estamos actualizando nuestra base de datos.\n"
                "Intenta de nuevo mañana o busca otro medicamento."
            )

            msg.body(ficha)

    except Exception as e:
        logging.error(f"Error crítico en webhook: {e}", exc_info=True)
        msg.body("Ocurrió un error, intenta de nuevo.")

    return Response(str(resp), mimetype="application/xml")