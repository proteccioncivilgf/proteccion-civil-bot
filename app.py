import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PC_GomezFarias")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8915682882:AAETJDNOamlw6XYjHcLi1sLxeeoYvFvLrfc")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7480300697")

user_state = {}
ultimo_numero = {}

def enviar_a_telegram(texto, urgente=False):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        if urgente:
            texto = f"🚨🚨🚨 ALERTA HUMANA 🚨🚨🚨\n\n{texto}"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Error Telegram texto: {e}")

def enviar_foto_a_telegram(numero, whatsapp_media_url, caption=""):
    try:
        # Primero mandamos texto avisando
        url_msg = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url_msg, data={"chat_id": TELEGRAM_CHAT_ID, "text": f"📸 Foto recibida de {numero}\nCaption: {caption}"}, timeout=10)
        
        # Luego mandamos la foto usando la URL de WhatsApp
        # Telegram puede descargar desde la URL de Facebook si le pasamos la URL directa
        url_foto = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        data = {"chat_id": TELEGRAM_CHAT_ID, "photo": whatsapp_media_url, "caption": f"De: {numero}\n{caption}"}
        requests.post(url_foto, data=data, timeout=15)
    except Exception as e:
        print(f"Error foto Telegram: {e}")
        enviar_a_telegram(f"📸 Foto de {numero} (no se pudo reenviar imagen, revisa WhatsApp Business). Caption: {caption}")

def enviar_ubicacion_a_telegram(numero, lat, lon, nombre=""):
    try:
        # 1. Mandar la ubicacion como mapa en Telegram
        url_loc = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendLocation"
        data = {"chat_id": TELEGRAM_CHAT_ID, "latitude": lat, "longitude": lon}
        requests.post(url_loc, data=data, timeout=10)
        
        # 2. Mandar texto con link de Google Maps
        maps_link = f"https://maps.google.com/?q={lat},{lon}"
        texto = f"📍 UBICACIÓN RECIBIDA\nDe: {numero}\nNombre: {nombre}\nLat: {lat}, Lon: {lon}\n\nGoogle Maps: {maps_link}\n\nPara responder: /responder {numero} Tu mensaje"
        enviar_a_telegram(texto, urgente=True)
    except Exception as e:
        print(f"Error ubicacion Telegram: {e}")

def get_whatsapp_media_url(media_id):
    try:
        # Paso 1: Obtener la URL real del archivo en los servidores de Meta
        url_meta = f"https://graph.facebook.com/v19.0/{media_id}/"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
        r = requests.get(url_meta, headers=headers, timeout=10)
        data = r.json()
        return data.get("url") # Esta URL es temporal y necesita el token para descargarse
    except Exception as e:
        print(f"Error get media url: {e}")
        return None

