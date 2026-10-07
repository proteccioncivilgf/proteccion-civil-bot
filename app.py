from flask import Flask, request
import requests
import os

app = Flask(__name__)
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "PC_GomezFarias_2025")
PHONE_CALL = "+52 652 104 8672"
PHONE_ID_NUMBER = "6521048672"

def call_api(payload):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_id = os.getenv("PHONE_NUMBER_ID")
    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload)
    print(f"API: {r.status_code} - {r.text}")
    return r

def enviar_mensaje(to, text):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    return call_api(payload)

def enviar_menu_principal(to):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "Hola soy el bot de proteccion civil de Gomez Farias, ¿cual es tu emergencia?"},
            "action": {
                "button": "Ver opciones",
                "sections": [{
                    "title": "Selecciona",
                    "rows": [
                        {"id": "opt_contacto", "title": "Contactanos", "description": "Llamar a PC 6521048672"},
                        {"id": "opt_accidente", "title": "Un accidente", "description": "Vehicular o caida"},
                        {"id": "opt_incendio", "title": "Incendio", "description": "Fuego o quema"},
                        {"id": "opt_inundacion", "title": "Inundacion", "description": "Agua o arroyo crecido"},
                        {"id": "opt_clima", "title": "Clima / Alerta", "description": "Pronostico y alertas"},
                        {"id": "opt_pareja", "title": "Discusion de pareja", "description": "Pleito o violencia"},
                        {"id": "opt_otros", "title": "Otros", "description": "Otra emergencia"}
                    ]
                }]
            }
        }
    }
    r = call_api(payload)
    if r.status_code != 200:
        enviar_mensaje(to, "Hola soy el bot de proteccion civil de Gomez Farias, ¿cual es tu emergencia?\n1 Contactanos\n2 Accidente\n3 Incendio\n4 Inundacion\n5 Clima\n6 Discusion pareja\n7 Otros")

def enviar_contacto_directo(to):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "cta_url",
            "body": {"text": f"📞 *CONTACTANOS DIRECTO*\n\nProteccion Civil Gomez Farias\nTel: {PHONE_CALL}\nNumero PC: {PHONE_ID_NUMBER}\n\nPresiona el boton para contactar o comparte tu ubicacion aqui."},
            "action": {
                "name": "cta_url",
                "parameters": {
                    "display_text": "Contactar 652 104 8672",
                    "url": f"https://wa.me/52{PHONE_ID_NUMBER}"
                }
            }
        }
    }
    r = call_api(payload)
    if r.status_code != 200:
        enviar_mensaje(to, f"📞 Contacto directo a Proteccion Civil: {PHONE_CALL}\nMarca directo desde tu telefono al {PHONE_ID_NUMBER}\nO comparte tu ubicacion por aqui.")

def enviar_submenu_accidente(to):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "🚗 *ACCIDENTE REPORTADO*\n\nPara ayudarte rapido selecciona:"},
            "action": {
                "button": "Opciones accidente",
                "sections": [{
                    "title": "¿Que necesitas?",
                    "rows": [
                        {"id": "acc_ubicacion", "title": "Mandar ubicacion", "description": "Comparte ubicacion por WhatsApp"},
                        {"id": "acc_lesionado", "title": "Si hay lesionados", "description": "Hay heridos"},
                        {"id": "acc_grua", "title": "Ocupan grua", "description": "Vehiculo no se mueve"},
                        {"id": "acc_ambulancia", "title": "Ocupan ambulancia", "description": "Enviar ambulancia"},
                        {"id": "acc_llamar", "title": "Llamar a PC", "description": f"Marcar al {PHONE_ID_NUMBER}"}
                    ]
                }]
            }
        }
    }
    call_api(payload)

def enviar_submenu_pareja(to):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": "👫 *DISCUSION DE PAREJA / PLEITO*\n\nSelecciona una opcion:"},
            "action": {
                "button": "Opciones pleito",
                "sections": [{
                    "title": "¿Que necesitas?",
                    "rows": [
                        {"id": "pareja_ubicacion", "title": "Mandar ubicacion", "description": "Direccion confidencial"},
                        {"id": "pareja_lesionado", "title": "Hay lesionados", "description": "Persona herida"},
                        {"id": "pareja_ambulancia", "title": "Ocupan ambulancia", "description": "Enviar ambulancia"},
                        {"id": "pareja_llamar", "title": "Llamar a PC", "description": f"Marcar al {PHONE_ID_NUMBER}"}
                    ]
                }]
            }
        }
    }
    call_api(payload)

