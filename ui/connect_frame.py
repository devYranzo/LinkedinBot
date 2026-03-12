import os
import threading
from tkinter import filedialog

import customtkinter as ctk

from core.connector import run_csv_process


class ConnectFrame(ctk.CTkFrame):
    def __init__(self, parent, get_credentials_fn, get_save_dir_fn, log_fn, stop_event, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._get_credentials = get_credentials_fn
        self._get_save_dir = get_save_dir_fn
        self._log = log_fn
        self._stop_event = stop_event
        self.csv_path = None

        # --- Título ---
        ctk.CTkLabel(self, text="Connect with people",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Upload the CSV file you got on Search People",
                     text_color="gray", font=ctk.CTkFont(size=15)).pack(pady=(5, 10))

        # --- Selector de archivo ---
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(pady=20)

        self.entry_csv_path = ctk.CTkEntry(
            path_frame, placeholder_text="No file selected",
            width=300, height=40, state="readonly"
        )
        self.entry_csv_path.pack(side="left", padx=(0, 10))

        ctk.CTkButton(path_frame, text="Examine...", height=40, width=100,
                      command=self._load_csv).pack(side="left")

        # --- Botón de ejecución ---
        ctk.CTkButton(self, text="Start Processing", height=40,
                      font=ctk.CTkFont(weight="bold"),
                      command=self._iniciar).pack(pady=30)

    def _load_csv(self):
        path = filedialog.askopenfilename(
            initialdir=self._get_save_dir(),
            title="Seleccionar CSV de contactos",
            filetypes=[("Archivos CSV", "*.csv")]
        )
        if path:
            self.csv_path = path
            self.entry_csv_path.configure(state="normal")
            self.entry_csv_path.delete(0, "end")
            self.entry_csv_path.insert(0, path)
            self.entry_csv_path.xview_moveto(1.0)
            self.entry_csv_path.configure(state="readonly")
            self._log(f"Archivo cargado: {os.path.basename(path)}")

    def _iniciar(self):
        # Notificar a la app que hay un proceso activo (activa el botón Stop)
        self.winfo_toplevel().set_proceso_activo(True)
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            ruta = self.entry_csv_path.get()
            if not ruta or not os.path.exists(ruta):
                self._log("Error: Selecciona un archivo CSV válido.")
                return

            email, password = self._get_credentials()
            run_csv_process(email, password, ruta, log_fn=self._log, stop_event=self._stop_event)
        finally:
            self.winfo_toplevel().set_proceso_activo(False)