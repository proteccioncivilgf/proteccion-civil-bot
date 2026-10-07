import os
from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PC_GomezFarias_VillaAldama_2025")

@app.route('/')
def home():
    return 'Bot PC Gomez Farias - Villa Aldama ACTIVO', 200

@app.route('/webhook', methods=['GET'])
def verificar():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    print(f"Intento verificacion: {mode} token recibido: {token} esperado: {VERIFY_TOKEN}")
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("VERIFICACION EXITOSA")
        return challenge, 200
    else:
        print("VERIFICACION FALLIDA")
        return 'Forbidden', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"Mensaje recibido: {data}")
    # Aqui luego ponemos la logica del bot
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
