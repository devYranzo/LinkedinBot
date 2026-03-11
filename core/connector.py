import csv
import time
import random

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from core.browser import iniciar_driver, login_proceso, buscar_y_clicar_js, debe_saltar_perfil


def run_csv_process(email, password, ruta_csv, log_fn=None):
    """
    Proceso principal de conexión masiva desde un archivo CSV.
    Cada fila debe tener una columna de URL y opcionalmente de nombre.
    """
    if log_fn:
        log_fn("Iniciando navegador para conectar...")

    driver = iniciar_driver()
    if not driver:
        return

    try:
        if not login_proceso(driver, email, password, log_fn):
            return

        if log_fn:
            log_fn("Login exitoso. Procesando lista...")

        with open(ruta_csv, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for fila in reader:
                if not any(fila.values()):
                    continue

                url = (fila.get('url') or fila.get('Link') or
                       fila.get('URL') or fila.get('Perfil LinkedIn'))
                nombre = (fila.get('full_name') or fila.get('Nombre') or
                          fila.get('Nombre Completo') or "Contacto")

                if not url or "http" not in str(url):
                    if log_fn:
                        log_fn("Saltando fila: URL no válida.")
                    continue

                if log_fn:
                    log_fn(f"Visitando a: {nombre}")
                driver.get(url)
                time.sleep(random.uniform(5, 7))

                # Guardia: saltar si ya estamos conectados o las conexiones están desactivadas
                saltar, motivo = debe_saltar_perfil(driver)
                if saltar:
                    if log_fn:
                        log_fn(f"Saltando a {nombre}: {motivo}.")
                    continue

                # Paso 1: Clic en 'Conectar' con coincidencia EXACTA para no
                # confundirse con textos de publicaciones que contengan esa palabra
                conectado = buscar_y_clicar_js(driver, ["conectar", "connect"], exacto=True)

                if not conectado:
                    if log_fn:
                        log_fn("Buscando en menú 'Más'...")
                    if buscar_y_clicar_js(driver, ["más...", "more...", "más"]):
                        time.sleep(1.5)
                        conectado = buscar_y_clicar_js(driver, ["conectar", "connect"], exacto=True)

                # Paso 2: Confirmación final por navegación TAB
                if conectado:
                    if log_fn:
                        log_fn("Modal detectada. Navegando con TAB al botón...")
                    time.sleep(3.5)

                    try:
                        actions = ActionChains(driver)
                        for _ in range(3):
                            actions.send_keys(Keys.TAB)
                            time.sleep(0.5)
                        actions.send_keys(Keys.ENTER)
                        actions.perform()

                        time.sleep(0.5)
                        actions.send_keys(Keys.SPACE)
                        actions.perform()

                        if log_fn:
                            log_fn("Comandos de Tabulación + Enter enviados.")

                    except Exception as e:
                        if log_fn:
                            log_fn(f"Fallo en navegación TAB: {str(e)}")
                        try:
                            ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                        except Exception:
                            pass

                    time.sleep(4)

                espera = random.uniform(10, 18)
                if log_fn:
                    log_fn(f"Esperando {int(espera)}s para el siguiente...")
                time.sleep(espera)

        if log_fn:
            log_fn("Proceso de CSV finalizado.")

    except Exception as e:
        if log_fn:
            log_fn(f"Error crítico: {str(e)}")
    finally:
        driver.quit()
        if log_fn:
            log_fn("Sesión cerrada.")