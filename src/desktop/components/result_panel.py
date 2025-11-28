"""
Panel para mostrar resultados de cálculos.
"""

import customtkinter as ctk
from typing import List, Optional, Dict


class ResultPanel(ctk.CTkFrame):
    """
    Panel para mostrar resultados de cálculos y retroalimentación.
    Incluye scroll y es redimensionable.
    """
    
    def __init__(
        self,
        master,
        title: str = "Resultados",
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.title = title
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del panel."""
        # Configurar grid para expandir
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header con título
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=30)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            header_frame,
            text=self.title,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        # Área scrollable principal
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=("gray70", "gray30"),
            scrollbar_button_hover_color=("gray60", "gray40")
        )
        self.scroll_frame.grid(row=1, column=0, sticky="nsew")
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Frame de resultado principal
        self.result_frame = ctk.CTkFrame(self.scroll_frame, fg_color=("gray90", "gray20"))
        self.result_frame.grid(row=0, column=0, sticky="ew", pady=5, padx=2)
        self.result_frame.grid_columnconfigure(0, weight=1)
        
        self.main_result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=380,
            justify="left"
        )
        self.main_result_label.grid(row=0, column=0, padx=15, pady=15, sticky="w")
        
        # Frame de interpretación
        self.interpretation_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.interpretation_frame.grid(row=1, column=0, sticky="ew", pady=10, padx=2)
        self.interpretation_frame.grid_columnconfigure(0, weight=1)
        
        self.interpretation_title = ctk.CTkLabel(
            self.interpretation_frame,
            text="💡 Interpretación:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.interpretation_title.grid(row=0, column=0, sticky="w")
        
        self.interpretation_text = ctk.CTkLabel(
            self.interpretation_frame,
            text="",
            font=ctk.CTkFont(size=12),
            wraplength=380,
            justify="left"
        )
        self.interpretation_text.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Frame de retroalimentación/detalles
        self.feedback_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        self.feedback_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=2)
        self.feedback_frame.grid_columnconfigure(0, weight=1)
        
        self.feedback_title = ctk.CTkLabel(
            self.feedback_frame,
            text="📋 Detalles:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.feedback_title.grid(row=0, column=0, sticky="w")
        
        # Textbox para feedback con scroll propio
        self.feedback_text = ctk.CTkTextbox(
            self.feedback_frame,
            height=120,
            font=ctk.CTkFont(size=11),
            wrap="word",
            scrollbar_button_color=("gray70", "gray30")
        )
        self.feedback_text.grid(row=1, column=0, sticky="ew", pady=(5, 0))
        
        # Inicialmente oculto
        self.hide()
    
    def show_result(
        self,
        main_result: str,
        interpretation: Optional[str] = None,
        feedback: Optional[List[str]] = None,
        result_color: Optional[str] = None
    ):
        """
        Muestra un resultado.
        
        Args:
            main_result: Resultado principal a mostrar
            interpretation: Interpretación del resultado
            feedback: Lista de puntos de retroalimentación
            result_color: Color del resultado (success, warning, error)
        """
        # Mostrar panel
        self.show()
        
        # Configurar color
        if result_color == "success":
            fg_color = ("#d4edda", "#1e4620")
            text_color = ("#155724", "#98d19e")
        elif result_color == "warning":
            fg_color = ("#fff3cd", "#4a3f06")
            text_color = ("#856404", "#ffc107")
        elif result_color == "error":
            fg_color = ("#f8d7da", "#4a1a1d")
            text_color = ("#721c24", "#f5c6cb")
        else:
            fg_color = ("gray90", "gray20")
            text_color = ("gray10", "gray90")
        
        self.result_frame.configure(fg_color=fg_color)
        self.main_result_label.configure(text=main_result, text_color=text_color)
        
        # Interpretación
        if interpretation:
            self.interpretation_text.configure(text=interpretation)
            self.interpretation_frame.grid()
        else:
            self.interpretation_frame.grid_remove()
        
        # Retroalimentación
        if feedback:
            self.feedback_text.configure(state="normal")
            self.feedback_text.delete("1.0", "end")
            for line in feedback:
                self.feedback_text.insert("end", f"• {line}\n\n")
            self.feedback_text.configure(state="disabled")
            self.feedback_frame.grid()
        else:
            self.feedback_frame.grid_remove()
    
    def show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.show_result(
            main_result=f"❌ Error: {message}",
            result_color="error"
        )

    def show_results(
        self,
        title: Optional[str] = None,
        results: Optional[Dict] = None,
        interpretation: Optional[str] = None,
        feedback: Optional[List[str]] = None
    ):
        """
        Muestra resultados con formato de tabla.
        
        Args:
            title: Título del panel (opcional)
            results: Diccionario de resultados {nombre: valor}
            interpretation: Texto de interpretación
            feedback: Lista de puntos de retroalimentación
        """
        if title:
            self.title_label.configure(text=title)
        
        # Formatear resultados como texto estructurado
        main_text = ""
        if results:
            for key, value in results.items():
                main_text += f"▸ {key}: {value}\n"
        
        self.show_result(
            main_result=main_text.strip() if main_text else "Sin resultados",
            interpretation=interpretation,
            feedback=feedback
        )
    
    def clear(self):
        """Limpia el panel."""
        self.main_result_label.configure(text="")
        self.interpretation_text.configure(text="")
        self.feedback_text.configure(state="normal")
        self.feedback_text.delete("1.0", "end")
        self.feedback_text.configure(state="disabled")
    
    def hide(self):
        """Oculta el panel."""
        self.grid_remove()
    
    def show(self):
        """Muestra el panel."""
        self.grid()
