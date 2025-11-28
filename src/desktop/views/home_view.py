"""
Vista de inicio/bienvenida.
"""

import customtkinter as ctk


class HomeView(ctk.CTkFrame):
    """
    Vista principal de bienvenida.
    """
    
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        # Título de bienvenida
        self.title = ctk.CTkLabel(
            self,
            text="🧬 Bienvenido al Entorno Virtual de Biofísica",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, pady=(20, 10))
        
        self.subtitle = ctk.CTkLabel(
            self,
            text="Herramienta Interactiva para la Resolución de Problemas",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, pady=(0, 30))
        
        # Frame de módulos
        self.modules_frame = ctk.CTkFrame(self)
        self.modules_frame.grid(row=2, column=0, sticky="ew", padx=50, pady=20)
        self.modules_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Tarjetas de módulos
        modules = [
            {
                "icon": "📖",
                "title": "Conferencias Digitales",
                "description": "Accede al contenido teórico organizado por temas",
                "view": "conferences",
                "row": 0, "col": 0
            },
            {
                "icon": "📚",
                "title": "Bibliografía",
                "description": "Consulta las referencias bibliográficas recomendadas",
                "view": "bibliography",
                "row": 0, "col": 1
            },
            {
                "icon": "📝",
                "title": "Problemas Propuestos",
                "description": "Practica con ejercicios de cada tema",
                "view": "problems",
                "row": 1, "col": 0
            },
            {
                "icon": "🧮",
                "title": "Módulos Interactivos",
                "description": "Resuelve problemas con retroalimentación inmediata",
                "view": "osmosis",
                "row": 1, "col": 1
            },
        ]
        
        for mod in modules:
            card = self._create_module_card(
                mod["icon"],
                mod["title"],
                mod["description"],
                mod["view"]
            )
            card.grid(
                row=mod["row"],
                column=mod["col"],
                padx=10,
                pady=10,
                sticky="nsew"
            )
        
        # Sección de módulos interactivos
        self.interactive_label = ctk.CTkLabel(
            self,
            text="⚡ Acceso Rápido a Módulos Interactivos",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.interactive_label.grid(row=3, column=0, pady=(30, 15))
        
        self.quick_buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quick_buttons_frame.grid(row=4, column=0)
        
        # Botones de acceso rápido
        osmosis_btn = ctk.CTkButton(
            self.quick_buttons_frame,
            text="💧 Módulo de Ósmosis",
            font=ctk.CTkFont(size=14),
            width=200,
            height=45,
            command=lambda: self.app.show_view("osmosis") if self.app else None
        )
        osmosis_btn.grid(row=0, column=0, padx=10, pady=5)
        
        patch_btn = ctk.CTkButton(
            self.quick_buttons_frame,
            text="⚡ Módulo Patch Clamp",
            font=ctk.CTkFont(size=14),
            width=200,
            height=45,
            command=lambda: self.app.show_view("patch_clamp") if self.app else None
        )
        patch_btn.grid(row=0, column=1, padx=10, pady=5)
        
        # Footer con información
        self.footer = ctk.CTkLabel(
            self,
            text="Desarrollado como recurso educativo complementario para la enseñanza de la Biofísica",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.footer.grid(row=5, column=0, pady=(40, 10))
    
    def _create_module_card(
        self,
        icon: str,
        title: str,
        description: str,
        view_name: str
    ) -> ctk.CTkFrame:
        """Crea una tarjeta de módulo."""
        card = ctk.CTkFrame(self.modules_frame, corner_radius=10)
        card.grid_columnconfigure(0, weight=1)
        
        # Icono
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=32)
        )
        icon_label.grid(row=0, column=0, pady=(15, 5))
        
        # Título
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        title_label.grid(row=1, column=0, pady=5)
        
        # Descripción
        desc_label = ctk.CTkLabel(
            card,
            text=description,
            font=ctk.CTkFont(size=11),
            text_color="gray",
            wraplength=180
        )
        desc_label.grid(row=2, column=0, pady=5, padx=10)
        
        # Botón de acceso
        btn = ctk.CTkButton(
            card,
            text="Acceder →",
            font=ctk.CTkFont(size=12),
            width=100,
            height=30,
            command=lambda: self.app.show_view(view_name) if self.app else None
        )
        btn.grid(row=3, column=0, pady=(10, 15))
        
        return card
