import time, os, psutil, random, gc
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.firefox import GeckoDriverManager

LINKS = [
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14099640Psd5ckztbxxpsp3mr80g&balance=0&currency=PEN&userid=14050994&isMobile=false",
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14099703Ptvek8xix3bv72oyabvu&balance=0&currency=PEN&userid=14051057&isMobile=false",
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14099777Pf29hvqzft6wzapuiqwc&balance=0&currency=PEN&userid=14051130&isMobile=false",
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14099906P6ochlhra28j8sisenry&balance=0&currency=PEN&userid=14051258&isMobile=false",
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14099976P7vs7rigibl8ssrlhtgy&balance=0&currency=PEN&userid=14051328&isMobile=false",
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14100055P9pwbojk1rly70mkpwm2&balance=0&currency=PEN&userid=14051407&isMobile=false",
    "https://casino.virtualsoft.tech/game/play/?gameid=70514&mode=real&provider=undefined&lan=es&partnerid=0&token=0P14100116Pz4oorga6cd91qz8oxuc&balance=0&currency=PEN&userid=14051468&isMobile=false"
]

PLANTILLA_BASE = "Quieres ganar Mas de 2mil en 45 minutos Escribeme al Whatsapp😍⚓+𝟓𝟐 𝟕𝟕𝟑𝟐𝟔𝟕𝟑𝟓𝟓𝟓 ⚓𝚝elegram⚓ 𝙰𝚅𝙸𝙰𝚃𝙾𝚁𝙿𝙺𝙰 sin cobros adelantados⚓⛺⚓⛳⚓😘VAR_3"
EMOJIS_POOL = list("😎😷😋😍😘😝😉😙🤓🔥💧👸😏🤑🤗👊✊👍💥👌👈👇👆👉👅👄🤘🙆💆💙💜💛💚👑🎩🙋💃🐽💗💌🤖🐺🐶💎🐦🐤🐥🐞🦄🐠🦀🦁🐼🐴🐒🐵➗🌹🌻🍄💐🌵🐩💵🎁💰")

historial_enviados = set()

def generar_mensaje_unico():
    global historial_enviados
    if len(historial_enviados) >= 10000: 
        historial_enviados.clear()
        
    for _ in range(5000):
        e1 = random.choice(EMOJIS_POOL)
        e2 = random.choice(EMOJIS_POOL)
        e3 = random.choice(EMOJIS_POOL)
        ultimos_tres = e1 + e2 + e3
        
        msg_final = PLANTILLA_BASE.replace("VAR_3", ultimos_tres)
        
        if msg_final not in historial_enviados:
            historial_enviados.add(msg_final)
            return msg_final
            
    return PLANTILLA_BASE.replace("VAR_3", "🔥💧👸")

def limpiar_especifico(pid):
    try:
        p = psutil.Process(pid)
        for hijo in p.children(recursive=True): hijo.kill()
        p.kill()
    except: pass
    gc.collect()

def iniciar():
    opt = Options()
    opt.add_argument("-headless")
    opt.set_preference("browser.cache.disk.enable", False)
    opt.set_preference("browser.cache.memory.enable", False)
    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=opt)
    try: driver.set_window_size(1920, 1080)
    except: pass
    return driver

def buscar_campo_texto(dr):
    try:
        caja = dr.find_elements(By.TAG_NAME, "textarea")
        if not caja: caja = dr.find_elements(By.CSS_SELECTOR, "input[type='text'], [contenteditable='true'], .chat-input, .message-input")
        if caja: return caja[0]
        iframes = dr.find_elements(By.TAG_NAME, "iframe")
        for frame in iframes:
            try:
                dr.switch_to.frame(frame)
                caja = dr.find_elements(By.TAG_NAME, "textarea")
                if not caja: caja = dr.find_elements(By.CSS_SELECTOR, "input[type='text'], [contenteditable='true'], .chat-input, .message-input")
                if caja: return caja[0]
                sub_caja = buscar_campo_texto(dr)
                if sub_caja: return sub_caja
                dr.switch_to.parent_frame()
            except:
                try: dr.switch_to.default_content()
                except: pass
    except: pass
    return None

def abrir_y_verificar_tags_todos(dr):
    print("⏳ [PLAY1 - HEADLESS] Abriendo y preparando todos los chats en segundo plano...", flush=True)
    handles = []
    for i, url in enumerate(LINKS):
        if i == 0:
            dr.get(url)
        else:
            dr.execute_script(f"window.open('{url}', '_blank');")
            time.sleep(0.5)
        
        pestanas = dr.window_handles
        current_handle = pestanas[-1]
        handles.append(current_handle)
        dr.switch_to.window(current_handle)
        
        listo = False; intentos = 0
        while not listo and intentos < 12:
            dr.switch_to.default_content()
            if buscar_campo_texto(dr):
                listo = True
                break
            time.sleep(1); intentos += 1
        time.sleep(1)
    
    dr.switch_to.default_content()
    return handles

def disparar_con_protocolo_seguro(dr, handle, idx, msg):
    try:
        dr.switch_to.window(handle)
        dr.switch_to.default_content()
        target = buscar_campo_texto(dr)
        
        if target:
            try: target.click()
            except: pass
            
            try:
                target.send_keys(Keys.CONTROL + "a")
                target.send_keys(Keys.BACKSPACE)
            except: pass
            
            target.send_keys(msg)
            
            val_actual = target.get_attribute("value") or target.text
            if not val_actual or len(val_actual) < 10:
                dr.execute_script("arguments[0].value = arguments[1];", target, msg)
            
            target.send_keys(Keys.ENTER)
            return True
    except:
        pass
    finally:
        try: dr.switch_to.default_content()
        except: pass
    return False

def run():
    dr = iniciar()
    pid = dr.service.process.pid
    total_disparos_global = 0
    MAX_DISPAROS_CICLO = 1200
    
    try:
        handles = abrir_y_verificar_tags_todos(dr)
        num_tags = len(handles)
        
        proximo_disparo_por_tag = {i: 0.0 for i in range(num_tags)}
        
        print(f"\n🚀 [PLAY1 ACTIONS] INICIANDO RACHAS INTELIGENTES ({num_tags} chats activos)...", flush=True)
        
        while total_disparos_global < MAX_DISPAROS_CICLO:
            ahora = time.time()
            disparo_realizado_en_iteracion = False
            
            for idx in range(num_tags):
                if total_disparos_global >= MAX_DISPAROS_CICLO:
                    break
                
                if ahora >= proximo_disparo_por_tag[idx]:
                    msg = generar_mensaje_unico()
                    
                    if disparar_con_protocolo_seguro(dr, handles[idx], idx, msg):
                        total_disparos_global += 1
                        disparo_realizado_en_iteracion = True
                        print(f"    ⚡ [PLAY1] Chat #{idx+1} enviado | Total ciclo: {total_disparos_global}/{MAX_DISPAROS_CICLO}", flush=True)
                        
                        proximo_disparo_por_tag[idx] = time.time() + 5.0
            
            if not disparo_realizado_en_iteracion:
                time.sleep(0.1)
        
        print(f"\n🎯 [PLAY1] META DE {MAX_DISPAROS_CICLO} ALCANZADA.", flush=True)
        
    except Exception as e:
        print(f"⚠️ [PLAY1] Error en ejecución: {e}", flush=True)
    finally:
        try: dr.quit()
        except: pass
        limpiar_especifico(pid)
        historial_enviados.clear()
        gc.collect()
        print("🔄 [PLAY1] Ciclo finalizado correctamente en GitHub Actions.\n", flush=True)

if __name__ == "__main__": 
    run()
