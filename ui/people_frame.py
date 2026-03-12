import threading

import customtkinter as ctk

from core.people_search import run_people_search


class PeopleFrame(ctk.CTkFrame):
    def __init__(self, parent, get_credentials_fn, get_save_dir_fn, log_fn, stop_event, stop_fn=None, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

        self._get_credentials = get_credentials_fn
        self._get_save_dir = get_save_dir_fn
        self._log = log_fn
        self._stop_event = stop_event
        self._stop_fn = stop_fn

        # --- Título ---
        ctk.CTkLabel(self, text="Find People on LinkedIn",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Introduce role to be searched",
                     text_color="gray", font=ctk.CTkFont(size=15)).pack(pady=(5, 10))

        # --- Campo de búsqueda ---
        self.entry_search = ctk.CTkEntry(
            self, placeholder_text="Work position (ej: CTO Malta)", width=350, height=40
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

        # --- Botones de ejecución ---
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.pack(pady=20)

        ctk.CTkButton(buttons_frame, text="Start searching...", height=40,
                      command=self._iniciar).pack(side="left", padx=5)

        self.btn_stop = ctk.CTkButton(buttons_frame, text="⏹  Stop", height=40,
                                      fg_color="#c0392b", hover_color="#922b21",
                                      font=ctk.CTkFont(weight="bold"),
                                      state="disabled",
                                      command=self._parar).pack(side="left", padx=5)

    def _update_pages_label(self, valor):
        self.label_pages.configure(text=f"Pages to extract: {int(valor)}")

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
            keyword = self.entry_search.get()
            paginas = int(self.slider_pages.get())
            email, password = self._get_credentials()

            if not email or not password:
                self._log("Error: Configura tus credenciales primero.")
                return

            run_people_search(
                email, password, keyword, paginas,
                self._get_save_dir(), log_fn=self._log, stop_event=self._stop_event
            )
        finally:
            self.winfo_toplevel().set_proceso_activo(False)
            self.btn_stop.configure(state="disabled")
