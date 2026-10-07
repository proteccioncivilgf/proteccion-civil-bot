import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "PC_GomezFarias")
WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8915682882:AAETJDNOamlw6XYjHcLi1sLxeeoYvFvLrfc")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7480300697")

# Memoria simple por numero para saber en que submenu esta
user_state = {}
ultimo_numero = {}

def enviar_a_telegram(texto, urgente=False):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        if urgente:
            texto = f"🚨🚨🚨 ALERTA HUMANA 🚨🚨🚨\n\n{texto}\n\n⚠️ QUIERE HABLAR CON UNA PERSONA"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": texto}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(e)

def enviar_whatsapp(numero, texto):
    try:
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}", "Content-Type": "application/json"}
        data = {"messaging_product": "whatsapp", "to": numero, "type": "text", "text": {"body": texto}}
        requests.post(url, headers=headers, json=data, timeout=10)
    except Exception as e:
        print(e)

# --- TEXTOS OFICIALES ---
MENSAJE_BIENVENIDA = """🚨 PROTECCIÓN CIVIL Y BOMBEROS DE GÓMEZ FARÍAS 🚒

Bienvenido(a) a nuestro asistente virtual.

Puedo ayudarte con información de prevención, seguridad, emergencias, clima y recomendaciones de Protección Civil.

📋 MENÚ PRINCIPAL

Escribe el número de la opción que necesitas:

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

También puedes escribir directamente una palabra clave, por ejemplo:

INCENDIO · CLIMA · ACCIDENTE · BOMBEROS · PRIMEROS AUXILIOS · ANIMALES · GAS · EXTINTOR · EVENTO"""

