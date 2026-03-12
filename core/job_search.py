import re
import time
import urllib.parse

import pandas as pd
from selenium.webdriver.common.by import By

from config import GEOIDS
from core.browser import iniciar_driver, login_proceso


def run_job_search(email, password, job_key, pais_seleccionado, save_callback, log_fn=None, stop_event=None):
    """
    Busca vacantes de empleo en LinkedIn.
    stop_event: threading.Event — si se activa, el proceso para limpiamente.
    """
    def parado():
        return stop_event is not None and stop_event.is_set()

    driver = iniciar_driver()
    if not driver:
        return

    try:
        if not login_proceso(driver, email, password, log_fn):
            return

        nombre_pais_en, geo_id = GEOIDS[pais_seleccionado]

        url_busqueda = (
            f"https://www.linkedin.com/jobs/search/?"
            f"keywords={urllib.parse.quote(job_key)}"
            f"&geoId={geo_id}"
            f"&location={urllib.parse.quote(nombre_pais_en)}"
            f"&f_WT=1%2C3"
            f"&sortBy=DD"
        )

        if log_fn:
            log_fn(f"Buscando '{job_key}' en {pais_seleccionado}...")
        driver.get(url_busqueda)
        time.sleep(5)

        if parado():
            if log_fn:
                log_fn("Proceso detenido por el usuario.")
            return

        # Scroll dinámico
        try:
            panel = None
            for selector in [".jobs-search-results-list", ".scaffold-layout__list-container", "main"]:
                try:
                    panel = driver.find_element(By.CSS_SELECTOR, selector)
                    if panel.is_displayed():
                        break
                except Exception:
                    continue

            if panel:
                for i in range(5):
                    if parado():
                        break
                    if log_fn:
                        log_fn(f"Scroll en panel de resultados ({i + 1}/5)...")
                    driver.execute_script("arguments[0].scrollTop += 1000;", panel)
                    time.sleep(1.5)
        except Exception:
            pass

        if parado():
            if log_fn:
                log_fn("Proceso detenido por el usuario.")
            return

        cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'job-card-container')]")
        if log_fn:
            log_fn(f"Analizando {len(cards)} tarjetas encontradas...")

        resultados = []
        palabras_basura = ["Inicio", "Notificaciones", "Mensajes", "Mi red", "Empleos", "Premium"]

        for card in cards:
            if parado():
                if log_fn:
                    log_fn("Proceso detenido por el usuario.")
                break

            try:
                driver.execute_script("arguments[0].scrollIntoView();", card)
                card.click()
                time.sleep(2)

                link_el = card.find_element(By.XPATH, ".//a[contains(@href, '/jobs/view/')]")
                url_job = link_el.get_attribute("href").split("?")[0]
                lineas = card.text.split('\n')
                titulo = lineas[0].strip()
                empresa = lineas[2] if len(lineas) > 2 else "N/A"
                ubicacion_texto = lineas[3] if len(lineas) > 3 else "N/A"

                reclutador = "Anónimo"
                try:
                    reclutador_el = driver.find_element(
                        By.CSS_SELECTOR, ".jobs-poster__name, .app-aware-link.jobs-poster__name"
                    )
                    reclutador = reclutador_el.text.strip()
                except Exception:
                    pass

                email_detectado = "No encontrado"
                try:
                    descripcion = driver.find_element(By.ID, "job-details").text
                    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', descripcion)
                    if emails:
                        email_detectado = ", ".join(list(set(emails)))
                except Exception:
                    pass

                modalidad = "No especificada"
                try:
                    info_empleo = driver.find_element(
                        By.CLASS_NAME, "jobs-unified-top-card__job-insight"
                    ).text
                    if any(x in info_empleo for x in ["Híbrido", "Hybrid"]):
                        modalidad = "Híbrido"
                    elif any(x in info_empleo for x in ["Presencial", "On-site"]):
                        modalidad = "Presencial"
                    elif any(x in info_empleo for x in ["Remoto", "Remote"]):
                        modalidad = "Remoto"
                except Exception:
                    pass

                if not any(pb in titulo for pb in palabras_basura):
                    resultados.append({
                        "Puesto": titulo,
                        "Empresa": empresa,
                        "Ubicación": ubicacion_texto,
                        "Modalidad": modalidad,
                        "Reclutador": reclutador,
                        "Email": email_detectado,
                        "Link": url_job,
                    })
                    if log_fn:
                        log_fn(f"Extraído: {titulo} en {empresa}")

            except Exception:
                continue

        if resultados:
            df = pd.DataFrame(resultados).drop_duplicates(subset=['Link'])
            if pais_seleccionado != "Reino Unido":
                df = df[~df['Ubicación'].str.contains(
                    'United Kingdom|Reino Unido|London', case=False, na=False
                )]

            if not df.empty:
                save_callback(df, pais_seleccionado)
            else:
                if log_fn:
                    log_fn("No quedaron resultados tras filtrar por ubicación.")
        else:
            if log_fn:
                log_fn("No se detectaron vacantes válidas.")

    finally:
        driver.quit()
        if log_fn:
            log_fn("Navegador cerrado.")