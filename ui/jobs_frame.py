import time
import threading
from tkinter import filedialog

import customtkinter as ctk

from config import GEOIDS
from core.job_search import run_job_search


class JobsFrame(ctk.CTkFrame):
    def __init__(self, parent, get_credentials_fn, get_save_dir_fn, log_fn, stop_event, stop_fn=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._get_credentials = get_credentials_fn
        self._get_save_dir = get_save_dir_fn
        self._log = log_fn
        self._stop_event = stop_event
        self._stop_fn = stop_fn

        # --- Título ---
        ctk.CTkLabel(self, text="Find Vacants on LinkedIn",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Introduce role to be searched",
                     text_color="gray", font=ctk.CTkFont(size=15)).pack(pady=(5, 10))

        # --- Campo de búsqueda ---
        self.entry_search = ctk.CTkEntry(
            self, placeholder_text="Software Engineer", width=350, height=40
        )
        self.entry_search.pack(pady=5)

        # --- Selector de país ---
        self.combo_pais = ctk.CTkOptionMenu(
            self, values=list(GEOIDS.keys()),
            width=300, height=40, dynamic_resizing=False,
            fg_color=("#F9F9FA", "#3b3b3b"),
            button_color=("#EBEBEC", "#2b2b2b"),
            button_hover_color=("#D4D4D7", "#4b4b4b"),
            text_color=("black", "white"),
        )
        self.combo_pais.pack(pady=20)

        # --- Botones de ejecución ---
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=20)

        ctk.CTkButton(buttons_frame, text="Buscar Empleos", height=40,
                      command=self._iniciar).pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(buttons_frame, text="⏹  Stop", height=40,
                                      fg_color="#c0392b", hover_color="#922b21",
                                      font=ctk.CTkFont(weight="bold"),
                                      state="disabled",
                                      command=self._parar).pack(side="left", padx=5)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=5)

    def _save_callback(self, df, pais_seleccionado):
        nombre_sugerido = f"Vacantes_{pais_seleccionado}_{int(time.time())}.csv"
        archivo_path = filedialog.asksaveasfilename(
            initialdir=self._get_save_dir(),
            initialfile=nombre_sugerido,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if archivo_path:
            df.to_csv(archivo_path, index=False, encoding='utf-8-sig')
            self._log(f"Guardado en:\n{archivo_path}")
        else:
            self._log("Guardado cancelado por el usuario.")

    def _iniciar(self):
        self.winfo_toplevel().set_proceso_activo(True)
        self.btn_stop.configure(state="normal")
        threading.Thread(target=self._run, daemon=True).start()

    def _parar(self):
        """Parar el proceso actual."""
        if self._stop_fn:
            self._stop_fn()
        self.btn_stop.configure(state="disabled")

    def _run(self):
        try:
            job_key = self.entry_search.get()
            pais = self.combo_pais.get()
            email, password = self._get_credentials()

            if not email or not password:
                self._log("Error: Introduce tus credenciales en Configuración.")
                return

            run_job_search(
                email, password, job_key, pais,
                save_callback=self._save_callback,
                log_fn=self._log,
                stop_event=self._stop_event,
            )
        finally:
            self.winfo_toplevel().set_proceso_activo(False)
            self.btn_stop.configure(state="disabled")
