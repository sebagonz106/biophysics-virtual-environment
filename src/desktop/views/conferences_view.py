"""
Vista de conferencias digitales.
"""

import customtkinter as ctk
from tkinter import messagebox


class ConferencesView(ctk.CTkFrame):
    """
    Vista para el módulo de Conferencias Digitales.
    """
    
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self._load_conferences()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.title = ctk.CTkLabel(
            header_frame,
            text="📖 Conferencias Digitales",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(
            header_frame,
            text="Contenido teórico organizado por temas",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, sticky="w")
        
        # Frame principal con scroll
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Mensaje inicial
        self.empty_label = ctk.CTkLabel(
            self.main_frame,
            text="📂 No hay conferencias disponibles\n\nPara agregar conferencias:\n1. Coloque archivos PDF en data/conferences/pdfs/\n2. Edite data/conferences/_index.json",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center"
        )
        self.empty_label.grid(row=0, column=0, pady=50)
    
    def _load_conferences(self):
        """Carga las conferencias desde el repositorio."""
        if not self.app:
            return
        
        conferences = self.app.conference_repo.get_all()
        
        if conferences:
            self.empty_label.grid_forget()
            
            # Agrupar por tema
            topics = {}
            for conf in conferences:
                topic = conf.get("topic", "General")
                if topic not in topics:
                    topics[topic] = []
                topics[topic].append(conf)
            
            row = 0
            for topic, confs in sorted(topics.items()):
                # Header del tema
                topic_frame = self._create_topic_section(topic, confs, row)
                topic_frame.grid(row=row, column=0, sticky="ew", pady=10)
                row += 1
    
    def _create_topic_section(self, topic: str, conferences: list, row: int) -> ctk.CTkFrame:
        """Crea una sección para un tema."""
        frame = ctk.CTkFrame(self.main_frame)
        frame.grid_columnconfigure(0, weight=1)
        
        # Título del tema
        topic_label = ctk.CTkLabel(
            frame,
            text=f"📁 {topic}",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        topic_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        # Lista de conferencias
        for i, conf in enumerate(sorted(conferences, key=lambda x: x.get("order", 0))):
            conf_item = self._create_conference_item(conf)
            conf_item.grid(row=i+1, column=0, sticky="ew", padx=15, pady=2)
        
        return frame
    
    def _create_conference_item(self, conf: dict) -> ctk.CTkFrame:
        """Crea un item de conferencia."""
        frame = ctk.CTkFrame(self.main_frame, fg_color=("gray90", "gray20"))
        frame.grid_columnconfigure(1, weight=1)
        
        # Número de orden
        order_label = ctk.CTkLabel(
            frame,
            text=f"{conf.get('order', '?')}.",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=30
        )
        order_label.grid(row=0, column=0, padx=(10, 5), pady=10)
        
        # Título
        title_label = ctk.CTkLabel(
            frame,
            text=conf.get("title", "Sin título"),
            font=ctk.CTkFont(size=13),
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="w", pady=10)
        
        # Botón de abrir
        if conf.get("local_path"):
            open_btn = ctk.CTkButton(
                frame,
                text="📄 Abrir",
                width=80,
                height=28,
                command=lambda: self._open_conference(conf)
            )
            open_btn.grid(row=0, column=2, padx=10, pady=10)
        else:
            no_file_label = ctk.CTkLabel(
                frame,
                text="Sin archivo",
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            no_file_label.grid(row=0, column=2, padx=10, pady=10)
        
        return frame
    
    def _open_conference(self, conf: dict):
        """Abre un archivo de conferencia."""
        if self.app and conf.get("local_path"):
            success = self.app.file_manager.open_pdf(conf["local_path"])
            if not success:
                messagebox.showerror(
                    "Error",
                    f"No se pudo abrir el archivo:\n{conf['local_path']}"
                )
