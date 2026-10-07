import os
import requests
from flask import Flask, request

app = Flask(__name__)

# --- TUS DATOS DE WHATSAPP ---
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PC_GomezFarias")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN") # Tu token largo de Meta
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")

# --- DATOS DE TELEGRAM PARA VER EN EL CELULAR ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8915682882:AAETJDNOamlw6XYjHcLi1sLxeeoYvFvLrfc")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7480300697")

# Guardamos el ultimo numero que escribio para poder responderle desde Telegram
ultimo_numero = {}

def enviar_a_telegram(texto):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Error Telegram: {e}")

def enviar_whatsapp(numero, texto):
    try:
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        data = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": texto}
        }
        requests.post(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(f"Error WhatsApp: {e}")

@app.route('/')
def home():
    return "Bot de Proteccion Civil Gomez Farias Activo - WhatsApp + Telegram OK"

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Token invalido", 403

@app.route('/webhook', methods=['POST'])
def webhook_whatsapp():
    data = request.get_json()
    print(f"Datos recibidos: {data}")
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

                print(f"Mensaje de {numero}: {texto}")

                # Guardamos para responder despues
                ultimo_numero["numero"] = numero

                # 1. Reenviar a tu Telegram en el celular
                enviar_a_telegram(f"📩 *Nuevo WhatsApp*\nDe: {numero}\nMensaje: {texto}\n\nPara responder escribe en Telegram:\n/responder {texto}")

                # 2. Aqui va tu logica de bot automatico (puedes dejarla o quitarla)
                # Por ahora solo responde automatico si quieres
                # enviar_whatsapp(numero, f"Hola, soy el bot de Proteccion Civil. Recibimos: {texto}")

    except Exception as e:
        print(f"Error en webhook: {e}")

    return "OK", 200

# --- WEBHOOK PARA RESPONDER DESDE TELEGRAM HACIA WHATSAPP ---
@app.route('/telegram', methods=['POST'])
def webhook_telegram():
    data = request.get_json()
    try:
        message = data.get("message", {})
        texto = message.get("text", "")
        chat_id = str(message.get("chat", {}).get("id", ""))

        # Solo tu puedes responder
        if chat_id == TELEGRAM_CHAT_ID:
            if texto.startswith("/responder"):
                # Formato: /responder numero mensaje  o  /responder mensaje (responde al ultimo)
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
                    enviar_a_telegram("Usa: /responder NUMERO mensaje\nEjemplo: /responder 52614XXXXXXX Estamos en camino")
            else:
                # Si no usas comando, lo tomamos como respuesta al ultimo
                if "numero" in ultimo_numero and texto:
                    numero_destino = ultimo_numero["numero"]
                    enviar_whatsapp(numero_destino, texto)
                    enviar_a_telegram(f"✅ Enviado a {numero_destino}: {texto}")

    except Exception as e:
        print(f"Error telegram webhook: {e}")

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
