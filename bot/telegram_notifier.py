import os
import logging
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message: str) -> bool:
    """
    Envía un mensaje al chat de Telegram configurado.
    Retorna True si se envió correctamente.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logging.warning("Telegram no configurado: token o chat_id faltantes")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            logging.info("Mensaje de Telegram enviado correctamente")
            return True
        else:
            logging.error(f"Error al enviar mensaje a Telegram: {response.text}")
            return False
    except Exception as e:
        logging.error(f"Excepción al enviar mensaje a Telegram: {e}")
        return False