TEXTOS = {
    "1": """🚨 REPORTE DE EMERGENCIA

Para solicitar apoyo de Protección Civil y Bomberos de Gómez Farías, comunícate directamente:

📞 652-104-86-72

Al realizar tu reporte proporciona:

📍 Ubicación exacta
🚨 Qué ocurrió
👥 Número de personas involucradas
🔥 Si existe incendio o algún otro riesgo
⚠️ Cualquier condición que pueda poner en peligro a las personas o al personal de emergencia.

Si deseas hablar con una persona escribe: HABLAR CON ALGUIEN""",

    "2_menu": """🔥 PREVENCIÓN DE INCENDIOS

Selecciona una opción:

1 🧯 Uso y manejo de extintores
2 🔥 Tipos de fuego
3 🏠 Prevención de incendios en casa
4 🏢 Prevención en negocios
5 ⛽ Fugas de gas LP
6 🌲 Incendios forestales

Escribe el número de la opción.
Escribe MENU para volver al menú principal.""",

    "2_1": """🧯 USO Y MANEJO DE EXTINTORES

1. Retira el seguro.
2. Apunta a la base del fuego, no a las llamas.
3. Presiona la manija.
4. Haz movimientos en zigzag.

Recuerda: Verifica vigencia, presión y colócalo en lugar visible y señalizado.
📞 652-104-86-72""",

    "2_2": """🔥 TIPOS DE FUEGO

Clase A: Sólidos (madera, papel)
Clase B: Líquidos (gasolina, aceite)
Clase C: Eléctricos
Clase D: Metales
Clase K: Aceites de cocina

Usa el extintor correcto para cada tipo.""",

    "2_3": """🏠 PREVENCIÓN EN CASA

• No sobrecargues enchufes
• Apaga veladoras y estufas al salir
• Mantén gas LP en lugar ventilado
• Ten extintor y detector de humo
📞 652-104-86-72""",

    "2_4": """🏢 PREVENCIÓN EN NEGOCIOS

• Extintores vigentes y señalizados
• Rutas de evacuación libres
• Instalación eléctrica en buen estado
• Capacitación a personal
📞 652-104-86-72""",

    "2_5": """⛽ FUGAS DE GAS LP

Si huele a gas:
🚫 No enciendas luces ni fuego
🚪 Abre puertas y ventanas
🔧 Cierra la válvula
📞 Llama a Bomberos 652-104-86-72
Evacúa si es necesario.""",

    "2_6": """🌲 INCENDIOS FORESTALES

• No hagas fogatas en campo
• No tires colillas de cigarro
• Si ves incendio reporta ubicación exacta
📞 652-104-86-72
¡Prevenir es tarea de todos!""",

    "3": """🌦️ INFORMACIÓN METEOROLÓGICA

Puedo ayudarte con:

☀️ Temperatura
🌧️ Probabilidad de lluvia
💨 Viento
⛈️ Tormentas
❄️ Frentes fríos
🌡️ Temperaturas extremas
⚠️ Recomendaciones preventivas

Para reporte actualizado del clima en Gómez Farías escribe CLIMA y te compartimos recomendaciones.

Ante clima severo resguárdate en lugar seguro.
📞 652-104-86-72""",

    "4_menu": """🚑 PRIMEROS AUXILIOS

Selecciona:

1 ❤️ RCP
2 🩸 Hemorragias
3 🔥 Quemaduras
4 🦴 Fracturas
5 😵 Desmayos
6 🤕 Traumatismos
7 🐍 Mordeduras y picaduras

Escribe el número.
⚠️ Información orientativa. Ante situación grave llama a:
📞 652-104-86-72""",

    "4_1": "❤️ RCP: Verifica inconsciencia, llama al 652-104-86-72, 30 compresiones en centro del pecho y 2 ventilaciones. Solo si estás capacitado.",
    "4_2": "🩸 HEMORRAGIAS: Presiona con tela limpia, no retires objetos incrustados, eleva la zona y llama a emergencias.",
    "4_3": "🔥 QUEMADURAS: Enfría con agua 10 min, no uses pasta dental ni hielo directo, cubre con gasa limpia y busca atención médica.",
    "4_4": "🦴 FRACTURAS: No muevas el área, inmoviliza y llama a PC 652-104-86-72.",
    "4_5": "😵 DESMAYOS: Acuesta, eleva pies, libera ropa ajustada y verifica respiración.",
    "4_6": "🤕 TRAUMATISMOS: No muevas a la persona si hay golpe en cabeza/cuello, controla sangrado y llama a emergencias.",
    "4_7": "🐍 MORDEDURAS: Lava, no succiones, no hagas torniquete, identifica animal si es posible y acude a servicio médico.",

    "5": """🐕 ANIMALES EN LA VÍA PÚBLICA

Los animales sueltos pueden provocar:

🚗 Accidentes de tránsito
🐎 Accidentes con ganado
🐕 Ataques a peatones

Mantén a tus animales dentro de un espacio seguro y evita que permanezcan en calles y carreteras.

Para reportar:
📞 652-104-86-72""",

    "6": """🚧 SEGURIDAD EN CARRETERA

Si encuentras un accidente o riesgo:

⚠️ Mantente a distancia segura.
🚗 Reduce velocidad.
💡 Usa intermitentes.
🚫 No te coloques detrás o delante de vehículos accidentados.
🔥 Aléjate si hay riesgo de incendio o fuga.

📞 652-104-86-72""",

    "7": """🏠 SEGURIDAD Y PREVENCIÓN

Puedo orientarte sobre:

🧯 Extintores
🔥 Instalaciones eléctricas
⛽ Gas LP
🚪 Rutas de evacuación
🚨 Señalización
🧰 Botiquines
⚠️ Identificación de riesgos

📞 652-104-86-72""",

    "8": """🎪 SEGURIDAD EN EVENTOS

Considera:

👥 Control de aforo
🚪 Rutas y salidas de emergencia
🧯 Extintores
🚑 Atención a emergencias
⚡ Seguridad eléctrica
⛽ Manejo seguro de gas LP

📞 652-104-86-72""",

    "9": """📋 PROGRAMA INTERNO DE PROTECCIÓN CIVIL

Te orientamos sobre:

🏢 Programa Interno
🚨 Plan de emergencia
🗺️ Rutas de evacuación
📍 Señalización
🧯 Extintores
👥 Brigadas
🎓 Capacitación
📝 Simulacros

📞 652-104-86-72""",

    "10": """🛡️ PROTECCIÓN CIVIL Y BOMBEROS DE GÓMEZ FARÍAS

Para comunicarte directamente:

📞 652-104-86-72

Atendemos:

🔥 Incendios
🚑 Emergencias
🚧 Accidentes
🌧️ Fenómenos meteorológicos
🐕 Animales en riesgo
🏠 Situaciones de riesgo
🎪 Eventos

Escribe HABLAR CON ALGUIEN si quieres que te atienda una persona ahora.""",

    "no_entiendo": """⚠️ No pude identificar tu solicitud.

Escribe MENU para consultar las opciones disponibles.

También puedes comunicarte directamente con:

📞 Protección Civil y Bomberos de Gómez Farías
652-104-86-72""",

    "gracias": """👍 Gracias por comunicarte con Protección Civil y Bomberos de Gómez Farías. Estamos para servirte. 🛡️🚒

🛡️ Gracias por comunicarte con Protección Civil y Bomberos de Gómez Farías.
Tu seguridad y la prevención son responsabilidad de todos.
🚒 Protección Civil y Bomberos de Gómez Farías
📞 652-104-86-72"""
}

PALABRAS_HUMANO = ["hablar con alguien","mensajear con alguien","hablar con una persona","quiero hablar","operador","humano","persona real","asesor","atenderme una persona"]

