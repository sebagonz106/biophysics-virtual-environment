"""
Barra lateral de navegación.
"""

import customtkinter as ctk
from typing import Callable, Optional
from PIL import Image
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import APP_LOGO


class Sidebar(ctk.CTkFrame):
    """
    Barra lateral de navegación con los módulos principales.
    """
    
    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        **kwargs
    ):
        super().__init__(master, width=200, corner_radius=0, **kwargs)
        
        self.on_navigate = on_navigate
        self.buttons = {}
        self.active_button = None
        
        # Configurar grid
        self.grid_rowconfigure(10, weight=1)  # Espaciador
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del sidebar."""
        # Logo de la aplicación
        self._create_logo()
    
    def _create_logo(self):
        """Crea y muestra el logo en el sidebar."""
        try:
            if APP_LOGO.exists():
                # Cargar imagen
                logo_image = Image.open(APP_LOGO)
                # Redimensionar para el sidebar (ancho máximo ~160px)
                max_width = 160
                ratio = max_width / logo_image.width
                new_height = int(logo_image.height * ratio)
                logo_image = logo_image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                
                # Crear CTkImage
                self.logo_ctk = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=(max_width, new_height)
                )
                
                # Mostrar logo
                self.logo_label = ctk.CTkLabel(
                    self,
                    image=self.logo_ctk,
                    text=""
                )
                self.logo_label.grid(row=0, column=0, padx=10, pady=(15, 5))
            else:
                self._create_text_logo()
        except Exception:
            self._create_text_logo()
        
        # Continuar con el resto de widgets
        self._create_nav_widgets()
    
    def _create_text_logo(self):
        """Crea el logo como texto (fallback)."""
        self.logo_label = ctk.CTkLabel(
            self,
            text="🧬 Biofísica",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.subtitle = ctk.CTkLabel(
            self,
            text="Entorno Virtual",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, padx=20, pady=(0, 20))
    
    def _create_nav_widgets(self):
        """Crea los widgets de navegación."""
        
        # Separador
        self.separator1 = ctk.CTkFrame(self, height=2, fg_color="gray70")
        self.separator1.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Botones de navegación principal
        nav_items = [
            ("home", "🏠 Inicio", 2),
            ("conferences", "📖 Conferencias", 3),
            ("bibliography", "📚 Bibliografía", 4),
            ("problems", "📝 Problemas", 5),
        ]
        
        for view_id, text, row in nav_items:
            btn = self._create_nav_button(text, view_id)
            btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
            self.buttons[view_id] = btn
        
        # Separador
        self.separator2 = ctk.CTkFrame(self, height=2, fg_color="gray70")
        self.separator2.grid(row=6, column=0, sticky="ew", padx=10, pady=10)
        
        # Sección Módulos Interactivos
        self.interactive_label = ctk.CTkLabel(
            self,
            text="🧮 Interactivos",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.interactive_label.grid(row=7, column=0, padx=20, pady=(5, 5), sticky="w")
        
        # Botones de módulos interactivos
        interactive_items = [
            ("osmosis", "  💧 Ósmosis", 8),
            ("ionic_equilibrium", "  ⚖️ Equilibrio Iónico", 9),
            ("patch_clamp", "  ⚡ Patch Clamp", 10),
        ]
        
        for view_id, text, row in interactive_items:
            btn = self._create_nav_button(text, view_id)
            btn.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
            self.buttons[view_id] = btn
        
        # Espaciador
        self.spacer = ctk.CTkLabel(self, text="")
        self.spacer.grid(row=11, column=0, sticky="nsew")
        
        # Versión en la parte inferior
        self.version_label = ctk.CTkLabel(
            self,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.version_label.grid(row=12, column=0, padx=20, pady=10)
    
    def _create_nav_button(self, text: str, view_id: str) -> ctk.CTkButton:
        """Crea un botón de navegación."""
        btn = ctk.CTkButton(
            self,
            text=text,
            font=ctk.CTkFont(size=13),
            anchor="w",
            height=35,
            corner_radius=8,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            command=lambda: self._on_button_click(view_id)
        )
        return btn
    
    def _on_button_click(self, view_id: str):
        """Maneja el click en un botón."""
        self.on_navigate(view_id)
    
    def set_active(self, view_id: str):
        """
        Marca un botón como activo.
        
        Args:
            view_id: ID de la vista activa
        """
        # Desactivar botón anterior
        if self.active_button and self.active_button in self.buttons:
            self.buttons[self.active_button].configure(
                fg_color="transparent",
                text_color=("gray10", "gray90")
            )
        
        # Activar nuevo botón
        if view_id in self.buttons:
            self.buttons[view_id].configure(
                fg_color=("gray75", "gray25"),
                text_color=("gray10", "gray90")
            )
            self.active_button = view_id
