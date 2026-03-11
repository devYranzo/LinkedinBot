import os
import json
import keyring
import customtkinter as ctk
from PIL import Image

from config import CONFIG_FILE, KEYRING_SERVICE


def cargar_icono(nombre_base, size=(20, 20)):
    """
    Carga automáticamente versiones light y dark de un icono.
    Ejemplo: nombre_base="search" -> busca "search-light.png" y "search-dark.png"
    """
    ruta_base = "Icons"
    path_light = os.path.join(ruta_base, f"{nombre_base}-light.png")
    path_dark = os.path.join(ruta_base, f"{nombre_base}-dark.png")

    img_light = Image.open(path_light)
    img_dark = Image.open(path_dark)

    return ctk.CTkImage(light_image=img_light, dark_image=img_dark, size=size)


def cargar_configuracion():
    """Lee email y ruta guardados del archivo JSON de configuración."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            datos = json.load(f)
            return datos.get("email", ""), datos.get("ruta_guardado", os.getcwd())
    return "", os.getcwd()


def guardar_configuracion(email, ruta, password, log_fn=None):
    """Guarda email/ruta en JSON y la contraseña en el llavero del sistema."""
    datos = {"email": email, "ruta_guardado": ruta}
    with open(CONFIG_FILE, "w") as f:
        json.dump(datos, f)

    if email and password:
        try:
            keyring.set_password(KEYRING_SERVICE, email, password)
            if log_fn:
                log_fn("Configuración y contraseña guardadas de forma segura.")
                log_fn("Configuración guardada.")
        except Exception as e:
            if log_fn:
                log_fn(f"Error al acceder al llavero: {e}")


def obtener_password_guardada(email):
    """Recupera la contraseña almacenada en el llavero del sistema."""
    return keyring.get_password(KEYRING_SERVICE, email)