def enviar_whatsapp(numero, texto):
    try:
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        data = {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": texto}}
        requests.post(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(e)

MENSAJE_BIENVENIDA = """🚨 PROTECCIÓN CIVIL Y BOMBEROS DE GÓMEZ FARÍAS 🚒

Bienvenido(a) a nuestro asistente virtual.

📋 MENÚ PRINCIPAL

1️⃣ 🚨 Reportar una emergencia
2️⃣ 🔥 Incendios y prevención
3️⃣ 🌧️ Clima y recomendaciones
4️⃣ 🚑 Primeros auxilios
5️⃣ 🐕 Animales en la vía pública
6️⃣ 🚧 Accidentes y riesgos en carretera
7️⃣ 🏠 Seguridad en viviendas y negocios
8️⃣ 🎪 Eventos y medidas de seguridad
9️⃣ 📋 Programas Internos de Protección Civil
🔟 📞 Contactar a Protección Civil

También puedes enviar tu 📍 UBICACIÓN y 📸 FOTO para reportes.

Palabra clave: INCENDIO · CLIMA · ACCIDENTE · GAS · ANIMALES · EVENTO · UBICACION · FOTO"""

TEXTOS = {
    "1": "🚨 REPORTE DE EMERGENCIA\n📞 652-104-86-72\nProporciona: Ubicación exacta, qué ocurrió, personas, si hay incendio/riesgo. Puedes mandar tu UBICACIÓN por WhatsApp y FOTO del incidente.",
    "2_menu": "🔥 PREVENCIÓN DE INCENDIOS\n1 Extintores\n2 Tipos de fuego\n3 Prevención casa\n4 Prevención negocios\n5 Fugas gas LP\n6 Incendios forestales\nEscribe número. MENU para volver.",
    "2_1": "🧯 EXTINTORES: Retira seguro, apunta base fuego, presiona y zigzag. Verifica vigencia.",
    "2_2": "🔥 TIPOS FUEGO: A-Sólidos, B-Líquidos, C-Eléctricos, D-Metales, K-Aceites cocina.",
    "2_3": "🏠 PREVENCION CASA: No sobrecargues enchufes, apaga veladoras, gas ventilado, ten extintor.",
    "2_4": "🏢 PREVENCION NEGOCIOS: Extintores vigentes, rutas libres, instalación bien, capacitación.",
    "2_5": "⛽ FUGA GAS: No fuego/luces, abre ventanas, cierra válvula, llama 652-104-86-72.",
    "2_6": "🌲 FORESTALES: No fogatas, no colillas, reporta ubicación exacta. 652-104-86-72",
    "3": "🌦️ CLIMA: Ante clima severo resguárdate. Si quieres reporte, manda tu ubicación. 📞 652-104-86-72",
    "4_menu": "🚑 PRIMEROS AUXILIOS\n1 RCP\n2 Hemorragias\n3 Quemaduras\n4 Fracturas\n5 Desmayos\n6 Traumatismos\n7 Mordeduras\nEscribe número. 📞 652-104-86-72",
    "4_1": "❤️ RCP: Verifica inconsciencia, llama 652-104-86-72, 30 compresiones y 2 ventilaciones si estás capacitado.",
    "4_2": "🩸 HEMORRAGIAS: Presiona con tela limpia, no retires objetos, eleva y llama emergencias.",
    "4_3": "🔥 QUEMADURAS: Agua 10 min, no pasta dental, cubre gasa limpia.",
    "4_4": "🦴 FRACTURAS: No muevas, inmoviliza y llama 652-104-86-72.",
    "4_5": "😵 DESMAYOS: Acuesta, eleva pies, libera ropa.",
    "4_6": "🤕 TRAUMATISMOS: No muevas cabeza/cuello, controla sangrado.",
    "4_7": "🐍 MORDEDURAS: Lava, no succiones, identifica animal.",
    "5": "🐕 ANIMALES VIA PUBLICA: Pueden provocar accidentes. Mantén animales en espacio seguro. Si es reporte urgente manda UBICACIÓN y FOTO. 📞 652-104-86-72",
    "6": "🚧 CARRETERA: Mantente distancia segura, reduce velocidad, intermitentes, aléjate si incendio/fuga. Manda UBICACIÓN si es reporte. 📞 652-104-86-72",
    "7": "🏠 SEGURIDAD VIVIENDAS: Extintores, instalación eléctrica, gas LP, rutas evacuación. 📞 652-104-86-72",
    "8": "🎪 EVENTOS: Control aforo, rutas emergencia, extintores, atención emergencias. 📞 652-104-86-72",
    "9": "📋 PROGRAMA INTERNO: Programa Interno, plan emergencia, rutas, brigadas, capacitación. 📞 652-104-86-72",
    "10": "🛡️ CONTACTO PC GÓMEZ FARÍAS\n📞 652-104-86-72\nEscribe HABLAR CON ALGUIEN para persona.",
    "no_entiendo": "⚠️ No identifiqué tu solicitud. Escribe MENU. Puedes mandar UBICACIÓN y FOTO para reportes. 📞 652-104-86-72",
    "gracias": "👍 Gracias por comunicarte con Protección Civil Gómez Farías. 🛡️🚒\n📞 652-104-86-72"
}

MAPA_TEMAS = {
    "1": "🚨 1-REPORTAR EMERGENCIA", "2": "🔥 2-INCENDIOS", "2_1": "🔥 2.1-Extintores", "2_2": "🔥 2.2-Tipos fuego",
    "2_3": "🔥 2.3-Prev casa", "2_4": "🔥 2.4-Prev negocios", "2_5": "⛽ 2.5-Fuga gas", "2_6": "🌲 2.6-Forestal",
    "3": "🌧️ 3-CLIMA", "4": "🚑 4-AUXILIOS", "5": "🐕 5-ANIMALES", "6": "🚧 6-CARRETERA",
    "7": "🏠 7-VIVIENDAS", "8": "🎪 8-EVENTOS", "9": "📋 9-PROGRAMAS", "10": "📞 10-CONTACTAR",
    "ubicacion": "📍 UBICACION ENVIADA", "foto": "📸 FOTO ENVIADA"
}

PALABRAS_HUMANO = ["hablar con alguien","mensajear con alguien","hablar con una persona","quiero hablar","operador","humano","persona real","asesor"]

def obtener_respuesta(numero, texto_original):
    texto = texto_original.strip().lower()
    estado = user_state.get(numero, "menu")
    if texto in ["menu","inicio","ayuda","hola","buenas","start"]:
        user_state[numero]="menu"
        return "menu", MENSAJE_BIENVENIDA
    if "gracias" in texto: return "gracias", TEXTOS["gracias"]
    if any(p in texto for p in PALABRAS_HUMANO): return "humano", "HUMANO"
    if any(x in texto for x in ["emergencia","urgente","rescate"]): return "1", TEXTOS["1"]
    if "clima" in texto: return "3", TEXTOS["3"]
    if "incendio" in texto and "forestal" in texto: return "2_6", TEXTOS["2_6"]
    if "incendio" in texto or "fuego" in texto: user_state[numero]="incendios"; return "2", TEXTOS["2_menu"]
    if "gas" in texto or "fuga" in texto: return "2_5", TEXTOS["2_5"]
    if "extintor" in texto: return "2_1", TEXTOS["2_1"]
    if "primeros auxilios" in texto or "rcp" in texto: user_state[numero]="auxilios"; return "4", TEXTOS["4_menu"]
    if "animal" in texto or "perro" in texto or "vaca" in texto or "caballo" in texto or "ganado" in texto: return "5", TEXTOS["5"]
    if "accidente" in texto or "choque" in texto or "volcadura" in texto or "carretera" in texto: return "6", TEXTOS["6"]
    if "casa" in texto or "negocio" in texto: return "7", TEXTOS["7"]
    if "evento" in texto or "feria" in texto: return "8", TEXTOS["8"]
    if "programa interno" in texto or "pipc" in texto or "brigada" in texto: return "9", TEXTOS["9"]
    if "contactar" in texto or "proteccion civil" in texto or "bomberos" in texto: return "10", TEXTOS["10"]
    if estado=="menu":
        if texto=="1": return "1", TEXTOS["1"]
        elif texto=="2": user_state[numero]="incendios"; return "2", TEXTOS["2_menu"]
        elif texto=="3": return "3", TEXTOS["3"]
        elif texto=="4": user_state[numero]="auxilios"; return "4", TEXTOS["4_menu"]
        elif texto=="5": return "5", TEXTOS["5"]
        elif texto=="6": return "6", TEXTOS["6"]
        elif texto=="7": return "7", TEXTOS["7"]
        elif texto=="8": return "8", TEXTOS["8"]
        elif texto=="9": return "9", TEXTOS["9"]
        elif texto=="10": return "10", TEXTOS["10"]
    elif estado=="incendios":
        if texto in ["1","2","3","4","5","6"]: return f"2_{texto}", TEXTOS[f"2_{texto}"]
        else: return "2", TEXTOS["2_menu"]
    elif estado=="auxilios":
        if texto in ["1","2","3","4","5","6","7"]: return f"4_{texto}", TEXTOS[f"4_{texto}"]
        else: return "4", TEXTOS["4_menu"]
    return "no", TEXTOS["no_entiendo"]

@app.route('/')
def home(): return "Bot Oficial PC Gomez Farias - Activo con ubicacion y foto"

@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.verify_token")==VERIFY_TOKEN:
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
                tipo = msg.get("type")
                ultimo_numero["numero"]=numero

                # --- CASO 1: UBICACION ---
                if tipo == "location":
                    loc = msg.get("location", {})
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    nombre = loc.get("name","") or loc.get("address","")
                    print(f"Ubicacion de {numero}: {lat},{lon}")
                    enviar_ubicacion_a_telegram(numero, lat, lon, nombre)
                    enviar_whatsapp(numero, f"📍 Gracias por compartir tu ubicación.\n\nLa hemos recibido: {lat}, {lon}\nUn operador de Protección Civil la está revisando. Si es emergencia llama directo:\n📞 652-104-86-72\n\nSi puedes, envía también una foto del incidente.")
                    return "OK", 200

                # --- CASO 2: FOTO / IMAGEN ---
                if tipo == "image":
                    image = msg.get("image", {})
                    media_id = image.get("id")
                    caption = image.get("caption","")
                    print(f"Foto de {numero}: {media_id} caption: {caption}")
                    
                    media_url = get_whatsapp_media_url(media_id)
                    
                    # Telegram necesita descargar la foto con token, asi que le pasamos la URL y le avisamos
                    # Si la URL directa falla, mandamos al menos el aviso
                    if media_url:
                        # Para que Telegram pueda bajarla, necesitamos reenviar con el token de WhatsApp como header no funciona directo
                        # Asi que enviamos el link y tambien intentamos enviar la foto
                        # Truco: Descargamos nosotros y re-subimos a Telegram como archivo
                        try:
                            headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                            img_data = requests.get(media_url, headers=headers, timeout=15).content
                            # Subir a Telegram
                            url_upload = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
                            files = {'photo': ('reporte.jpg', img_data)}
                            data_tg = {'chat_id': TELEGRAM_CHAT_ID, 'caption': f"📸 FOTO de {numero}\nCaption: {caption}\n\n/responder {numero} Tu mensaje"}
                            requests.post(url_upload, data=data_tg, files=files, timeout=15)
                            enviar_a_telegram(f"📸 Foto recibida de {numero} - Tema: {caption if caption else 'Sin descripcion'}")
                        except Exception as e:
                            print(f"Error reenviando foto: {e}")
                            enviar_foto_a_telegram(numero, media_url, caption)
                    else:
                        enviar_a_telegram(f"📸 FOTO de {numero} recibida pero no se pudo obtener URL. Caption: {caption}", urgente=True)

                    enviar_whatsapp(numero, "📸 Foto recibida. Gracias por el reporte.\n\nLa estamos revisando en Protección Civil Gómez Farías. Si es emergencia, comparte también tu ubicación y llama:\n📞 652-104-86-72")
                    return "OK", 200

                # --- CASO 3: TEXTO NORMAL ---
                if tipo == "text":
                    texto = msg.get("text", {}).get("body", "")
                    codigo, respuesta = obtener_respuesta(numero, texto)
                    tema_legible = MAPA_TEMAS.get(codigo, codigo)

                    if respuesta == "HUMANO":
                        enviar_a_telegram(f"🚨 ALERTA HUMANA 🚨\n\nDe: {numero}\nMensaje: {texto}\n\nQuiere hablar con persona. Numero: {numero}", urgente=True)
                        enviar_whatsapp(numero, "✅ Te conecto con un operador de Protección Civil Gómez Farías. En un momento te atiende una persona. Mantente en el chat.\n\n📞 652-104-86-72")
                    else:
                        mensaje_telegram = (
                            f"📩 *WhatsApp Nuevo*\n"
                            f"De: {numero}\n"
                            f"Escribio: {texto}\n"
                            f"Tema: {tema_legible}\n\n"
                            f"🤖 Bot contesto:\n{respuesta}\n\n"
                            f"Para responder: /responder {numero} Tu mensaje"
                        )
                        enviar_a_telegram(mensaje_telegram)
                        enviar_whatsapp(numero, respuesta)

    except Exception as e:
        print(f"Error: {e}")
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
                if len(partes)==3:
                    enviar_whatsapp(partes[1], partes[2])
                    enviar_a_telegram(f"✅ Enviado a {partes[1]}: {partes[2]}")
                elif len(partes)==2 and "numero" in ultimo_numero:
                    enviar_whatsapp(ultimo_numero["numero"], partes[1])
                    enviar_a_telegram(f"✅ Enviado a {ultimo_numero['numero']}: {partes[1]}")
            else:
                if "numero" in ultimo_numero:
                    enviar_whatsapp(ultimo_numero["numero"], texto)
                    enviar_a_telegram(f"✅ Enviado a {ultimo_numero['numero']}: {texto}")
    except Exception as e:
        print(e)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
