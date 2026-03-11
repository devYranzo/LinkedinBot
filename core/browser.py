import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def iniciar_driver():
    """Inicia el navegador Chrome sin detección de automatización."""
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    try:
        return uc.Chrome(options=options)
    except Exception:
        options = uc.ChromeOptions()
        options.add_argument("--window-size=1280,900")
        return uc.Chrome(options=options, version_main=145)


def login_proceso(driver, email, password, log_fn=None):
    """Realiza el login en LinkedIn. Retorna True si tuvo éxito."""
    if not email or not password:
        if log_fn:
            log_fn("Error: Falta Email o Password")
        return False

    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    try:
        driver.find_element(By.ID, "username").send_keys(email)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
        if "checkpoint" in driver.current_url:
            if log_fn:
                log_fn("Resuelve el CAPTCHA en el navegador...")
            WebDriverWait(driver, 60).until(ec.url_contains("feed"))
        return True
    except Exception as e:
        if log_fn:
            log_fn(f"Error Login: {e}")
        return False


def buscar_y_clicar_js(driver, palabras_clave, intentar_clic=True, exacto=False):
    """
    Escanea el DOM buscando botones/elementos que coincidan con las palabras clave.
    - exacto=False (por defecto): usa includes, igual que antes.
    - exacto=True: coincidencia exacta sobre el texto visible del elemento.
    """
    script = """
        var keywords    = arguments[0];
        var click       = arguments[1];
        var exactMatch  = arguments[2];
        var selectores  = "button, span, a, [role='button']";
        var elementos   = document.querySelectorAll(selectores);

        for (var i = 0; i < elementos.length; i++) {
            var el = elementos[i];
            if (!(el.offsetWidth > 0 && el.offsetHeight > 0)) continue;

            var txt   = (el.innerText              || "").toLowerCase().trim();
            var aria  = (el.getAttribute("aria-label") || "").toLowerCase().trim();
            var title = (el.getAttribute("title")      || "").toLowerCase().trim();

            for (var j = 0; j < keywords.length; j++) {
                var kw = keywords[j].toLowerCase().trim();
                var matched = exactMatch
                    ? (txt === kw || aria === kw || title === kw)
                    : (txt.includes(kw) || aria.includes(kw) || title.includes(kw));

                if (matched) {
                    if (click) {
                        var target = (el.tagName.toLowerCase() === 'span' && el.parentElement) ? el.parentElement : el;
                        target.scrollIntoView({behavior: "auto", block: "center"});
                        target.click();
                    }
                    return true;
                }
            }
        }
        return false;
    """
    try:
        return driver.execute_script(script, palabras_clave, intentar_clic, exacto)
    except Exception as e:
        print(f"Error en JS: {e}")
        return False


def debe_saltar_perfil(driver):
    """
    Devuelve (True, motivo) si el perfil debe ignorarse, (False, "") si se puede conectar.

    Casos que provocan salto:
    - Ya conectados: aparece 'Mensaje'/'Message' y NO aparece 'Conectar'/'Connect'.
    - Conexiones desactivadas: aparece 'Seguir'/'Follow' y NO aparece 'Conectar'/'Connect'.

    Usa coincidencia EXACTA en el texto visible para evitar falsos positivos
    (ej: "Dejar de seguir", "Enviar mensaje", etc.).
    """
    script = """
        var conectKw  = ["conectar", "connect"];
        var seguirKw  = ["seguir", "follow"];
        var mensajeKw = ["mensaje", "message"];

        var selectores = "button, span, a, [role='button']";
        var elementos  = document.querySelectorAll(selectores);

        var hayConectar = false;
        var haySeguir   = false;
        var hayMensaje  = false;

        for (var i = 0; i < elementos.length; i++) {
            var el = elementos[i];
            if (!(el.offsetWidth > 0 && el.offsetHeight > 0)) continue;

            var txt = (el.innerText || "").toLowerCase().trim();

            for (var j = 0; j < conectKw.length; j++) {
                if (txt === conectKw[j]) hayConectar = true;
            }
            for (var k = 0; k < seguirKw.length; k++) {
                if (txt === seguirKw[k]) haySeguir = true;
            }
            for (var m = 0; m < mensajeKw.length; m++) {
                if (txt === mensajeKw[m]) hayMensaje = true;
            }
        }

        if (hayMensaje && !hayConectar) return "ya_conectado";
        if (haySeguir  && !hayConectar) return "solo_seguir";
        return "";
    """
    try:
        motivo = driver.execute_script(script)
        if motivo == "ya_conectado":
            return True, "ya estáis conectados (botón 'Mensaje' visible)"
        if motivo == "solo_seguir":
            return True, "conexiones desactivadas (solo aparece 'Seguir')"
        return False, ""
    except Exception as e:
        print(f"Error en debe_saltar_perfil: {e}")
        return False, ""