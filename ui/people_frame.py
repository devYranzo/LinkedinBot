import threading

import customtkinter as ctk

from core.people_search import run_people_search


class PeopleFrame(ctk.CTkFrame):
    def __init__(self, parent, get_credentials_fn, get_save_dir_fn, log_fn, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._get_credentials = get_credentials_fn
        self._get_save_dir = get_save_dir_fn
        self._log = log_fn

        # --- Título ---
        ctk.CTkLabel(self, text="Find People on LinkedIn",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Introduce role to be searched",
                     text_color="gray", font=ctk.CTkFont(size=15)).pack(pady=(5, 10))

        # --- Campo de búsqueda ---
        self.entry_search = ctk.CTkEntry(
            self, placeholder_text="Puesto (ej: CTO Malta)", width=300, height=40
        )
        self.entry_search.pack(pady=5)

        # --- Slider de páginas ---
        self.label_pages = ctk.CTkLabel(self, text="Pages to extract: 3",
                                        font=ctk.CTkFont(size=14))
        self.label_pages.pack(pady=(10, 0))

        self.slider_pages = ctk.CTkSlider(
            self, from_=1, to=10, number_of_steps=9,
            width=300, height=20,
            command=self._update_pages_label
        )
        self.slider_pages.set(3)
        self.slider_pages.pack(pady=(5, 10))

        # --- Botón de ejecución ---
        ctk.CTkButton(self, text="Extraer Perfiles", height=40,
                      command=lambda: threading.Thread(
                          target=self._run, daemon=True
                      ).start()).pack(pady=10)

    def _update_pages_label(self, valor):
        self.label_pages.configure(text=f"Pages to extract: {int(valor)}")

    def _run(self):
        keyword = self.entry_search.get()
        paginas = int(self.slider_pages.get())
        email, password = self._get_credentials()

        if not email or not password:
            self._log("Error: Configura tus credenciales primero.")
            return

        run_people_search(
            email, password, keyword, paginas,
            self._get_save_dir(), log_fn=self._log
        )
