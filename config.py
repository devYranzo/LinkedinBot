import customtkinter as ctk

# --- Apariencia ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

# --- Datos de países ---
GEOIDS = {
    "Malta": ("Malta", "102126540"),
    "España": ("Spain", "105646813"),
}

# --- Archivos ---
CONFIG_FILE = "config.json"
KEYRING_SERVICE = "LinkedInBot_AIntelligence"
