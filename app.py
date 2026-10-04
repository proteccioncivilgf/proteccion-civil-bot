from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

# CONFIG - Tus datos
VERIFY_TOKEN = "PC_GF_2025_VERIFICA_CHIHUAHUA"
# El último token que me diste - CAMBIALO si generas uno nuevo
ACCESS_TOKEN = "EAAPJjQGyykYBSj1dv7r9S0rfoHbBYQ1THL35sEIBkE4B9JZBqZBCvNIVPXV5zxQ1pWe4CaARE0yvKsAhbZChtGPCvAcrZCANlCklQZAF0ky3fYNS0oQKlD5h63DhOd6ambIXnpleC02tkN00LfrctXy3qgpROTRQSnZCb6wUcm9BiCu0WZAZBVPmkGQ4EQ21825NJcYeq5bgNJfgPnexPdFar6UKgfjZCePlevx7OCLTd0DkrL4eFf4YK8QZDZD"
PHONE_NUMBER_ID = "1342634898935598"

@app.route('/')
def home():
    return "Bot Protección Civil GF - Activo ✅", 200

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFICADO!")
        return challenge, 200
    else:
        return "Token invalido", 403

@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print(f"Mensaje recibido: {data}")
    
    if data and 'entry' in data:
        for entry in data['entry']:
            for change in entry.get('changes', []):
                value = change.get('value', {})
                messages = value.get('messages', [])
                for msg in messages:
                    from_number = msg.get('from')
                    text = msg.get('text', {}).get('body', '').lower()
                    handle_proteccion_civil(from_number, text, msg)
    
    return jsonify({"status": "ok"}), 200

def handle_proteccion_civil(to, text, msg_obj):
    # Lógica del bot de Protección Civil
    if "hola" in text or "inicio" in text:
        reply = (
            "🚨 *Protección Civil Chihuahua* 🚨\n\n"
            "Bienvenido al sistema de reportes.\n"
            "Escribe el número de tu emergencia:\n\n"
            "1️⃣ Inundación / Encharcamiento\n"
            "2️⃣ Incendio\n"
            "3️⃣ Árbol caído / Poste\n"
            "4️⃣ Fuga de gas / Químico\n"
            "5️⃣ Persona lesionada\n"
            "6️⃣ Otro reporte\n\n"
            "O envía tu *ubicación* directamente."
        )
    elif "1" in text or "inundacion" in text:
        reply = "💧 Reporte de INUNDACIÓN recibido.\nPor favor envía tu UBICACIÓN por WhatsApp y una foto si es posible. ¿Qué altura tiene el agua?"
    elif "2" in text or "incendio" in text:
        reply = "🔥 Reporte de INCENDIO recibido.\n¿Es en casa, baldío o forestal? Envía tu UBICACIÓN inmediata."
    elif "ubicacion" in text or msg_obj.get('type') == 'location':
        reply = "📍 Ubicación recibida. Una unidad va en camino. ¿Puedes dejar un número de contacto? Mantente en lugar seguro."
    else:
        reply = f"✅ Recibimos: '{text}'\nTu reporte ha sido registrado en el sistema GF. Un operador te contactará. Para nuevo reporte escribe HOLA."

    send_whatsapp_message(to, reply)

def send_whatsapp_message(to, body):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body}
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"Enviado a {to}: {r.status_code} {r.text}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
