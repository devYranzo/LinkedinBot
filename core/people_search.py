import os
import re
import time
import urllib.parse

import pandas as pd
from selenium.webdriver.common.by import By

from core.browser import iniciar_driver, login_proceso


def run_people_search(email, password, keyword, paginas, ruta_guardado, log_fn=None):
    """
    Busca perfiles de personas en LinkedIn y guarda los resultados en un CSV.
    """
    driver = iniciar_driver()
    if not driver:
        return

    try:
        if not login_proceso(driver, email, password, log_fn):
            return

        leads_finales = []
        enlaces_vistos = set()

        for p in range(1, paginas + 1):
            url = (f"https://www.linkedin.com/search/results/people/?"
                   f"keywords={urllib.parse.quote(keyword)}&page={p}")

            if log_fn:
                log_fn(f"Escaneando página {p} de {paginas}...")
            driver.get(url)
            time.sleep(5)

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            items = driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")
            if log_fn:
                log_fn(f"Detectados {len(items)} elementos en la página.")

            for item in items:
                try:
                    enlace_el = item.find_element(
                        By.CSS_SELECTOR, "a[data-view-name='search-result-lockup-title']"
                    )
                    link = enlace_el.get_attribute("href").split("?")[0]

                    if link in enlaces_vistos:
                        continue
                    nombre = enlace_el.text.strip()

                    parrafos = item.find_elements(By.TAG_NAME, "p")
                    cargo = "N/A"
                    ubicacion = "N/A"
                    empresa_solo = "N/A"
                    textos_secundarios = []

                    for p_tag in parrafos:
                        txt = p_tag.text.strip()
                        if not txt or txt == nombre or "Conectar" in txt:
                            continue
                        if "Actual:" in txt:
                            frase = txt.replace("Actual:", "").strip()
                            partes = re.split(r'\s+en\s+|\s+at\s+|\s+@\s+', frase, flags=re.IGNORECASE)
                            empresa_solo = partes[-1].strip() if len(partes) > 1 else frase
                        else:
                            textos_secundarios.append(txt)

                    if len(textos_secundarios) > 1:
                        cargo = textos_secundarios[1]
                    if len(textos_secundarios) > 2:
                        ubicacion = textos_secundarios[2]

                    if len(nombre) > 2:
                        leads_finales.append({
                            "Nombre Completo": nombre,
                            "Cargo": cargo,
                            "Empresa": empresa_solo,
                            "Ubicación": ubicacion,
                            "Perfil LinkedIn": link,
                        })
                        enlaces_vistos.add(link)
                except Exception:
                    continue

        if leads_finales:
            df = pd.DataFrame(leads_finales)
            nombre_archivo = f"Leads_{keyword.replace(' ', '_')}.csv"
            ruta_final = os.path.join(ruta_guardado, nombre_archivo)
            df.to_csv(ruta_final, index=False, encoding='utf-8-sig')

            if log_fn:
                log_fn(f"¡Hecho! {len(df)} perfiles únicos guardados.")
                log_fn(f"Guardado: {nombre_archivo}")
        else:
            if log_fn:
                log_fn("No se capturaron datos. Revisa el navegador.")

    finally:
        driver.quit()
        if log_fn:
            log_fn("Sesión de búsqueda finalizada.")