def obtener_respuesta(numero, texto_original):
    texto = texto_original.strip().lower()
    estado = user_state.get(numero, "menu")

    # Comandos generales
    if texto in ["menu","inicio","ayuda","hola","buenas","buenos dias","buenas tardes","start"]:
        user_state[numero] = "menu"
        return MENSAJE_BIENVENIDA

    if texto in ["gracias","muchas gracias","thanks"]:
        return TEXTOS["gracias"]

    if any(p in texto for p in PALABRAS_HUMANO):
        return "HUMANO"

    # Palabras clave directas
    if any(x in texto for x in ["emergencia","urgente","ayuda","rescate"]):
        return TEXTOS["1"]
    if "clima" in texto or "lluvia" in texto or "tormenta" in texto or "viento" in texto or "frio" in texto or "calor" in texto:
        return TEXTOS["3"]
    if "incendio" in texto or "fuego" in texto or "extintor" in texto:
        user_state[numero] = "incendios"
        return TEXTOS["2_menu"]
    if "gas" in texto or "gas lp" in texto or "fuga" in texto:
        return TEXTOS["2_5"]
    if "primeros auxilios" in texto or "rcp" in texto or "herida" in texto or "sangrado" in texto or "quemadura" in texto:
        user_state[numero] = "auxilios"
        return TEXTOS["4_menu"]
    if "animal" in texto or "perro" in texto or "vaca" in texto or "caballo" in texto or "ganado" in texto:
        return TEXTOS["5"]
    if "accidente" in texto or "choque" in texto or "volcadura" in texto or "carretera" in texto:
        return TEXTOS["6"]
    if "casa" in texto or "negocio" in texto or "evacuacion" in texto:
        return TEXTOS["7"]
    if "evento" in texto or "feria" in texto or "baile" in texto or "rodeo" in texto:
        return TEXTOS["8"]
    if "programa interno" in texto or "pipc" in texto or "brigada" in texto or "simulacro" in texto:
        return TEXTOS["9"]
    if "contactar" in texto or "proteccion civil" in texto or "bomberos" in texto or "telefono" in texto:
        return TEXTOS["10"]

    # Manejo de numeros
    if estado == "menu":
        if texto == "1":
            return TEXTOS["1"]
        elif texto == "2":
            user_state[numero] = "incendios"
            return TEXTOS["2_menu"]
        elif texto == "3":
            return TEXTOS["3"]
        elif texto == "4":
            user_state[numero] = "auxilios"
            return TEXTOS["4_menu"]
        elif texto == "5":
            return TEXTOS["5"]
        elif texto == "6":
            return TEXTOS["6"]
        elif texto == "7":
            return TEXTOS["7"]
        elif texto == "8":
            return TEXTOS["8"]
        elif texto == "9":
            return TEXTOS["9"]
        elif texto == "10":
            return TEXTOS["10"]

    elif estado == "incendios":
        if texto == "1": return TEXTOS["2_1"]
        elif texto == "2": return TEXTOS["2_2"]
        elif texto == "3": return TEXTOS["2_3"]
        elif texto == "4": return TEXTOS["2_4"]
        elif texto == "5": return TEXTOS["2_5"]
        elif texto == "6": return TEXTOS["2_6"]
        else: return TEXTOS["2_menu"]

    elif estado == "auxilios":
        if texto == "1": return TEXTOS["4_1"]
        elif texto == "2": return TEXTOS["4_2"]
        elif texto == "3": return TEXTOS["4_3"]
        elif texto == "4": return TEXTOS["4_4"]
        elif texto == "5": return TEXTOS["4_5"]
        elif texto == "6": return TEXTOS["4_6"]
        elif texto == "7": return TEXTOS["4_7"]
        else: return TEXTOS["4_menu"]

    return TEXTOS["no_entiendo"]

@app.route('/')
def home():
    return "Bot Oficial Proteccion Civil Gomez Farias - Activo"

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
                ultimo_numero["numero"] = numero

                # Reenviar copia a Telegram siempre
                enviar_a_telegram(f"📩 WhatsApp {numero}: {texto}")

                respuesta = obtener_respuesta(numero, texto)

                if respuesta == "HUMANO":
                    enviar_a_telegram(f"De: {numero}\nQuiere hablar con humano: {texto}\nNumero: {numero}", urgente=True)
                    enviar_whatsapp(numero, "✅ Te conecto con un operador de Protección Civil Gómez Farías. En un momento te atiende una persona. Por favor mantente en el chat.\n\n📞 Emergencias directas: 652-104-86-72")
                else:
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
                if len(partes) == 3:
                    enviar_whatsapp(partes[1], partes[2])
                    enviar_a_telegram(f"✅ Enviado a {partes[1]}: {partes[2]}")
                elif len(partes) == 2 and "numero" in ultimo_numero:
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
