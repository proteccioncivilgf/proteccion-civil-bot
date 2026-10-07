from flask import Flask, request
import requests
import os

app = Flask(_name_)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "PC_GomezFarias_VillaAldama_2025")

@app.route('/')
def home():
    return 'Bot de Protección Civil Gómez Farías Activo'

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return 'Error', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)
    try:
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                if 'messages' in value:
                    for msg in value['messages']:
                        from_num = msg['from']
                        text = msg.get('text', {}).get('body', '')
                        
                        respuesta = f"Hola, soy el Bot de Protección Civil de Gómez Farías 🚨\n\nRecibí: '{text}'\n\nSi es emergencia marca 911. En breve te atiende un elemento."

                        token = os.getenv("WHATSAPP_TOKEN")
                        phone_id = os.getenv("PHONE_NUMBER_ID")
                        
                        if token and phone_id:
                            url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
                            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                            payload = {"messaging_product": "whatsapp", "to": from_num, "text": {"body": respuesta}}
                            requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Error: {e}")
    return 'OK', 200

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=10000)
