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


def buscar_y_clicar_js(driver, palabras_clave, intentar_clic=True):
    """
    Escanea el DOM buscando botones/elementos que coincidan con las palabras clave.
    Usa lógica robusta para encontrar spans dentro de botones.
    """
    script = """
        var keywords = arguments[0];
        var click = arguments[1];
        var selectores = "button, span, a, [role='button']";
        var elementos = document.querySelectorAll(selectores);

        for (var i = 0; i < elementos.length; i++) {
            var el = elementos[i];
            if (!(el.offsetWidth > 0 && el.offsetHeight > 0)) continue;

            var txt = (el.innerText || "").toLowerCase().trim();
            var aria = (el.getAttribute("aria-label") || "").toLowerCase().trim();
            var title = (el.getAttribute("title") || "").toLowerCase().trim();

            for (var j = 0; j < keywords.length; j++) {
                var kw = keywords[j].toLowerCase().trim();
                if (txt.includes(kw) || aria.includes(kw) || title.includes(kw)) {
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
        return driver.execute_script(script, palabras_clave, intentar_clic)
    except Exception as e:
        print(f"Error en JS: {e}")
        return False
