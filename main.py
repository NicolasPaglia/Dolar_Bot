from flask import Flask
import requests
from telegram import Bot
from datetime import datetime
import os

# === CONFIGURACIÓN ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID tuyo o del grupo
bot = Bot(token=TELEGRAM_TOKEN)

app = Flask(__name__)

# === FUNCIONES ===
def obtener_datos_dolarapi():
    url = "https://dolarapi.com/v1/dolares"
    try:
        response = requests.get(url, timeout=5)
        return response.json()
    except Exception as e:
        print(f"❌ Error al consultar la API: {e}")
        return []

def formatear_mensaje(data):
    now = datetime.now().strftime("%d/%m/%Y %H:%M")
    mensaje = f"💵 *Cotización del Dólar* – {now}\n"

    for item in data:
        nombre = item.get("nombre", "")
        compra = item.get("compra", "-")
        venta = item.get("venta", "-")
        if nombre.lower() in ["mayorista"]:
            continue
        mensaje += f"• *{nombre}*: {compra} / {venta}\n"
    return mensaje

def enviar_mensaje():
    data = obtener_datos_dolarapi()
    if not data:
        bot.send_message(chat_id=CHAT_ID, text="⚠️ No se pudieron obtener los datos del dólar.")
        return
    mensaje = formatear_mensaje(data)
    bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")

# === ENDPOINT PARA CRON ===
@app.route("/send", methods=["GET"])
def send():
    enviar_mensaje()
    return "✅ Mensaje enviado al canal/usuario de Telegram"

# === RUTA BASE (opcional) ===
@app.route("/", methods=["GET"])
def home():
    return "🟢 Bot funcionando. Endpoint: /send"

# === MAIN ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
