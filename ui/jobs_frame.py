import time
import threading
from tkinter import filedialog

import customtkinter as ctk

from config import GEOIDS
from core.job_search import run_job_search


class JobsFrame(ctk.CTkFrame):
    def __init__(self, parent, get_credentials_fn, get_save_dir_fn, log_fn, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._get_credentials = get_credentials_fn
        self._get_save_dir = get_save_dir_fn
        self._log = log_fn

        # --- Título ---
        ctk.CTkLabel(self, text="Find Vacants on LinkedIn",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Introduce role to be searched",
                     text_color="gray", font=ctk.CTkFont(size=15)).pack(pady=(5, 10))

        # --- Campo de búsqueda ---
        self.entry_search = ctk.CTkEntry(
            self, placeholder_text="Software Engineer", width=300, height=40
        )
        self.entry_search.pack(pady=5)

        # --- Selector de país ---
        self.combo_pais = ctk.CTkOptionMenu(
            self, values=list(GEOIDS.keys()),
            width=300, height=40, dynamic_resizing=False,
            fg_color="#3b3b3b", button_color="#2b2b2b", button_hover_color="#4b4b4b",
        )
        self.combo_pais.pack(pady=20)

        # --- Botón de ejecución ---
        ctk.CTkButton(self, text="Buscar Empleos", height=40,
                      command=lambda: threading.Thread(
                          target=self._run, daemon=True
                      ).start()).pack(pady=10)

        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=5)

    def _save_callback(self, df, pais_seleccionado):
        """Abre el diálogo 'Guardar como...' desde el hilo principal."""
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

    def _run(self):
        job_key = self.entry_search.get()
        pais = self.combo_pais.get()
        email, password = self._get_credentials()

        if not email or not password:
            self._log("Error: Introduce tus credenciales en Configuración.")
            return

        run_job_search(
            email, password, job_key, pais,
            save_callback=self._save_callback,
            log_fn=self._log
        )
