"""
Vista interactiva del módulo de Ósmosis.

Esta vista proporciona una interfaz para:
- Comparar osmolaridades intracelular y extracelular
- Clasificar soluciones por osmolaridad y tonicidad
- Visualizar dinámica de volumen celular
- Detectar condiciones de lisis
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional, List, Dict

from ...components.input_form import InputForm, FormField
from ...components.result_panel import ResultPanel
from ...components.plot_canvas import PlotCanvas
from ...components.solute_widgets import SoluteSection

from .osmosis_plotting import (
    plot_osmolarity_comparison,
    plot_lysis_comparison,
    plot_volume_dynamics,
    plot_volume_dynamics_lysis,
)


class OsmosisView(ctk.CTkFrame):
    """
    Vista interactiva para el módulo de Ósmosis.
    
    Permite calcular:
    - Osmolaridad de soluciones
    - Clasificación de tonicidad
    - Cambios de volumen celular (Boyle-van't Hoff)
    - Comparación de osmolaridades intra/extracelular
    """
    
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app = app
        self.solver_service = app.solver_service if app else None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        self._create_header()
        self._create_main_panels()
    
    def _create_header(self):
        """Crea el header de la vista."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        self.title = ctk.CTkLabel(
            header,
            text="💧 Módulo Interactivo de Ósmosis",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(
            header,
            text="Comparación de Osmolaridades y Clasificación Tónica",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, sticky="w")
    
    def _create_main_panels(self):
        """Crea los paneles principales de la vista."""
        # Panel principal con PanedWindow horizontal
        self.main_paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            sashrelief=tk.RAISED,
            bg="#3a3a3a"
        )
        self.main_paned.grid(row=1, column=0, sticky="nsew")
        
        # Panel izquierdo - Tabs de cálculos
        left_frame = ctk.CTkFrame(self.main_paned)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        
        self.tabs = ctk.CTkTabview(left_frame, width=420)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.tab_comparison = self.tabs.add("Comparación")
        self._setup_comparison_tab()
        
        # Panel derecho con PanedWindow vertical
        right_outer = ctk.CTkFrame(self.main_paned)
        right_outer.grid_columnconfigure(0, weight=1)
        right_outer.grid_rowconfigure(0, weight=1)
        
        self.right_paned = tk.PanedWindow(
            right_outer,
            orient=tk.VERTICAL,
            sashwidth=6,
            sashrelief=tk.RAISED,
            bg="#3a3a3a"
        )
        self.right_paned.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Panel de resultados
        result_container = ctk.CTkFrame(self.right_paned)
        result_container.grid_columnconfigure(0, weight=1)
        result_container.grid_rowconfigure(0, weight=1)
        
        self.result_panel = ResultPanel(result_container)
        self.result_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Panel del gráfico
        plot_container = ctk.CTkFrame(self.right_paned)
        plot_container.grid_columnconfigure(0, weight=1)
        plot_container.grid_rowconfigure(0, weight=1)
        
        self.plot_canvas = PlotCanvas(plot_container, figsize=(5, 3.5))
        self.plot_canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Añadir paneles
        self.right_paned.add(result_container, minsize=150, stretch="always")
        self.right_paned.add(plot_container, minsize=200, stretch="always")
        
        self.main_paned.add(left_frame, minsize=400, stretch="always")
        self.main_paned.add(right_outer, minsize=400, stretch="always")
    
    def _setup_comparison_tab(self):
        """Configura el tab de comparación de osmolaridades."""
        self.tab_comparison.grid_columnconfigure(0, weight=1)
        self.tab_comparison.grid_rowconfigure(1, weight=1)
        
        # Información
        info = ctk.CTkLabel(
            self.tab_comparison,
            text="Comparar osmolaridades intra y extracelular\n"
                 "Clasifica por osmolaridad total y presión osmótica real",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        info.grid(row=0, column=0, sticky="w", pady=(10, 10))
        
        # Scrollable frame para las secciones
        scroll_frame = ctk.CTkScrollableFrame(
            self.tab_comparison,
            fg_color="transparent"
        )
        scroll_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Sección intracelular
        self.internal_section = SoluteSection(
            scroll_frame,
            title="🔵 Solutos Intracelulares"
        )
        self.internal_section.grid(row=0, column=0, sticky="ew", pady=5, padx=5)
        
        # Sección extracelular
        self.external_section = SoluteSection(
            scroll_frame,
            title="🟢 Solutos Extracelulares"
        )
        self.external_section.grid(row=1, column=0, sticky="ew", pady=10, padx=5)
        
        # Campo de volumen crítico para lisis
        self._create_lysis_controls(scroll_frame)
        
        # Botón calcular
        btn_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", pady=10)
        
        self.compare_btn = ctk.CTkButton(
            btn_frame,
            text="⚖️ Comparar Osmolaridades",
            width=200,
            height=35,
            command=self._calculate_comparison
        )
        self.compare_btn.grid(row=0, column=0, pady=10)
        
        # Opciones de visualización
        self._create_visualization_options(scroll_frame)
        
        # Ejemplos rápidos
        self._create_examples_section(scroll_frame)
    
    def _create_lysis_controls(self, parent):
        """Crea los controles para configuración de lisis."""
        lysis_frame = ctk.CTkFrame(parent)
        lysis_frame.grid(row=2, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            lysis_frame,
            text="⚠️ Volumen crítico (Vf/V₀):",
            font=ctk.CTkFont(size=11)
        ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
        
        self.critical_volume_entry = ctk.CTkEntry(
            lysis_frame,
            width=60,
            placeholder_text="2.0"
        )
        self.critical_volume_entry.grid(row=0, column=1, padx=5, pady=8)
        self.critical_volume_entry.insert(0, "2.0")
        
        ctk.CTkLabel(
            lysis_frame,
            text="(Si V/V₀ > este valor → lisis)",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).grid(row=0, column=2, sticky="w", padx=5, pady=8)
    
    def _create_visualization_options(self, parent):
        """Crea las opciones de visualización."""
        options_frame = ctk.CTkFrame(parent)
        options_frame.grid(row=4, column=0, sticky="ew", pady=(5, 10), padx=5)
        
        ctk.CTkLabel(
            options_frame,
            text="🔧 Opciones de visualización:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        self.show_volume_dynamics = ctk.BooleanVar(value=False)
        
        self.volume_dynamics_switch = ctk.CTkSwitch(
            options_frame,
            text="Gráfica de Volumen vs Tiempo (dinámica)",
            variable=self.show_volume_dynamics,
            onvalue=True,
            offvalue=False,
            font=ctk.CTkFont(size=11)
        )
        self.volume_dynamics_switch.grid(row=1, column=0, sticky="w", padx=15, pady=(5, 10))
    
    def _create_examples_section(self, parent):
        """Crea la sección de ejemplos."""
        examples_frame = ctk.CTkFrame(parent)
        examples_frame.grid(row=5, column=0, sticky="ew", pady=5, padx=5)
        
        ctk.CTkLabel(
            examples_frame,
            text="📋 Ejemplos:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        examples = [
            ("Isotónico", self._set_example_isotonic),
            ("Sol. Salina 3%", self._set_example_hypertonic),
            ("Urea en sangre", self._set_example_urea),
        ]
        
        for i, (name, callback) in enumerate(examples):
            btn = ctk.CTkButton(
                examples_frame,
                text=name,
                width=120,
                height=28,
                command=callback
            )
            btn.grid(row=1, column=i, padx=5, pady=(5, 10))
    
    def _calculate_comparison(self):
        """Calcula la comparación de osmolaridades."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener solutos
            internal_solutes = self.internal_section.get_all_solutes()
            external_solutes = self.external_section.get_all_solutes()
            
            if not internal_solutes or not external_solutes:
                self.result_panel.show_error(
                    "Agregue al menos un soluto en cada compartimento"
                )
                return
            
            # Obtener volumen crítico
            try:
                critical_volume = float(self.critical_volume_entry.get() or 2.0)
            except ValueError:
                critical_volume = 2.0
            
            # Calcular
            result = self.solver_service.compare_osmolarities(
                internal_solutes=internal_solutes,
                external_solutes=external_solutes
            )
            
            # Detectar lisis
            lysis_detected, lysis_reason = self._check_lysis_conditions(
                result, critical_volume
            )
            
            if lysis_detected:
                self._show_lysis_results(
                    result, critical_volume, lysis_reason,
                    internal_solutes, external_solutes
                )
            else:
                self._show_normal_results(
                    result, internal_solutes, external_solutes
                )
            
        except Exception as e:
            self.result_panel.show_error(f"Error de cálculo: {e}")
    
    def _check_lysis_conditions(self, result, critical_volume: float) -> tuple:
        """
        Verifica condiciones de lisis.
        
        Returns:
            Tuple (lysis_detected: bool, reason: str)
        """
        # Caso A: Presión osmótica real extracelular = 0
        if result.external_effective_osmolarity <= 0:
            return True, "π real extracelular = 0 (sin solutos no penetrantes externos)"
        
        # Caso B: Coeficiente > volumen crítico
        if result.effective_osmolarity_ratio > critical_volume:
            return True, (
                f"Coef. π real ({result.effective_osmolarity_ratio:.2f}) > "
                f"Volumen crítico ({critical_volume:.2f})"
            )
        
        return False, ""
    
    def _show_lysis_results(
        self, result, critical_volume: float, lysis_reason: str,
        internal_solutes: List[Dict], external_solutes: List[Dict]
    ):
        """Muestra resultados cuando hay lisis."""
        results_data = {
            "⚠️ LISIS CELULAR": "DETECTADA",
            "━━━━━━━━━━━━━━━━━━━": "",
            "Razón": lysis_reason,
            "━━━━━━━━━━━━━━━━━━": "",
            "Osm. Intracelular Total": f"{result.internal_osmolarity:.1f} mOsm/L",
            "Osm. Extracelular Total": f"{result.external_osmolarity:.1f} mOsm/L",
            "π Real Intracelular": f"{result.internal_effective_osmolarity:.1f} mOsm/L",
            "π Real Extracelular": f"{result.external_effective_osmolarity:.1f} mOsm/L",
            "Coef. π Real": f"{result.effective_osmolarity_ratio:.4f}",
            "Volumen crítico": f"{critical_volume:.2f}",
        }
        
        lysis_interpretation = (
            "⚠️ LISIS CELULAR INMINENTE\n\n"
            f"Causa: {lysis_reason}\n\n"
            "La célula no puede soportar el gradiente osmótico y la membrana "
            "se romperá debido a la entrada excesiva de agua.\n\n"
            "En estas condiciones, no tiene sentido clasificar la solución "
            "por osmolaridad o tonicidad, ya que el resultado es la destrucción celular."
        )
        
        self.result_panel.show_results(
            title="💀 Lisis Celular Detectada",
            results=results_data,
            interpretation=lysis_interpretation,
            feedback=["⚠️ La célula lisará antes de alcanzar el equilibrio osmótico"]
        )
        
        # Graficar
        if self.show_volume_dynamics.get():
            plot_volume_dynamics_lysis(
                self.plot_canvas.figure,
                result, internal_solutes, external_solutes, critical_volume
            )
        else:
            plot_lysis_comparison(
                self.plot_canvas.figure,
                result, critical_volume
            )
        self.plot_canvas.draw()
    
    def _show_normal_results(
        self, result,
        internal_solutes: List[Dict], external_solutes: List[Dict]
    ):
        """Muestra resultados normales (sin lisis)."""
        results_data = {
            "Osm. Intracelular Total": f"{result.internal_osmolarity:.1f} mOsm/L",
            "Osm. Extracelular Total": f"{result.external_osmolarity:.1f} mOsm/L",
            "π Real Intracelular": f"{result.internal_effective_osmolarity:.1f} mOsm/L",
            "π Real Extracelular": f"{result.external_effective_osmolarity:.1f} mOsm/L",
            "━━━━━━━━━━━━━━━━━━━": "",
            "Clasificación Osmótica": result.osmotic_classification,
            "━━━━━━━━━━━━━━━━━━": "",
            "Coef. π Real": f"{result.effective_osmolarity_ratio:.4f}",
            "Clasificación Tónica": result.tonic_classification,
        }
        
        self.result_panel.show_results(
            title="⚖️ Comparación de Osmolaridades",
            results=results_data,
            interpretation=result.interpretation,
            feedback=result.feedback
        )
        
        # Graficar
        if self.show_volume_dynamics.get():
            plot_volume_dynamics(
                self.plot_canvas.figure,
                result, internal_solutes, external_solutes
            )
        else:
            plot_osmolarity_comparison(
                self.plot_canvas.figure,
                result
            )
        self.plot_canvas.draw()
    
    # ==================== Ejemplos ====================
    
    def _set_example_isotonic(self):
        """Ejemplo de solución isotónica."""
        self.internal_section.clear_all()
        self.external_section.clear_all()
        
        self.result_panel.show_info(
            "Ejemplo Isotónico",
            "Configure manualmente:\n"
            "• Intracelular: KCl 140mM, otras sales\n"
            "• Extracelular: NaCl 140mM (Osm ≈ 280 mOsm/L)\n\n"
            "La célula mantiene su volumen cuando las\n"
            "osmolaridades efectivas son iguales."
        )
    
    def _set_example_hypertonic(self):
        """Ejemplo de solución salina hipertónica (3%)."""
        self.result_panel.show_info(
            "Solución Salina al 3%",
            "Configure manualmente:\n"
            "• Intracelular: NaCl ~140mM (Osm ≈ 280 mOsm/L)\n"
            "• Extracelular: NaCl ~513mM (Osm ≈ 1026 mOsm/L)\n\n"
            "La célula perderá agua (solución hipertónica)\n"
            "El volumen final será menor que el inicial."
        )
    
    def _set_example_urea(self):
        """Ejemplo con urea (penetrante)."""
        self.result_panel.show_info(
            "Efecto de la Urea",
            "Configure manualmente:\n"
            "• Agregue urea (300mM) al medio extracelular\n"
            "• Marque urea como penetrante (P)\n\n"
            "La urea atraviesa la membrana, por lo que\n"
            "aunque aumenta la osmolaridad total,\n"
            "no afecta la tonicidad (volumen celular).\n\n"
            "⚡ Hiperosmótico pero Isotónico"
        )