def enviar_submenu_incendio(to, tipo="Incendio"):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": f"🔥 *{tipo.upper()} REPORTADO*\n\nSelecciona que ocupas:"},
            "action": {
                "button": "Opciones",
                "sections": [{
                    "title": "¿Que necesitas?",
                    "rows": [
                        {"id": "inc_ubicacion", "title": "Mandar ubicacion", "description": "Donde es el fuego/agua"},
                        {"id": "inc_ambulancia", "title": "Ocupan ambulancia", "description": "Hay heridos"},
                        {"id": "inc_bomberos", "title": "Ocupan bomberos", "description": "Enviar bomberos"},
                        {"id": "inc_llamar", "title": "Llamar a PC", "description": f"Marcar al {PHONE_ID_NUMBER}"}
                    ]
                }]
            }
        }
    }
    call_api(payload)

@app.route('/')
def home():
    return 'Bot de Proteccion Civil Gomez Farias Activo'

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
                        if msg.get('type') == 'interactive':
                            list_id = msg.get('interactive', {}).get('list_reply', {}).get('id','')
                            btn_id = msg.get('interactive', {}).get('button_reply', {}).get('id','')
                            selected = list_id or btn_id
                            print(f"Seleccion: {selected}")

                            if selected == 'opt_clima':
                                enviar_mensaje(from_num, "🌧 *CLIMA / ALERTA GOMEZ FARIAS*\n\nMantente atento a lluvias fuertes y vientos. Evita cruzar arroyos. Asegura laminas.\n\nSi ves riesgo, reportalo aqui con ubicacion.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'opt_contacto':
                                enviar_contacto_directo(from_num)
                            elif selected == 'opt_accidente':
                                enviar_mensaje(from_num, "Has seleccionado: Un accidente. ¿Que necesitas?")
                                enviar_submenu_accidente(from_num)
                            elif selected == 'opt_pareja':
                                enviar_submenu_pareja(from_num)
                            elif selected == 'opt_incendio':
                                enviar_submenu_incendio(from_num, "Incendio")
                            elif selected == 'opt_inundacion':
                                enviar_submenu_incendio(from_num, "Inundacion")
                            elif selected == 'opt_otros':
                                enviar_mensaje(from_num, "Describe tu emergencia y comparte tu ubicacion por WhatsApp. O contacta directo.")
                                enviar_contacto_directo(from_num)

                            elif selected == 'acc_ubicacion':
                                enviar_mensaje(from_num, "📍 Por favor comparte tu ubicacion usando el clip 📎 > Ubicacion > Enviar ubicacion actual.\nEsto nos ayuda a llegar rapido.")
                            elif selected == 'acc_lesionado':
                                enviar_mensaje(from_num, "🩹 Hay lesionados: ¿Cuantos? ¿Estan conscientes? No los muevas si hay fractura. Presiona si hay sangrado. Comparte ubicacion aqui.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'acc_grua':
                                enviar_mensaje(from_num, "🚜 Ocupan grua: Comparte ubicacion y tipo de vehiculo. Ya estamos avisando a Seguridad Publica.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'acc_ambulancia':
                                enviar_mensaje(from_num, "🚑 Ambulancia solicitada. Comparte ubicacion exacta. ¿Cuantos lesionados?")
                                enviar_contacto_directo(from_num)
                            elif selected == 'acc_llamar':
                                enviar_contacto_directo(from_num)

                            elif selected == 'pareja_ubicacion':
                                enviar_mensaje(from_num, "📍 Comparte tu ubicacion de forma confidencial por aqui (clip > Ubicacion). Si hay menores en riesgo mencionalo.")
                            elif selected == 'pareja_lesionado':
                                enviar_mensaje(from_num, "Hay lesionados por discusion: ¿Necesita atencion? No te expongas. Comparte ubicacion.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'pareja_ambulancia':
                                enviar_mensaje(from_num, "🚑 Ambulancia solicitada. Comparte ubicacion.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'pareja_llamar':
                                enviar_contacto_directo(from_num)

                            elif selected == 'inc_ubicacion':
                                enviar_mensaje(from_num, "📍 Comparte ubicacion y si puedes una foto o video del lugar (si es seguro). Que tan grande es el incendio o inundacion?")
                            elif selected == 'inc_ambulancia':
                                enviar_mensaje(from_num, "🚑 Ambulancia solicitada para incendio/inundacion. Comparte ubicacion.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'inc_bomberos':
                                enviar_mensaje(from_num, "🔥🚒 Bomberos notificados. Alejate del area, no intentes apagar si es grande. Comparte ubicacion.")
                                enviar_contacto_directo(from_num)
                            elif selected == 'inc_llamar':
                                enviar_contacto_directo(from_num)

                            continue

                        txt = msg.get('text', {}).get('body', '')
                        lower = txt.lower().strip()
                        print(f"Texto: {txt}")
                        saludos = ['hola','buenos dias','buen dia','buenas tardes','buenas noches','buenas','ola','menu','inicio']
                        if any(s in lower for s in saludos):
                            enviar_menu_principal(from_num)
                        else:
                            enviar_menu_principal(from_num)
    except Exception as e:
        print(f"Error: {e}")
    return 'OK', 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
