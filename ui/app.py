import time
import threading

import customtkinter as ctk

from utils.helpers import cargar_icono, cargar_configuracion, obtener_password_guardada
from ui.connect_frame import ConnectFrame
from ui.people_frame import PeopleFrame
from ui.jobs_frame import JobsFrame
from ui.config_frame import ConfigFrame


class LinkedInBotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LinkedIn Bot")
        self.geometry("1000x600")

        # Cargar configuración persistida
        email_guardado, ruta_guardado = cargar_configuracion()
        password_guardada = obtener_password_guardada(email_guardado)

        # ── Evento de parada compartido entre todos los procesos ──—──────────
        self.stop_event = threading.Event()

        # --- Grid principal ---
        self.grid_columnconfigure(0, minsize=250)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="LinkedIn Bot",
                     font=ctk.CTkFont(size=34, weight="bold")).grid(row=0, column=0, padx=20, pady=20)

        nav_items = [
            ("connect",  1, "customer-insight", "Connect People"),
            ("people",   2, "search",            "Search People"),
            ("jobs",     3, "briefcase",         "Vacancies"),
            ("config",   5, "configuration",     "Configuration"),
        ]
        self._nav_buttons = {}
        for name, row, icon_name, label in nav_items:
            icon = cargar_icono(icon_name)
            btn = ctk.CTkButton(
                self.sidebar_frame, text=label,
                text_color=("#333333", "white"), anchor="w",
                fg_color="transparent", hover_color=("#CCCCCC", "#333333"),
                height=40, cursor="hand2", image=icon,
                command=lambda n=name: self.select_frame(n)
            )
            btn.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            self._nav_buttons[name] = btn

        # ── CONTENEDOR DERECHO ───────────────────────────────────────────────
        self.right_container = ctk.CTkFrame(self, fg_color="transparent")
        self.right_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.right_container.grid_rowconfigure(0, weight=1)
        self.right_container.grid_columnconfigure(0, weight=1)

        # ── CONFIG FRAME ─────────────────────────────────────────────────────
        self.config_frame = ConfigFrame(
            self.right_container,
            email_inicial=email_guardado,
            password_inicial=password_guardada or "",
            ruta_inicial=ruta_guardado,
            log_fn=self.escribir_log,
        )

        # ── RESTO DE FRAMES ──────────────────────────────────────────────────
        self.connect_frame = ConnectFrame(
            self.right_container,
            get_credentials_fn=self.config_frame.get_credentials,
            get_save_dir_fn=self.config_frame.get_save_dir,
            log_fn=self.escribir_log,
            stop_event=self.stop_event,
            stop_fn=self._parar_proceso,
        )
        self.people_frame = PeopleFrame(
            self.right_container,
            get_credentials_fn=self.config_frame.get_credentials,
            get_save_dir_fn=self.config_frame.get_save_dir,
            log_fn=self.escribir_log,
            stop_event=self.stop_event,
            stop_fn=self._parar_proceso,
        )
        self.jobs_frame = JobsFrame(
            self.right_container,
            get_credentials_fn=self.config_frame.get_credentials,
            get_save_dir_fn=self.config_frame.get_save_dir,
            log_fn=self.escribir_log,
            stop_event=self.stop_event,
            stop_fn=self._parar_proceso,
        )

        self._all_frames = {
            "connect": self.connect_frame,
            "people":  self.people_frame,
            "jobs":    self.jobs_frame,
            "config":  self.config_frame,
        }

        # ── TERMINAL ───────────────────────────────────────────────────────────
        terminal_frame = ctk.CTkFrame(self.right_container, fg_color="transparent")
        terminal_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        terminal_frame.grid_columnconfigure(0, weight=1)

        self.terminal = ctk.CTkTextbox(
            terminal_frame, height=150, border_width=1, state="disabled"
        )
        self.terminal.grid(row=0, column=0, sticky="ew")


        self.select_frame("connect")

    # ── Navegación ────────────────────────────────────────────────────────────
    def select_frame(self, name):
        for key, btn in self._nav_buttons.items():
            color_seleccionado = ("#CCCCCC", "#333333") if key == name else "transparent"
            btn.configure(fg_color=color_seleccionado)

        for frame in self._all_frames.values():
            frame.grid_forget()

        self._all_frames[name].grid(row=0, column=0, sticky="nsew")

    # ── Control de parada ─────────────────────────────────────────────────────
    def _parar_proceso(self):
        self.stop_event.set()
        self.escribir_log("⏹ Señal de parada enviada. Finalizando tras el paso actual...")

    def set_proceso_activo(self, activo: bool):
        """Llamado por los frames al iniciar/terminar un proceso."""
        if activo:
            self.stop_event.clear()
        # El botón Stop es manejado por cada frame individualmente

    # ── Terminal de log ───────────────────────────────────────────────────────
    def escribir_log(self, mensaje):
        timestamp = time.strftime("%H:%M:%S")
        self.terminal.configure(state="normal")
        self.terminal.insert("end", f"[{timestamp}] {mensaje}\n")
        self.terminal.see("end")
        self.terminal.configure(state="disabled")
        self.update_idletasks()