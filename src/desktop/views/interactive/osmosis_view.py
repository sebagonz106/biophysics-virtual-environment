"""
Vista interactiva del módulo de Ósmosis.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional

from ...components.input_form import InputForm, FormField
from ...components.result_panel import ResultPanel
from ...components.plot_canvas import PlotCanvas


class OsmosisView(ctk.CTkFrame):
    """
    Vista interactiva para el módulo de Ósmosis.
    
    Permite calcular:
    - Osmolaridad de soluciones
    - Clasificación de tonicidad
    - Cambios de volumen celular (Boyle-van't Hoff)
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
        # Header
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
            text="Osmolaridad, Tonicidad y Ley de Boyle-van't Hoff",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, sticky="w")
        
        # Panel principal con PanedWindow horizontal
        self.main_paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=6,
            sashrelief=tk.RAISED,
            bg="#3a3a3a"
        )
        self.main_paned.grid(row=1, column=0, sticky="nsew")
        
        # Panel izquierdo - Tabs de cálculos (scrollable)
        left_frame = ctk.CTkFrame(self.main_paned)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        
        self.tabs = ctk.CTkTabview(left_frame, width=380)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.tab_osmolarity = self.tabs.add("Osmolaridad")
        self.tab_volume = self.tabs.add("Volumen Celular")
        
        self._setup_osmolarity_tab()
        self._setup_volume_tab()
        
        # Panel derecho con PanedWindow vertical para resultados/gráficos
        right_outer = ctk.CTkFrame(self.main_paned)
        right_outer.grid_columnconfigure(0, weight=1)
        right_outer.grid_rowconfigure(0, weight=1)
        
        # PanedWindow vertical para redimensionar resultados vs gráfico
        self.right_paned = tk.PanedWindow(
            right_outer,
            orient=tk.VERTICAL,
            sashwidth=6,
            sashrelief=tk.RAISED,
            bg="#3a3a3a"
        )
        self.right_paned.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Panel de resultados (scrollable)
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
        
        # Añadir paneles al PanedWindow vertical
        self.right_paned.add(result_container, minsize=150, stretch="always")
        self.right_paned.add(plot_container, minsize=200, stretch="always")
        
        # Añadir paneles al PanedWindow horizontal
        self.main_paned.add(left_frame, minsize=350, stretch="always")
        self.main_paned.add(right_outer, minsize=400, stretch="always")
    
    def _setup_osmolarity_tab(self):
        """Configura el tab de osmolaridad."""
        self.tab_osmolarity.grid_columnconfigure(0, weight=1)
        
        # Información
        info = ctk.CTkLabel(
            self.tab_osmolarity,
            text="Calcular la osmolaridad de una solución\n"
                 "Fórmula: Osm = n × C",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        info.grid(row=0, column=0, sticky="w", pady=(10, 15))
        
        # Formulario
        self.osm_form = InputForm(
            self.tab_osmolarity,
            title="Datos de la Solución",
            fields=[
                FormField("solute", "Soluto (nombre)", "entry", "NaCl"),
                FormField(
                    "solute_type", "Tipo de soluto", "combobox",
                    options=["NaCl", "Glucosa", "CaCl₂", "KCl", "Urea", "MgCl₂", "Sacarosa", "Otro"]
                ),
                FormField("concentration", "Concentración (mM)", "entry", "150"),
                FormField("coefficient", "Coef. osmótico (g)", "entry", "1.0",
                         tooltip="Opcional. Dejar en 1.0 para usar valor automático"),
                FormField("num_particles", "Nº partículas (n)", "entry", "",
                         tooltip="Opcional. Dejar vacío para usar valor automático"),
            ],
            on_submit=self._calculate_osmolarity,
            submit_text="Calcular Osmolaridad"
        )
        self.osm_form.grid(row=1, column=0, sticky="ew", padx=5)
        
        # Ejemplos clínicos
        examples_frame = ctk.CTkFrame(self.tab_osmolarity)
        examples_frame.grid(row=2, column=0, sticky="ew", pady=15, padx=5)
        
        ctk.CTkLabel(
            examples_frame,
            text="📋 Ejemplos Clínicos:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        examples = [
            ("Solución Salina 0.9%", "NaCl", "154"),
            ("Dextrosa 5%", "Glucosa", "278"),
            ("Lactato Ringer", "NaCl", "130"),
        ]
        
        for i, (name, solute, conc) in enumerate(examples):
            btn = ctk.CTkButton(
                examples_frame,
                text=name,
                width=140,
                height=28,
                command=lambda s=solute, c=conc: self._set_osmolarity_example(s, c)
            )
            btn.grid(row=1, column=i, padx=5, pady=(5, 10))
    
    def _setup_volume_tab(self):
        """Configura el tab de volumen celular."""
        self.tab_volume.grid_columnconfigure(0, weight=1)
        
        # Información
        info = ctk.CTkLabel(
            self.tab_volume,
            text="Calcular cambios de volumen celular\n"
                 "Ley de Boyle-van't Hoff: V = Vb + Va(πi/πe)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        info.grid(row=0, column=0, sticky="w", pady=(10, 15))
        
        # Formulario
        self.vol_form = InputForm(
            self.tab_volume,
            title="Datos del Sistema",
            fields=[
                FormField("initial_volume", "Volumen inicial (μm³)", "entry", "1000"),
                FormField("non_osmotic_fraction", "Fracción no osmótica (b)", "entry", "0.4",
                         tooltip="Típicamente 0.3-0.4 para células"),
                FormField("internal_osmolarity", "Osmolaridad interna (mOsm)", "entry", "300"),
                FormField("external_osmolarity", "Osmolaridad externa (mOsm)", "entry", "300"),
            ],
            on_submit=self._calculate_volume,
            submit_text="Calcular Volumen Final"
        )
        self.vol_form.grid(row=1, column=0, sticky="ew", padx=5)
        
        # Escenarios
        scenarios_frame = ctk.CTkFrame(self.tab_volume)
        scenarios_frame.grid(row=2, column=0, sticky="ew", pady=15, padx=5)
        
        ctk.CTkLabel(
            scenarios_frame,
            text="🧪 Escenarios:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        scenarios = [
            ("Isotónico", "300", "300"),
            ("Hipotónico", "300", "150"),
            ("Hipertónico", "300", "600"),
        ]
        
        for i, (name, pi, pe) in enumerate(scenarios):
            btn = ctk.CTkButton(
                scenarios_frame,
                text=name,
                width=100,
                height=28,
                command=lambda internal=pi, external=pe: self._set_volume_example(internal, external)
            )
            btn.grid(row=1, column=i, padx=5, pady=(5, 10))
    
    def _calculate_osmolarity(self, data: dict):
        """Calcula la osmolaridad."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener valores
            solute_type = data.get("solute_type", "NaCl")
            concentration = float(data.get("concentration", 0))
            
            # Coeficiente y partículas opcionales
            g = data.get("coefficient", "1.0")
            g = float(g) if g and g != "1.0" else None
            
            n = data.get("num_particles", "")
            n = int(n) if n else None
            
            # Calcular
            result = self.solver_service.calculate_osmolarity(
                solute_name=solute_type,
                concentration_mM=concentration,
                g=g,
                n=n
            )
            
            # Mostrar resultados
            results_data = {
                "Osmolaridad": f"{result.osmolarity:.2f} mOsm/L",
                "Concentración": f"{result.concentration_mM:.2f} mM",
                "Nº partículas (n)": str(result.n),
                "Coef. osmótico (g)": f"{result.g:.2f}",
                "Clasificación": result.tonicity_classification or "N/A"
            }
            
            self.result_panel.show_results(
                title="📊 Resultados de Osmolaridad",
                results=results_data,
                interpretation=result.clinical_interpretation,
                feedback=result.feedback
            )
            
            # Mostrar comparación visual
            plasma_osm = 280  # mOsm/L referencia
            self.plot_canvas.clear()
            self.plot_canvas.ax.bar(
                ["Solución", "Plasma (ref)"],
                [result.osmolarity or 0.0, plasma_osm],
                color=["steelblue", "coral"]
            )
            self.plot_canvas.ax.set_ylabel("Osmolaridad (mOsm/L)")
            self.plot_canvas.ax.set_title("Comparación con Plasma")
            self.plot_canvas.ax.axhline(y=plasma_osm, color="coral", linestyle="--", alpha=0.5)
            self.plot_canvas.draw()
            
        except ValueError as e:
            self.result_panel.show_error(f"Error en los datos: {e}")
        except Exception as e:
            self.result_panel.show_error(f"Error de cálculo: {e}")
    
    def _calculate_volume(self, data: dict):
        """Calcula el volumen celular final."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener valores
            v0 = float(data.get("initial_volume", 1000))
            b = float(data.get("non_osmotic_fraction", 0.4))
            pi = float(data.get("internal_osmolarity", 300))
            pe = float(data.get("external_osmolarity", 300))
            
            # Calcular
            result = self.solver_service.calculate_cell_volume(
                initial_volume=v0,
                internal_osmolarity=pi,
                external_osmolarity=pe,
                non_osmotic_fraction=b
            )
            
            # Mostrar resultados
            volume_change_pct = ((result.final_volume / result.initial_volume) - 1) * 100
            
            results_data = {
                "Volumen inicial": f"{result.initial_volume:.2f} μm³",
                "Volumen final": f"{result.final_volume:.2f} μm³",
                "Cambio de volumen": f"{volume_change_pct:+.1f}%",
                "Osmolaridad interna": f"{result.internal_osmolarity:.1f} mOsm",
                "Osmolaridad externa": f"{result.external_osmolarity:.1f} mOsm",
                "Estado": result.tonicity or "N/A"
            }
            
            self.result_panel.show_results(
                title="📊 Resultados de Volumen Celular",
                results=results_data,
                interpretation=result.interpretation,
                feedback=result.feedback
            )
            
            # Graficar curva de volumen
            self.plot_canvas.plot_boyle_vant_hoff_params(
                initial_volume=v0,
                non_osmotic_fraction=b,
                internal_osmolarity=pi,
                external_osmolarity_current=pe
            )
            
        except ValueError as e:
            self.result_panel.show_error(f"Error en los datos: {e}")
        except Exception as e:
            self.result_panel.show_error(f"Error de cálculo: {e}")
    
    def _set_osmolarity_example(self, solute: str, concentration: str):
        """Establece valores de ejemplo para osmolaridad."""
        self.osm_form.set_value("solute_type", solute)
        self.osm_form.set_value("concentration", concentration)
    
    def _set_volume_example(self, internal: str, external: str):
        """Establece valores de ejemplo para volumen."""
        self.vol_form.set_value("internal_osmolarity", internal)
        self.vol_form.set_value("external_osmolarity", external)
