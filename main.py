import os
import json
import anthropic
from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

load_dotenv()

app = Flask(__name__)

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Obtener mensaje
    mensaje = request.values.get("Body", "")
    
    # Crear respuesta base
    twilio_response = MessagingResponse()

    if not mensaje:
        twilio_response.message("No recibí ningún mensaje.")
        return str(twilio_response)

    try:
        # Llamada a Claude con un modelo que SÍ existe
        respuesta_claude = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Modelo robusto y ampliamente disponible
            max_tokens=300,
            system="""
Eres un asistente experto en medicamentos en México.

Tu respuesta DEBE ser únicamente un JSON con este formato:
{
"nombre ingresado": "string",
"nombre_generico": "string",
"uso_principal": "string",
"requiere_receta": boolean
}
""",
            messages=[
                {"role": "user", "content": mensaje}
            ]
        )

        texto = respuesta_claude.content[0].text
        # Limpiar marcadores de código
        texto = texto.replace("```json", "").replace("```", "").strip()
        datos = json.loads(texto)

        nombre = datos.get("nombre ingresado", "Desconocido")
        uso = datos.get("uso_principal", "No especificado")
        receta = "Sí" if datos.get("requiere_receta", False) else "No"

        respuesta_usuario = (
            f"💊 {nombre}\n\n"
            f"Uso principal: {uso}\n\n"
            f"¿Requiere receta? {receta}"
        )

    except Exception as e:
        # Imprimir el error en la terminal para depuración
        print("="*50)
        print("ERROR EN CLAUDE:")
        print(e)
        print("="*50)
        # Mensaje de error amigable
        respuesta_usuario = "Lo siento, ocurrió un error al procesar tu consulta. Por favor, intenta de nuevo."

    # Siempre enviamos la respuesta
    twilio_response.message(respuesta_usuario)
    return str(twilio_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)