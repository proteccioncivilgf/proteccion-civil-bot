import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- TUS DATOS ---
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PC_GomezFarias")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8915682882:AAETJDNOamlw6XYjHcLi1sLxeeoYvFvLrfc")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7480300697")

ultimo_numero = {}

# --- PALABRAS QUE ACTIVAN ALERTA HUMANA ---
PALABRAS_ALERTA = [
    "hablar con alguien",
    "mensajear con alguien",
    "hablar con una persona",
    "quiero hablar con alguien",
    "hablar con humano",
    "hablar con operador",
    "persona real",
    "operador",
    "humano",
    "asesor",
    "ayuda humana"
]

def enviar_a_telegram(texto, urgente=False):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        if urgente:
            texto = f"🚨🚨🚨 ALERTA HUMANA 🚨🚨🚨\n\n{texto}\n\n⚠️ Alguien quiere hablar contigo, responde rapido!"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Error Telegram: {e}")

def enviar_whatsapp(numero, texto):
    try:
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        data = {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": texto}}
        r = requests.post(url, headers=headers, json=data, timeout=10)
        print(f"WhatsApp enviado: {r.text}")
    except Exception as e:
        print(f"Error WhatsApp: {e}")

@app.route('/')
def home():
    return "Bot PC Gomez Farias Activo - Modo Hibrido"

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Token invalido", 403

@app.route('/webhook', methods=['POST'])
def webhook_whatsapp():
    data = request.get_json()
    try:
        if data and data.get("object"):
            entry = data["entry"][0]
            changes = entry["changes"][0]
            value = changes.get("value", {})
            messages = value.get("messages", [])

            if messages:
                msg = messages[0]
                numero = msg["from"]
                texto = msg.get("text", {}).get("body", "")
                texto_lower = texto.lower()

                print(f"Mensaje de {numero}: {texto}")
                ultimo_numero["numero"] = numero

                # Checar si quiere hablar con humano
                quiere_humano = any(palabra in texto_lower for palabra in PALABRAS_ALERTA)

                if quiere_humano:
                    # ALERTA A TELEGRAM
                    enviar_a_telegram(f"📩 *De:* {numero}\n*Mensaje:* {texto}\n*Numero:* `{numero}`", urgente=True)
                    # Mensaje a la persona
                    enviar_whatsapp(numero, "✅ Entendido. Te estoy conectando con un operador de Protección Civil Gómez Farías. En un momento te atiende una persona. Por favor no cierres el chat.")
                else:
                    # MODO BOT AUTOMATICO NORMAL
                    enviar_a_telegram(f"📩 *Nuevo WhatsApp*\nDe: {numero}\nMensaje: {texto}\n\nPara responder escribe en Telegram:\n/responder {numero} Tu mensaje")
                    
                    # --- AQUI VA TU MENU AUTOMATICO ---
                    # Puedes cambiar este texto
                    respuesta_bot = (
                        "👋 Hola, soy el asistente de *Protección Civil Gómez Farías* 🏔️\n\n"
                        "¿En qué te puedo ayudar?\n"
                        "1️⃣ Reportar emergencia\n"
                        "2️⃣ Reportar incendio\n"
                        "3️⃣ Información de clima\n"
                        "4️⃣ Hablar con un operador humano\n\n"
                        "Escribe el número o escribe *hablar con alguien* para que te atienda una persona."
                    )
                    # Solo responde automatico si no es la primera vez que pide humano
                    # Si quieres que siempre conteste el bot, deja esta linea activa:
                    enviar_whatsapp(numero, respuesta_bot)

    except Exception as e:
        print(f"Error en webhook: {e}")

    return "OK", 200

@app.route('/telegram', methods=['POST'])
def webhook_telegram():
    data = request.get_json()
    try:
        message = data.get("message", {})
        texto = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))

        if chat_id == TELEGRAM_CHAT_ID and texto:
            if texto.startswith("/responder"):
                partes = texto.split(" ", 2)
                if len(partes) == 3:
                    numero_destino = partes[1]
                    mensaje_respuesta = partes[2]
                    enviar_whatsapp(numero_destino, mensaje_respuesta)
                    enviar_a_telegram(f"✅ Enviado a {numero_destino}: {mensaje_respuesta}")
                elif len(partes) == 2 and "numero" in ultimo_numero:
                    mensaje_respuesta = partes[1]
                    numero_destino = ultimo_numero["numero"]
                    enviar_whatsapp(numero_destino, mensaje_respuesta)
                    enviar_a_telegram(f"✅ Enviado a {numero_destino}: {mensaje_respuesta}")
            else:
                # Respuesta directa al ultimo numero
                if "numero" in ultimo_numero:
                    numero_destino = ultimo_numero["numero"]
                    enviar_whatsapp(numero_destino, texto)
                    enviar_a_telegram(f"✅ Enviado a {numero_destino}: {texto}")
    except Exception as e:
        print(f"Error telegram webhook: {e}")

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
