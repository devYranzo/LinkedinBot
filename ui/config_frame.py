import os
from tkinter import filedialog

import customtkinter as ctk

from utils.helpers import guardar_configuracion


class ConfigFrame(ctk.CTkScrollableFrame):
    def __init__(self, parent, email_inicial, password_inicial, ruta_inicial, log_fn, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._log = log_fn

        # --- Título de credenciales ---
        ctk.CTkLabel(self, text="LinkedIn Account",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(fill="x", pady=(10, 10))

        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(pady=10)

        # Email
        ctk.CTkLabel(form, text="Email:", anchor="w").pack(fill="x", padx=5)
        self.entry_email = ctk.CTkEntry(
            form, placeholder_text="account@email.com", width=350, height=40
        )
        self.entry_email.pack(pady=(5, 15))

        # Password
        ctk.CTkLabel(form, text="Password:", anchor="w").pack(fill="x", padx=5)
        self.entry_pass = ctk.CTkEntry(
            form, placeholder_text="••••••••", show="*", width=350, height=40
        )
        self.entry_pass.pack(pady=(5, 15))

        # --- Botón guardar ---
        ctk.CTkButton(form, text="Save", height=40, command=self._guardar).pack(pady=10)

        # --- Título de directorio ---
        ctk.CTkLabel(form, text="Saves Directory Location",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(10, 10), fill="x")
        ctk.CTkLabel(form, text="Save file on:", anchor="w").pack(fill="x", padx=5)

        folder_frame = ctk.CTkFrame(form, fg_color="transparent")
        folder_frame.pack(fill="x", pady=5)

        self.entry_folder = ctk.CTkEntry(
            folder_frame, placeholder_text="Selecciona carpeta...", width=260, height=40
        )
        self.entry_folder.pack(side="left", padx=(0, 5))

        ctk.CTkButton(folder_frame, text="Examine...", width=80, height=40, cursor="hand2",
                      command=self._seleccionar_carpeta).pack(side="left")

        # Prellenar campos con datos guardados
        self.entry_email.insert(0, email_inicial)
        self.entry_pass.insert(0, password_inicial)
        self.entry_folder.insert(0, ruta_inicial)

    def get_credentials(self):
        return self.entry_email.get(), self.entry_pass.get()

    def get_save_dir(self):
        return self.entry_folder.get() or os.getcwd()

    def _seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(
            initialdir=self.get_save_dir(),
            title="Select where you want to save the CSV"
        )
        if carpeta:
            self.entry_folder.delete(0, "end")
            self.entry_folder.insert(0, carpeta)
            self._log(f"Save directory set to: {carpeta}")

    def _guardar(self):
        email = self.entry_email.get()
        password = self.entry_pass.get()
        ruta = self.entry_folder.get()
        guardar_configuracion(email, ruta, password, log_fn=self._log)
