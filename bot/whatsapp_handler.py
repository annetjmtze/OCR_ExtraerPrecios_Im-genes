import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from llm.normalizer import MedicamentoNormalizer
from data.database import get_resumen
from bot.counter import increment_and_check_limit, LIMITE_DIARIO, LIMITE_NOTIFICACION
from bot.telegram_notifier import send_telegram_message

load_dotenv()

app = Flask(__name__)
normalizer = MedicamentoNormalizer()

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

        if incoming_msg.lower().startswith("/medicamento"):
            incoming_msg = incoming_msg[len("/medicamento"):].strip()

        resultado = normalizer.normalizar(incoming_msg)
        if "error" in resultado:
            msg.body(f"❌ Error: {resultado['error']}")
            return Response(str(resp), mimetype="application/xml")

        nombre_generico = resultado.get('nombre_generico', '').lower()
        nombre_ingresado = resultado.get('nombre_ingresado', incoming_msg)

        precios = get_resumen(nombre_generico)

        if precios:
            respuesta = f" *{nombre_generico.title()}*\n\n"
            respuesta += " *Precios en farmacias:*\n"
            for i, p in enumerate(precios, 1):
                linea = f"{i}. {p['farmacia']} — ${p['precio']:.2f}"
                if p.get('precio_promo'):
                    linea += f"\n ️ Promo: ${p['precio_promo']:.2f} (antes)"
                if p.get('vigencia'):
                    linea += f"\n Válido hasta: {p['vigencia']}"
                respuesta += linea + "\n"
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

        # --- NOTIFICACIÓN TELEGRAM (3c) ---
        if increment_and_check_limit():
            mensaje = (
                f"⚠️ *Dr. Ahorro* — Límite diario al 80%\n"
                f"Hoy se han procesado {LIMITE_NOTIFICACION} mensajes de {LIMITE_DIARIO} permitidos.\n"
                f"Revisa el uso del sandbox de Twilio."
            )
            send_telegram_message(mensaje)

    except Exception as e:
        logging.error(f"Error crítico en webhook: {e}", exc_info=True)
        msg.body("Ocurrió un error, intenta de nuevo.")

    return Response(str(resp), mimetype="application/xml")

# --------------------------------------------
#  🆕 FUNCIÓN AÑADIDA PARA QUE main.py FUNCIONE
# --------------------------------------------
def run_whatsapp_bot(port=5000):
    """
    Función que arranca el servidor Flask para recibir mensajes de WhatsApp.
    Esta es la función que main.py está importando.
    """
    # debug=False evita problemas con hilos cuando usas --channel all
    app.run(host="0.0.0.0", port=port, debug=False)


# Este bloque se ejecuta solo si corres este archivo directamente
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)