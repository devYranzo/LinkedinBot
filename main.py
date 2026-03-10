import csv
import json
import os
import random
import re
import threading
import time
import urllib.parse
from tkinter import filedialog

import customtkinter as ctk
import keyring
import pandas as pd
import undetected_chromedriver as uc
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys

# --- Configuration ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

GEOIDS = {"Malta": ("Malta", "102126540"), "España": ("Spain", "105646813"), }


class LinkedInBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.entry_csv_path = None
        self.title("LinkedIn Bot")
        self.geometry("1100x750")

        # 1. Definir variables de estado
        self.config_file = "config.json"
        self.ruta_guardado = os.getcwd()
        self.email_guardado = ""

        # 2. Cargar datos del archivo
        self.cargar_configuracion()

        # 3. Configuración del Grid Principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR (Columna 0) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.grid_columnconfigure(0, minsize=250)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="LinkedIn Bot",
                                       font=ctk.CTkFont(size=34, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # Botones de navegación (con sus iconos)
        self.connectIcon = self.cargar_icono("customer-insight")
        self.btn_connect = ctk.CTkButton(self.sidebar_frame, text="Connect People", text_color=("black", "white"),
                                         anchor="w", fg_color="transparent", hover_color="#333333", height=40,
                                         cursor="hand2", image=self.connectIcon,
                                         command=lambda: self.select_frame("connect"))
        self.btn_connect.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.searchIcon = self.cargar_icono("search")
        self.btn_people = ctk.CTkButton(self.sidebar_frame, text="Search People", text_color=("black", "white"),
                                        anchor="w", fg_color="transparent", hover_color="#333333", height=40,
                                        cursor="hand2", image=self.searchIcon,
                                        command=lambda: self.select_frame("people"))
        self.btn_people.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        self.briefcaseIcon = self.cargar_icono("briefcase")
        self.btn_jobs = ctk.CTkButton(self.sidebar_frame, text="Vacancies", text_color=("black", "white"), anchor="w",
                                      fg_color="transparent", hover_color="#333333", height=40, cursor="hand2",
                                      image=self.briefcaseIcon, command=lambda: self.select_frame("jobs"))
        self.btn_jobs.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        self.configIcon = self.cargar_icono("configuration")
        self.btn_config = ctk.CTkButton(self.sidebar_frame, text="Configuration", text_color=("black", "white"),
                                        anchor="w", fg_color="transparent", hover_color="#333333", height=40,
                                        cursor="hand2", image=self.configIcon,
                                        command=lambda: self.select_frame("config"))
        self.btn_config.grid(row=5, column=0, padx=10, pady=10, sticky="ew")

        # --- CONTENEDOR DERECHO ---
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        # Inicializar Frames
        self.connect_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.people_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.jobs_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        self.config_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")

        # CREAR LA UI
        self.setup_connect_ui()
        self.setup_people_ui()
        self.setup_jobs_ui()
        self.setup_config_ui()

        # TERMINAL
        self.terminal = ctk.CTkTextbox(self.right_container, height=200, border_width=1)
        self.terminal.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        # 4. AHORA SÍ: RELLENAR LOS CAMPOS (Porque ya existen)
        if self.email_guardado:
            self.entry_email.insert(0, self.email_guardado)

        if self.ruta_guardado:
            self.entry_folder.insert(0, self.ruta_guardado)

        password = keyring.get_password("LinkedInBot_AIntelligence", self.email_guardado)
        if password:
            self.entry_pass.insert(0, password)

        self.select_frame("connect")

    def select_frame(self, name):
        botones = {"connect": self.btn_connect, "people": self.btn_people, "jobs": self.btn_jobs,
            "config": self.btn_config}

        for key, boton in botones.items():
            if key == name:
                boton.configure(fg_color="#333333")  # Botón activo
            else:
                boton.configure(fg_color="transparent")  # Botones inactivos

        # Lógica de visualización
        self.connect_frame.grid_forget()
        self.people_frame.grid_forget()
        self.jobs_frame.grid_forget()
        self.config_frame.grid_forget()

        if name == "connect":
            self.connect_frame.grid(row=0, column=0, sticky="nsew")
        elif name == "people":
            self.people_frame.grid(row=0, column=0, sticky="nsew")
        elif name == "jobs":
            self.jobs_frame.grid(row=0, column=0, sticky="nsew")
        elif name == "config":
            self.config_frame.grid(row=0, column=0, sticky="nsew")

    @staticmethod
    def cargar_icono(nombre_base, size=(20, 20)):
        """
        Carga automáticamente versiones light y dark.
        Ejemplo: nombre_base="search" -> busca "search-light.png" y "search-dark.png"
        """
        ruta_base = "Icons"  # Tu carpeta de iconos

        path_light = os.path.join(ruta_base, f"{nombre_base}-light.png")
        path_dark = os.path.join(ruta_base, f"{nombre_base}-dark.png")

        # Abrimos las imágenes con PIL
        img_light = Image.open(path_light)
        img_dark = Image.open(path_dark)

        return ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=size)

    def guardar_configuracion(self):
        email = self.entry_email.get()
        ruta = self.entry_folder.get()
        password = self.entry_pass.get()

        # 1. Guardar Email y Ruta en JSON (Datos no sensibles)
        datos = {"email": email, "ruta_guardado": ruta}
        with open(self.config_file, "w") as f:
            json.dump(datos, f)

        # 2. Guardar Contraseña en el LLAVERO DEL SISTEMA (Seguro)
        if email and password:
            try:
                keyring.set_password("LinkedInBot_AIntelligence", email, password)
                self.escribir_log("Configuración y contraseña guardadas de forma segura.")
                self.escribir_log("Configuración guardada.")
            except Exception as e:
                self.escribir_log(f"Error al acceder al llavero: {e}")

    def cargar_configuracion(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                datos = json.load(f)
                self.email_guardado = datos.get("email", "")
                self.ruta_guardado = datos.get("ruta_guardado", os.getcwd())

    # ==============================================================================
    # UI SETUP
    # ==============================================================================
    def setup_connect_ui(self):
        self.conn_label = ctk.CTkLabel(self.connect_frame, text="Procesar Lista de Contactos (CSV)",
                                       font=ctk.CTkFont(size=22, weight="bold"))
        self.conn_label.pack(pady=(20, 10))

        # --- NUEVO: Campo para mostrar la ruta del archivo ---
        # Creamos un contenedor para que el Entry y el botón de buscar estén en la misma línea
        path_frame = ctk.CTkFrame(self.connect_frame, fg_color="transparent")
        path_frame.pack(pady=10, padx=20, fill="x")

        # DEFINICIÓN IMPORTANTE: self.entry_csv_path
        self.entry_csv_path = ctk.CTkEntry(path_frame, placeholder_text="No file selected", height=40)
        self.entry_csv_path.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_browse = ctk.CTkButton(path_frame, text="Examine...", height=40, width=100, command=self.load_csv)
        self.btn_browse.pack(side="right")

        # Inicializamos la variable que usabas antes por si acaso
        self.csv_path = None

        # Botón de ejecución
        self.btn_run_csv = ctk.CTkButton(self.connect_frame, text="🚀 Start Processing", fg_color="#28a745",
                                         hover_color="#218838", height=50, font=ctk.CTkFont(weight="bold"),
                                         command=lambda: threading.Thread(target=self.run_csv_process).start())
        self.btn_run_csv.pack(pady=30)

    def setup_people_ui(self):
        ctk.CTkLabel(self.people_frame, text="Buscador de Personas", font=ctk.CTkFont(size=18)).pack(pady=10)
        self.entry_p_search = ctk.CTkEntry(self.people_frame, placeholder_text="Puesto (ej: CTO Malta)", width=300,
                                           height=40)
        self.entry_p_search.pack(pady=5)
        self.slider_pages = ctk.CTkSlider(self.people_frame, from_=1, to=10, number_of_steps=9)
        self.slider_pages.pack(pady=10)
        self.btn_run_people = ctk.CTkButton(self.people_frame, text="Extraer Perfiles", height=40,
                                            command=lambda: threading.Thread(target=self.run_people_search).start())
        self.btn_run_people.pack(pady=10)

    def setup_jobs_ui(self):
        ctk.CTkLabel(self.jobs_frame, text="Buscador de Vacantes", font=ctk.CTkFont(size=18)).pack(pady=10)
        self.entry_j_search = ctk.CTkEntry(self.jobs_frame, placeholder_text="Software Engineer", width=300, height=40)
        self.entry_j_search.pack(pady=5)
        self.combo_pais = ctk.CTkComboBox(self.jobs_frame, values=list(GEOIDS.keys()), height=40)
        self.combo_pais.pack(pady=10)
        self.btn_run_jobs = ctk.CTkButton(self.jobs_frame, text="Buscar Empleos", height=40,
                                          command=lambda: threading.Thread(target=self.run_job_search).start())
        self.btn_run_jobs.pack(pady=10)
        self.job_status_label = ctk.CTkLabel(self.jobs_frame, text="", font=ctk.CTkFont(weight="bold"))
        self.job_status_label.pack(pady=5)

    def setup_config_ui(self):
        # --- TÍTULO PRINCIPAL ---
        ctk.CTkLabel(self.config_frame, text="LinkedIn Account", font=ctk.CTkFont(size=18, weight="bold")).pack(
            fill="x", pady=(20, 10))

        # --- CONTENEDOR PARA CREDENCIALES ---
        form_inner = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        form_inner.pack(pady=10)

        # Email
        ctk.CTkLabel(form_inner, text="Email:", anchor="w").pack(fill="x", padx=5)
        self.entry_email = ctk.CTkEntry(form_inner, placeholder_text="account@email.com", width=350, height=40)
        self.entry_email.pack(pady=(5, 15))

        # Password
        ctk.CTkLabel(form_inner, text="Password:", anchor="w").pack(fill="x", padx=5)
        self.entry_pass = ctk.CTkEntry(form_inner, placeholder_text="••••••••", show="*", width=350, height=40)
        self.entry_pass.pack(pady=(5, 15))

        # --- TÍTULO SECCIÓN DIRECTORIO ---
        ctk.CTkLabel(form_inner, text="Saves Directory Location", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=(20, 10), fill="x")

        ctk.CTkLabel(form_inner, text="Save file on:", anchor="w").pack(fill="x", padx=5)

        # Frame para agrupar la entrada y el botón de búsqueda
        folder_frame = ctk.CTkFrame(form_inner, fg_color="transparent")
        folder_frame.pack(fill="x", pady=5)

        self.entry_folder = ctk.CTkEntry(folder_frame, placeholder_text="Selecciona carpeta...", width=260, height=40)
        self.entry_folder.pack(side="left", padx=(0, 5))

        self.btn_browse_folder = ctk.CTkButton(folder_frame, text="Examine...", width=80, height=40, cursor="hand2",
            command=self.seleccionar_carpeta)
        self.btn_browse_folder.pack(side="left")

        # --- BOTÓN GUARDAR ---
        self.btn_save = ctk.CTkButton(form_inner, text="Save Settings", height=45, fg_color="#0077B5",
                                      command=self.guardar_configuracion)
        self.btn_save.pack(pady=30)

    # ==============================================================================
    # CORE LOGIC
    # ==============================================================================
    @staticmethod
    def iniciar_driver():
        options = uc.ChromeOptions()
        # (Same options as your original script)
        options.add_argument("--window-size=1280,900")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        try:
            return uc.Chrome(options=options)
        except:
            options = uc.ChromeOptions()
            options.add_argument("--window-size=1280,900")
            driver = uc.Chrome(options=options, version_main=145)  # Usa la version más nueva a día 05/03/2026
            return driver

    def escribir_log(self, mensaje):
        try:
            self.terminal.insert("end", f"[{time.strftime('%H:%M:%S')}] {mensaje}\n")
            self.terminal.see("end")
        except Exception as e:
            print(f"Error escribiendo en terminal: {e}")

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(initialdir=self.ruta_guardado, title="Select where you want to save the CSV")
        if carpeta:
            self.ruta_guardado = carpeta
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, carpeta)
            self.escribir_log(f"Save directory set to: {carpeta}")

    def login_proceso(self, driver):
        email = self.entry_email.get()
        password = self.entry_pass.get()
        if not email or not password:
            self.escribir_log(f"Error: Falta Email o Password")
            return False

        driver.get("https://www.linkedin.com/login")
        time.sleep(2)
        try:
            driver.find_element(By.ID, "username").send_keys(email)
            driver.find_element(By.ID, "password").send_keys(password)
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(5)
            if "checkpoint" in driver.current_url:
                self.escribir_log(f"Resuelve el CAPTCHA en el navegador...")
                WebDriverWait(driver, 60).until(ec.url_contains("feed"))
            return True
        except Exception as e:
            self.escribir_log(f"Error Login: {e}")
            return False

    @staticmethod
    def buscar_y_clicar_js(driver, palabras_clave, intentar_clic=True):
        """
        Escanea el DOM buscando botones o elementos que coincidan con las palabras clave.
        Usa una lógica robusta para encontrar spans dentro de botones.
        """
        script = """
            var keywords = arguments[0];
            var click = arguments[1];
            var selectores = "button, span, a, [role='button']";
            var elementos = document.querySelectorAll(selectores);

            for (var i = 0; i < elementos.length; i++) {
                var el = elementos[i];

                // Ignorar elementos no visibles
                if (!(el.offsetWidth > 0 && el.offsetHeight > 0)) continue;

                var txt = (el.innerText || "").toLowerCase().trim();
                var aria = (el.getAttribute("aria-label") || "").toLowerCase().trim();
                var title = (el.getAttribute("title") || "").toLowerCase().trim();

                for (var j = 0; j < keywords.length; j++) {
                    var kw = keywords[j].toLowerCase().trim();

                    // Verificamos coincidencia parcial o exacta
                    if (txt.includes(kw) || aria.includes(kw) || title.includes(kw)) {
                        if (click) {
                            // Si el elemento es un span, intentamos clicar al botón padre
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

    def load_csv(self):
        """Abre el explorador de archivos y carga la ruta en la interfaz."""
        path = filedialog.askopenfilename(initialdir=self.ruta_guardado, title="Seleccionar CSV de contactos",
            filetypes=[("Archivos CSV", "*.csv")])
        if path:
            self.csv_path = path
            self.entry_csv_path.delete(0, "end")
            self.entry_csv_path.insert(0, path)
            self.escribir_log(f"📂 Archivo cargado: {os.path.basename(path)}")

    def run_csv_process(self):
        """Proceso principal de conexión masiva desde CSV."""
        ruta = self.entry_csv_path.get()
        if not ruta or not os.path.exists(ruta):
            self.escribir_log("❌ Error: Selecciona un archivo CSV válido.")
            return

        self.escribir_log("🚀 Iniciando navegador para conectar...")
        driver = self.iniciar_driver()
        if not driver: return

        try:
            if self.login_proceso(driver):
                self.escribir_log("✅ Login exitoso. Procesando lista...")

                with open(ruta, mode='r', encoding='utf-8-sig') as f:
                    reader = csv.DictReader(f)

                    for fila in reader:
                        # Saltar filas vacías
                        if not any(fila.values()): continue

                        # 1. Extracción flexible de datos
                        url = fila.get('url') or fila.get('Link') or fila.get('URL') or fila.get('Perfil LinkedIn')
                        nombre = fila.get('full_name') or fila.get('Nombre') or fila.get(
                            'Nombre Completo') or "Contacto"

                        if not url or "http" not in str(url):
                            self.escribir_log(f"⚠️ Saltando fila: URL no válida.")
                            continue

                        self.escribir_log(f"👤 Visitando a: {nombre}")
                        driver.get(url)
                        time.sleep(random.uniform(5, 7))

                        # 2. Paso 1: Clic en 'Conectar' (Directo o Menú Más)
                        conectado = self.buscar_y_clicar_js(driver, ["conectar", "connect"])

                        if not conectado:
                            self.escribir_log("   🔍 Buscando en menú 'Más'...")
                            if self.buscar_y_clicar_js(driver, ["más...", "more...", "más"]):
                                time.sleep(1.5)
                                conectado = self.buscar_y_clicar_js(driver, ["conectar", "connect"])

                        # 2. PASO: CONFIRMACIÓN FINAL (NAVEGACIÓN POR TABS)
                        if conectado:
                            self.escribir_log("   ↳ Modal detectada. Navegando con TAB al botón...")
                            time.sleep(3.5)

                            try:
                                from selenium.webdriver.common.action_chains import ActionChains
                                actions = ActionChains(driver)

                                # 1. Pulsamos TAB dos veces para saltar de la Modal/Nota al botón 'Enviar sin nota'
                                # (Normalmente es 1 o 2 veces dependiendo de dónde empiece el foco)
                                actions.send_keys(Keys.TAB)
                                time.sleep(0.5)
                                actions.send_keys(Keys.TAB)
                                time.sleep(0.5)
                                actions.send_keys(Keys.TAB)
                                time.sleep(0.5)

                                # 2. Ahora que el foco debería estar en el botón azul, pulsamos ENTER
                                actions.send_keys(Keys.ENTER)
                                actions.perform()

                                # 3. Intento extra con ESPACIO (a veces el ENTER no dispara botones en JS)
                                time.sleep(0.5)
                                actions.send_keys(Keys.SPACE)
                                actions.perform()

                                self.escribir_log(f"   ✅ Comandos de Tabulación + Enter enviados.")

                            except Exception as e:
                                self.escribir_log(f"   ❌ Fallo en navegación TAB: {str(e)}")
                                # Limpieza por si acaso
                                try:
                                    ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                                except:
                                    pass

                            time.sleep(4)

                        # Pausa de seguridad entre contactos
                        espera = random.uniform(10, 18)
                        self.escribir_log(f"⏳ Esperando {int(espera)}s para el siguiente...")
                        time.sleep(espera)

                self.escribir_log("🏁 Proceso de CSV finalizado.")
                if hasattr(self, 'mostrar_notificacion_temporal'):
                    self.mostrar_notificacion_temporal("Éxito", "Lista procesada correctamente.")

        except Exception as e:
            self.escribir_log(f"❌ Error crítico: {str(e)}")
        finally:
            driver.quit()
            self.escribir_log("🔒 Sesión cerrada.")

    def run_people_search(self):
        # 1. Obtener datos de la interfaz
        keyword_p = self.entry_p_search.get()
        paginas = 2

        user_email = self.entry_email.get()
        user_pass = self.entry_pass.get()

        if not user_email or not user_pass:
            self.escribir_log("Error: Configura tus credenciales primero.")
            return

        driver = self.iniciar_driver()
        if not driver: return

        try:
            if self.login_proceso(driver):
                leads_finales = []
                enlaces_vistos = set()

                for p in range(1, paginas + 1):
                    url = f"https://www.linkedin.com/search/results/people/?keywords={urllib.parse.quote(keyword_p)}&page={p}"
                    self.escribir_log(f"Escaneando página {p} de {paginas}...")
                    driver.get(url)
                    time.sleep(5)

                    # Scroll progresivo para cargar imágenes y datos
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)

                    # Seleccionamos las tarjetas
                    items = driver.find_elements(By.CSS_SELECTOR, "[role='listitem']")
                    self.escribir_log(f"Detectados {len(items)} elementos en la página.")

                    for item in items:
                        try:
                            # 1. Extraer Enlace y Nombre
                            enlace_el = item.find_element(By.CSS_SELECTOR,
                                                          "a[data-view-name='search-result-lockup-title']")
                            link = enlace_el.get_attribute("href").split("?")[0]

                            if link in enlaces_vistos: continue
                            nombre = enlace_el.text.strip()

                            # 2. Extraer párrafos para Cargo, Empresa y Ubicación
                            parrafos = item.find_elements(By.TAG_NAME, "p")

                            cargo = "N/A"
                            ubicacion = "N/A"
                            empresa_solo = "N/A"
                            textos_secundarios = []

                            for p_tag in parrafos:
                                txt = p_tag.text.strip()
                                if not txt or txt == nombre or "Conectar" in txt:
                                    continue

                                # Lógica de limpieza de Empresa
                                if "Actual:" in txt:
                                    frase_completa = txt.replace("Actual:", "").strip()
                                    # Split por conectores usando Regex
                                    partes = re.split(r'\s+en\s+|\s+at\s+|\s+@\s+', frase_completa, flags=re.IGNORECASE)
                                    empresa_solo = partes[-1].strip() if len(partes) > 1 else frase_completa
                                else:
                                    textos_secundarios.append(txt)

                            # Asignación de Cargo y Ubicación
                            if len(textos_secundarios) > 1:
                                cargo = textos_secundarios[1]
                            if len(textos_secundarios) > 2:
                                ubicacion = textos_secundarios[2]

                            if len(nombre) > 2:
                                leads_finales.append(
                                    {"Nombre Completo": nombre, "Cargo": cargo, "Empresa": empresa_solo,
                                        "Ubicación": ubicacion, "Perfil LinkedIn": link})
                                enlaces_vistos.add(link)
                        except:
                            continue

                # --- GUARDADO AUTOMÁTICO ---
                if leads_finales:
                    df = pd.DataFrame(leads_finales)
                    nombre_archivo = f"Leads_{keyword_p.replace(' ', '_')}.csv"
                    ruta_final = os.path.join(self.ruta_guardado, nombre_archivo)

                    df.to_csv(ruta_final, index=False, encoding='utf-8-sig')

                    self.escribir_log(f"¡Hecho! {len(df)} perfiles únicos guardados.")
                    self.escribir_log(f"Guardado: {nombre_archivo}")
                else:
                    self.escribir_log("No se capturaron datos. Revisa el navegador.")

        finally:
            driver.quit()
            self.escribir_log("Sesión de búsqueda finalizada.")

    def run_job_search(self):
        # 1. Obtener datos de la UI
        job_key = self.entry_j_search.get()
        pais_seleccionado = self.combo_pais.get()
        user_email = self.entry_email.get()
        user_pass = self.entry_pass.get()

        if not user_email or not user_pass:
            self.escribir_log("❌ Error: Introduce tus credenciales en Configuración.")
            return

        # 2. Iniciar Navegador
        driver = self.iniciar_driver()
        if not driver: return

        try:
            if self.login_proceso(driver):
                # --- DESEMPAQUETADO ---
                datos_pais = GEOIDS[pais_seleccionado]
                nombre_pais_en = datos_pais[0]
                geo_id = datos_pais[1]

                url_busqueda = (f"https://www.linkedin.com/jobs/search/?"
                                f"keywords={urllib.parse.quote(job_key)}"
                                f"&geoId={geo_id}"
                                f"&location={urllib.parse.quote(nombre_pais_en)}"
                                f"&f_WT=1%2C3"
                                f"&sortBy=DD")

                self.escribir_log(f"🌍 Buscando '{job_key}' en {pais_seleccionado}...")
                driver.get(url_busqueda)
                time.sleep(5)

                # --- SCROLL DINÁMICO ---
                try:
                    panel = None
                    for selector in [".jobs-search-results-list", ".scaffold-layout__list-container", "main"]:
                        try:
                            panel = driver.find_element(By.CSS_SELECTOR, selector)
                            if panel.is_displayed(): break
                        except:
                            continue

                    if panel:
                        for i in range(5):
                            self.escribir_log(f"Scroll en panel de resultados ({i + 1}/5)...")
                            driver.execute_script("arguments[0].scrollTop += 1000;", panel)
                            time.sleep(1.5)
                except:
                    pass

                # --- EXTRACCIÓN ---
                cards = driver.find_elements(By.XPATH, "//div[contains(@class, 'job-card-container')]")
                self.escribir_log(f"Analizando {len(cards)} tarjetas encontradas...")
                resultados = []

                for card in cards:
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

                        # Reclutador
                        reclutador = "Anónimo"
                        try:
                            reclutador_el = driver.find_element(By.CSS_SELECTOR,
                                                                ".jobs-poster__name, .app-aware-link.jobs-poster__name")
                            reclutador = reclutador_el.text.strip()
                        except:
                            pass

                        # Email en descripción
                        email_detectado = "No encontrado"
                        try:
                            descripcion = driver.find_element(By.ID, "job-details").text
                            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', descripcion)
                            if emails: email_detectado = ", ".join(list(set(emails)))
                        except:
                            pass

                        # Modalidad
                        modalidad = "No especificada"
                        try:
                            info_empleo = driver.find_element(By.CLASS_NAME, "jobs-unified-top-card__job-insight").text
                            if any(x in info_empleo for x in ["Híbrido", "Hybrid"]):
                                modalidad = "Híbrido"
                            elif any(x in info_empleo for x in ["Presencial", "On-site"]):
                                modalidad = "Presencial"
                            elif any(x in info_empleo for x in ["Remoto", "Remote"]):
                                modalidad = "Remoto"
                        except:
                            pass

                        palabras_basura = ["Inicio", "Notificaciones", "Mensajes", "Mi red", "Empleos", "Premium"]
                        if not any(pb in titulo for pb in palabras_basura):
                            resultados.append({"Puesto": titulo, "Empresa": empresa, "Ubicación": ubicacion_texto,
                                "Modalidad": modalidad, "Reclutador": reclutador, "Email": email_detectado,
                                "Link": url_job})
                            self.escribir_log(f"✅ Extraído: {titulo} en {empresa}")

                    except:
                        continue

                # --- PROCESAMIENTO FINAL ---
                if resultados:
                    df = pd.DataFrame(resultados).drop_duplicates(subset=['Link'])
                    if pais_seleccionado != "Reino Unido":
                        df = df[
                            ~df['Ubicación'].str.contains('United Kingdom|Reino Unido|London', case=False, na=False)]

                    if not df.empty:
                        # Generamos un nombre sugerido
                        nombre_sugerido = f"Vacantes_{pais_seleccionado}_{int(time.time())}.csv"

                        # Abrir el "Guardar como..." nativo del sistema
                        archivo_path = filedialog.asksaveasfilename(initialdir=self.ruta_guardado,
                            initialfile=nombre_sugerido, defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

                        if archivo_path:
                            df.to_csv(archivo_path, index=False, encoding='utf-8-sig')
                            self.escribir_log(f"Guardado en:\n{os.path.basename(archivo_path)}")
                            self.escribir_log(f"Archivo guardado en: {archivo_path}")
                        else:
                            self.escribir_log("Guardado cancelado por el usuario.")
                    else:
                        self.escribir_log("No quedaron resultados tras filtrar por ubicación.")
                else:
                    self.escribir_log("No se detectaron vacantes válidas.")

        finally:
            driver.quit()
            self.escribir_log("Navegador cerrado.")


if __name__ == "__main__":
    app = LinkedInBotApp()
    app.mainloop()
