from flask import Flask
import requests
from telegram import Bot
from datetime import datetime
import os
import asyncio

# === CONFIGURACIÓN ===
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # Puede ser tu chat personal o canal
bot = Bot(token=TELEGRAM_TOKEN)

app = Flask(__name__)

# === FUNCIONES ===

def obtener_datos_dolarapi():
    url = "https://dolarapi.com/v1/dolares"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        print("✅ Datos obtenidos de la API.")
        return data
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

        if nombre.lower() == "mayorista":
            continue

        mensaje += f"• *{nombre}*: {compra} / {venta}\n"

    return mensaje

async def enviar_mensaje_async():
    print("📡 Obteniendo cotización...")
    data = obtener_datos_dolarapi()

    if not data:
        print("⚠️ No se pudieron obtener los datos del dólar.")
        await bot.send_message(chat_id=CHAT_ID, text="⚠️ No se pudieron obtener los datos del dólar.")
        return

    mensaje = formatear_mensaje(data)
    print("📨 Enviando mensaje a Telegram...")
    try:
        await bot.send_message(chat_id=CHAT_ID, text=mensaje, parse_mode="Markdown")
        print("✅ Mensaje enviado correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar el mensaje: {e}")

# === ENDPOINT PARA CRON-JOB.ORG ===
@app.route("/send", methods=["GET"])
def send():
    print("📥 Solicitud recibida en /send")
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(enviar_mensaje_async())
        return "✅ Mensaje enviado al canal/usuario de Telegram"
    except Exception as e:
        print(f"❌ Error en loop: {e}")
        return f"❌ Error al enviar mensaje: {e}", 500

# === ENDPOINT PARA OBTENER CHAT_ID ===
@app.route("/get_id", methods=["GET"])
def get_id():
    print("🔍 Solicitando actualizaciones desde la API de Telegram...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        response = requests.get(url)
        data = response.json()

        if "result" in data and len(data["result"]) > 0:
            last_message = data["result"][-1]
            chat_id = last_message["message"]["chat"]["id"]
            print(f"🆔 Último chat_id detectado: {chat_id}")
            return f"<b>🆔 Tu CHAT_ID es:</b> <code>{chat_id}</code>", 200, {'Content-Type': 'text/html'}
        else:
            return "⚠️ No hay mensajes recientes. Escribí algo al bot primero.", 200, {'Content-Type': 'text/html'}

    except Exception as e:
        print(f"❌ Error al obtener el chat_id: {e}")
        return f"<b>❌ Error al obtener el chat_id:</b> {e}", 500, {'Content-Type': 'text/html'}

# === ENDPOINT BASE ===
@app.route("/", methods=["GET"])
def home():
    return "🟢 Bot funcionando correctamente. Endpoint principal: /send"

# === MAIN ===
if __name__ == "__main__":
    print("🚀 Bot ejecutándose en Render...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
