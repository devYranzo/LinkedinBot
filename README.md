# LinkedIn Automation

![Python](https://img.shields.io/badge/python-3.14+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/interface-CustomTkinter-black.svg)

Una herramienta de escritorio potente y visual diseñada para optimizar procesos de networking en LinkedIn. Permite la extracción de perfiles por puesto de trabajo y la automatización inteligente de invitaciones mediante procesamiento de archivos CSV.

## ✨ Características Principales

* **Búsqueda Avanzada:** Encuentra perfiles específicos por rol y ubicación (ej: "CTO Malta") con control de paginación.
* **Conexión Inteligente:** Algoritmo avanzado que detecta botones de conexión ocultos en menús secundarios.
* **Evasión de Bloqueos:** Simulación de comportamiento humano mediante navegación por teclado (Tab/Enter) y tiempos de espera aleatorios.
* **Gestión de CSV:** Carga masiva de contactos con detección flexible de columnas (`url`, `full_name`, etc.).
* **Interfaz Moderna:** GUI oscura y profesional construida con `CustomTkinter`.
* **Logs en Tiempo Real:** Terminal integrada no editable para monitorizar cada paso del proceso.

## ⚠️ Aviso de Seguridad y Buenas Prácticas (IMPORTANTE)

El uso de este software implica interactuar con la plataforma de LinkedIn de manera automatizada. Para evitar restricciones o el baneo permanente de tu cuenta, es imperativo seguir estas reglas:

### 🚫 Reglas de Oro
1. **Sesión Única:** NUNCA ejecutes este script mientras tienes la cuenta abierta en otro navegador o dispositivo (móvil, tablet u otro PC). LinkedIn detecta la actividad concurrente desde diferentes IPs y suspende la cuenta de inmediato.
2. **Límites Diarios:** No superes las **20-30 invitaciones diarias**. Si tu cuenta es nueva o tiene pocos contactos, empieza con 5-10 al día.
3. **Pausas Humanas:** El script incluye tiempos de espera aleatorios. No intentes reducirlos para "ir más rápido"; la velocidad constante es la huella digital de un bot.
4. **Enfriamiento (Cooldown):** Si recibes un aviso de "actividad inusual", detén el script inmediatamente y no lo uses durante al menos 48 horas.

### ⚖️ Descargo de Responsabilidad (Disclaimer)
Este proyecto ha sido creado exclusivamente con fines educativos y de investigación técnica. 
* **Uso bajo propio riesgo:** El autor no se hace responsable del uso indebido de esta herramienta ni de las posibles sanciones, restricciones o cierres de cuenta por parte de LinkedIn.
* **Términos de Servicio:** El uso de automatizaciones viola los [Términos de Servicio de LinkedIn](https://www.linkedin.com/legal/user-agreement). Al descargar y ejecutar este código, asumes toda la responsabilidad legal y técnica.

## 🚀 Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone https://github.com/devYranzo/LinkedinBot.git
    cd LinkedinBot
    ```

2.  **Instala las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configura el Driver:**
    Asegúrate de tener instalado [Google Chrome](https://www.google.com/chrome/) y el `chromedriver` correspondiente a tu versión de navegador.

## 🛠️ Uso

1. Ejecuta la aplicación:
   ```bash
   python3 main.py