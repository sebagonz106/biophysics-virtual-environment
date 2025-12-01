"""
Vista interactiva del módulo de Ósmosis.
"""

import customtkinter as ctk
import tkinter as tk
import numpy as np
from typing import Optional, List, Dict
from scipy.integrate import odeint

from ...components.input_form import InputForm, FormField
from ...components.result_panel import ResultPanel
from ...components.plot_canvas import PlotCanvas


class SoluteEntryRow(ctk.CTkFrame):
    """Fila para entrada de un soluto."""
    
    PREDEFINED_SOLUTES = {
        "NaCl": {"j": 2, "penetrant": False, "permeability": 0.0},
        "KCl": {"j": 2, "penetrant": False, "permeability": 0.0},
        "CaCl₂": {"j": 3, "penetrant": False, "permeability": 0.0},
        "MgCl₂": {"j": 3, "penetrant": False, "permeability": 0.0},
        "NaHCO₃": {"j": 2, "penetrant": False, "permeability": 0.0},
        "Glucosa": {"j": 1, "penetrant": False, "permeability": 0.0},
        "Sacarosa": {"j": 1, "penetrant": False, "permeability": 0.0},
        "Manitol": {"j": 1, "penetrant": False, "permeability": 0.0},
        "Urea": {"j": 1, "penetrant": True, "permeability": 1e-5},
        "Codeina": {"j": 1, "penetrant": True, "permeability": 1e-5},
        "Personalizado": {"j": 1, "penetrant": False, "permeability": 0.0},
    }
    
    def __init__(self, master, on_remove=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_remove = on_remove
        
        # Selector de soluto
        self.solute_var = ctk.StringVar(value="NaCl")
        self.solute_combo = ctk.CTkComboBox(
            self,
            values=list(self.PREDEFINED_SOLUTES.keys()),
            variable=self.solute_var,
            width=105,
            command=self._on_solute_change
        )
        self.solute_combo.grid(row=0, column=0, padx=(0, 8))
        
        # Concentración con label inline
        ctk.CTkLabel(self, text="C:", font=ctk.CTkFont(size=11)).grid(row=0, column=1, padx=(0, 2))
        self.conc_entry = ctk.CTkEntry(self, width=55, placeholder_text="mM")
        self.conc_entry.grid(row=0, column=2, padx=(0, 8))
        self.conc_entry.insert(0, "140")
        
        # Factor j con label inline (editable para personalizado)
        ctk.CTkLabel(self, text="j:", font=ctk.CTkFont(size=11)).grid(row=0, column=3, padx=(0, 2))
        self.j_entry = ctk.CTkEntry(self, width=35, placeholder_text="j")
        self.j_entry.grid(row=0, column=4, padx=(0, 8))
        self.j_entry.insert(0, "2")
        self.j_entry.configure(state="disabled")

        # Permeabilidad (cm/s) - editable para todas las sustancias
        ctk.CTkLabel(self, text="Perm:", font=ctk.CTkFont(size=10)).grid(row=0, column=5, padx=(0, 2))
        self.perm_entry = ctk.CTkEntry(self, width=70, placeholder_text="cm/s")
        self.perm_entry.grid(row=0, column=6, padx=(0, 8))
        self.perm_entry.insert(0, "0.0")

        # Checkbox penetrante con label inline
        ctk.CTkLabel(self, text="P:", font=ctk.CTkFont(size=11)).grid(row=0, column=7, padx=(0, 2))
        self.penetrant_var = ctk.BooleanVar(value=False)
        self.penetrant_check = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.penetrant_var,
            width=20,
            checkbox_width=18,
            checkbox_height=18
        )
        self.penetrant_check.grid(row=0, column=8, padx=(0, 8))
        self.penetrant_check.configure(state="disabled")
        
        # Botón eliminar (columna 9, después de penetrante)
        self.remove_btn = ctk.CTkButton(
            self,
            text="×",
            width=28,
            height=28,
            fg_color="transparent",
            text_color=("#c0392b", "#e74c3c"),
            hover_color=("#fadbd8", "#641e16"),
            command=self._remove
        )
        self.remove_btn.grid(row=0, column=9, padx=(0, 0))
        
        self._on_solute_change(self.solute_var.get())
        
        # Binding para auto-cambiar a Personalizado al modificar checkbox penetrante
        self.penetrant_check.configure(command=self._on_penetrant_change)
    
    def _on_penetrant_change(self):
        """Cambia a Personalizado cuando el usuario modifica el checkbox penetrante."""
        current = self.solute_var.get()
        if current != "Personalizado":
            # Guardar el valor actual de j antes de cambiar
            current_j = self.j_entry.get()
            self.solute_var.set("Personalizado")
            # Habilitar j_entry y penetrant_check, restaurar valor
            self.j_entry.configure(state="normal")
            self.j_entry.delete(0, "end")
            self.j_entry.insert(0, current_j)
            self.penetrant_check.configure(state="normal")
            # Habilitar la entrada de permeabilidad para personalizado
            self.perm_entry.configure(state="normal")
    
    def _on_solute_change(self, choice: str):
        """Actualiza campos según el soluto seleccionado."""
        if choice == "Personalizado":
            self.j_entry.configure(state="normal")
            self.penetrant_check.configure(state="normal")
            # Perm siempre editable
        else:
            info = self.PREDEFINED_SOLUTES.get(choice, {"j": 1, "penetrant": False, "permeability": 0.0})
            self.j_entry.configure(state="normal")
            self.j_entry.delete(0, "end")
            self.j_entry.insert(0, str(info["j"]))
            self.j_entry.configure(state="disabled")
            self.penetrant_var.set(info["penetrant"])
            self.penetrant_check.configure(state="disabled")
            # Rellenar permeabilidad con valor por defecto, pero mantener editable
            perm = info.get("permeability", 0.0)
            self.perm_entry.delete(0, "end")
            self.perm_entry.insert(0, str(perm))
            # perm_entry se mantiene editable para que el usuario pueda modificarlo
    
    def _remove(self):
        """Elimina esta fila."""
        if self.on_remove:
            self.on_remove(self)
        self.destroy()
    
    def get_data(self) -> Dict:
        """Obtiene los datos del soluto."""
        name = self.solute_var.get()
        try:
            conc = float(self.conc_entry.get() or 0)
        except ValueError:
            conc = 0
        try:
            j = int(self.j_entry.get() or 1)
        except ValueError:
            j = 1
        try:
            perm = float(self.perm_entry.get() or 0.0)
        except ValueError:
            perm = 0.0
        
        return {
            "name": name,
            "concentration": conc,
            "j": j,
            "is_penetrant": self.penetrant_var.get(),
            "permeability": perm
        }


class SoluteSection(ctk.CTkFrame):
    """Sección para agregar múltiples solutos."""
    
    def __init__(self, master, title: str, **kwargs):
        super().__init__(master, **kwargs)
        
        self.solute_rows: List[SoluteEntryRow] = []
        
        self.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            header,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        self.add_btn = ctk.CTkButton(
            header,
            text="+ Agregar",
            width=80,
            height=26,
            command=self._add_solute
        )
        self.add_btn.grid(row=0, column=1)
        
        # Contenedor de solutos
        self.solutes_container = ctk.CTkFrame(self, fg_color="transparent")
        self.solutes_container.grid(row=1, column=0, sticky="nsew")
        self.solutes_container.grid_columnconfigure(0, weight=1)
        
        # Agregar un soluto por defecto
        self._add_solute()
    
    def _add_solute(self):
        """Agrega una nueva fila de soluto."""
        row = SoluteEntryRow(self.solutes_container, on_remove=self._remove_solute)
        row.grid(row=len(self.solute_rows), column=0, sticky="ew", pady=2)
        self.solute_rows.append(row)
    
    def _remove_solute(self, row: SoluteEntryRow):
        """Elimina una fila de soluto."""
        if row in self.solute_rows:
            self.solute_rows.remove(row)
    
    def get_all_solutes(self) -> List[Dict]:
        """Obtiene datos de todos los solutos."""
        return [row.get_data() for row in self.solute_rows if row.winfo_exists()]
    
    def clear_all(self):
        """Elimina todos los solutos."""
        for row in self.solute_rows[:]:
            row.destroy()
        self.solute_rows.clear()
        self._add_solute()


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
            text="Comparación de Osmolaridades y Clasificación Tónica",
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
        
        self.tabs = ctk.CTkTabview(left_frame, width=420)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.tab_comparison = self.tabs.add("Comparación")
        
        self._setup_comparison_tab()
        
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
        self.main_paned.add(left_frame, minsize=400, stretch="always")
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
        lysis_frame = ctk.CTkFrame(scroll_frame)
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
        
        # Frame para opciones de visualización
        options_frame = ctk.CTkFrame(scroll_frame)
        options_frame.grid(row=4, column=0, sticky="ew", pady=(5, 10), padx=5)
        
        ctk.CTkLabel(
            options_frame,
            text="🔧 Opciones de visualización:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Variable para el switch de gráfica de volumen vs tiempo
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
        
        # Ejemplos rápidos
        examples_frame = ctk.CTkFrame(scroll_frame)
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
    
    def _calculate_comparison(self):
        """Calcula la comparación de osmolaridades."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener solutos
            internal_solutes = self.internal_section.get_all_solutes()
            external_solutes = self.external_section.get_all_solutes()
            
            # Validar que haya al menos un soluto en cada compartimento
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
            
            # Detectar condiciones de lisis
            lysis_detected = False
            lysis_reason = ""
            
            # Caso A: Presión osmótica real extracelular = 0
            if result.external_effective_osmolarity <= 0:
                lysis_detected = True
                lysis_reason = "π real extracelular = 0 (sin solutos no penetrantes externos)"
            
            # Caso B: Coeficiente > volumen crítico (célula se hincharía demasiado)
            elif result.effective_osmolarity_ratio > critical_volume:
                lysis_detected = True
                lysis_reason = f"Coef. π real ({result.effective_osmolarity_ratio:.2f}) > Volumen crítico ({critical_volume:.2f})"
            
            if lysis_detected:
                # Mostrar resultados de lisis
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
                
                # Graficar lisis
                if self.show_volume_dynamics.get():
                    self._plot_volume_dynamics_lysis(result, internal_solutes, external_solutes, critical_volume)
                else:
                    self._plot_comparison_lysis(result, critical_volume)
            else:
                # Mostrar resultados normales
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
                
                # Graficar según el switch
                if self.show_volume_dynamics.get():
                    self._plot_volume_dynamics(result, internal_solutes, external_solutes)
                else:
                    self._plot_comparison(result)
            
        except Exception as e:
            self.result_panel.show_error(f"Error de cálculo: {e}")
    
    def _plot_comparison(self, result):
        """Grafica la comparación de osmolaridades."""
        import matplotlib.pyplot as plt
        
        self.plot_canvas.clear()
        
        # Crear subplots
        fig = self.plot_canvas.figure
        fig.clear()
        
        # Subplot 1: Barras de osmolaridad
        ax1 = fig.add_subplot(1, 2, 1)
        
        x = [0, 1]
        width = 0.35
        
        # Barras de osmolaridad total
        total_bars = ax1.bar(
            [i - width/2 for i in x],
            [result.internal_osmolarity, result.external_osmolarity],
            width,
            label='Total',
            color=['#4a90d9', '#5cb85c'],
            alpha=0.8
        )
        
        # Barras de presión osmótica real
        eff_bars = ax1.bar(
            [i + width/2 for i in x],
            [result.internal_effective_osmolarity, result.external_effective_osmolarity],
            width,
            label='π Real',
            color=['#2a6099', '#3c783c'],
            alpha=0.8
        )
        
        ax1.set_ylabel('Osmolaridad (mOsm/L)')
        ax1.set_title('Comparación de Osmolaridades')
        ax1.set_xticks(x)
        ax1.set_xticklabels(['Intracelular', 'Extracelular'])
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Visualización del coeficiente
        ax2 = fig.add_subplot(1, 2, 2)
        
        # Mostrar el coeficiente como un indicador
        coef = result.effective_osmolarity_ratio
        
        # Determinar color según clasificación
        if result.tonic_classification == "Hipertónica":
            color = '#d9534f'  # Rojo
            status = "< 1\nHipertónica"
        elif result.tonic_classification == "Hipotónica":
            color = '#5cb85c'  # Verde
            status = "> 1\nHipotónica"
        else:
            color = '#5bc0de'  # Azul
            status = "≈ 1\nIsotónica"
        
        # Dibujar indicador de coeficiente
        ax2.barh([0], [coef], height=0.5, color=color, alpha=0.7)
        ax2.axvline(x=1, color='black', linestyle='--', linewidth=2, label='Equilibrio (1.0)')
        
        # Marcar el valor
        ax2.text(coef, 0, f' {coef:.3f}', va='center', ha='left', fontsize=12, fontweight='bold')
        
        ax2.set_xlim(0, max(2, coef * 1.2))
        ax2.set_ylim(-0.5, 0.5)
        ax2.set_xlabel('Coeficiente de Presión Osmótica Real')
        ax2.set_title(f'Coef = π_int_real / π_ext_real\n{status}')
        ax2.set_yticks([])
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3, axis='x')
        
        fig.tight_layout()
        self.plot_canvas.draw()
    
    def _plot_comparison_lysis(self, result, critical_volume: float):
        """Grafica la comparación cuando hay lisis."""
        self.plot_canvas.clear()
        fig = self.plot_canvas.figure
        fig.clear()
        
        ax = fig.add_subplot(1, 1, 1)
        
        # Mostrar indicador de lisis
        coef = result.effective_osmolarity_ratio
        
        # Barras mostrando el coeficiente vs volumen crítico
        bars = ax.bar(
            ['Coef. π Real', 'Volumen Crítico'],
            [coef, critical_volume],
            color=['#d9534f', '#5bc0de'],
            alpha=0.8,
            edgecolor='black',
            linewidth=2
        )
        
        # Línea de volumen crítico
        ax.axhline(y=critical_volume, color='#d9534f', linestyle='--', 
                   linewidth=2, label=f'Límite lisis ({critical_volume:.1f})')
        
        # Zona de lisis
        ax.axhspan(critical_volume, max(coef * 1.2, critical_volume * 1.5), 
                   alpha=0.2, color='red', label='Zona de lisis')
        
        # Etiquetas
        ax.set_ylabel('Razón de Volumen (V/V₀)')
        ax.set_title('[!] LISIS CELULAR DETECTADA\nEl volumen excedería el límite crítico', 
                     fontsize=12, color='#d9534f')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        # Añadir valores sobre las barras
        for bar, val in zip(bars, [coef, critical_volume]):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                   f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        fig.tight_layout()
        self.plot_canvas.draw()
    
    def _plot_volume_dynamics_lysis(self, result, internal_solutes: List[Dict], 
                                     external_solutes: List[Dict], critical_volume: float):
        """Grafica la dinámica del volumen hasta el punto de lisis."""
        self.plot_canvas.clear()
        fig = self.plot_canvas.figure
        fig.clear()
        
        # Parámetros del modelo
        V0 = 1.0
        b = 0.4
        V_osm_0 = V0 * (1 - b)
        Lp = 0.5
        
        # Calcular permeabilidad efectiva de solutos penetrantes
        ext_penetrants = [s for s in external_solutes if s.get("is_penetrant", False)]
        int_penetrants = [s for s in internal_solutes if s.get("is_penetrant", False)]
        
        total_pen_conc = sum(s.get("concentration", 0) for s in ext_penetrants + int_penetrants)
        if total_pen_conc > 0:
            Ps = sum(
                s.get("permeability", 0.0) * s.get("concentration", 0)
                for s in ext_penetrants + int_penetrants
            ) / total_pen_conc
            Ps = Ps * 1e4  # Escalar para visualización
        else:
            Ps = 0.0
        Ps = max(Ps, 0.01) if any(ext_penetrants) or any(int_penetrants) else 0.0
        
        # Calcular osmolaridades
        int_nonpen_osm = sum(
            s["concentration"] * s["j"] 
            for s in internal_solutes if not s.get("is_penetrant", False)
        )
        int_pen_osm = sum(
            s["concentration"] * s["j"]
            for s in internal_solutes if s.get("is_penetrant", False)
        )
        ext_nonpen_osm = sum(
            s["concentration"] * s["j"]
            for s in external_solutes if not s.get("is_penetrant", False)
        )
        ext_pen_osm = sum(
            s["concentration"] * s["j"]
            for s in external_solutes if s.get("is_penetrant", False)
        )
        
        total_int_osm = int_nonpen_osm + int_pen_osm if (int_nonpen_osm + int_pen_osm) > 0 else 280
        n_int_nonpen_0 = int_nonpen_osm * V_osm_0 / total_int_osm
        n_int_pen_0 = int_pen_osm * V_osm_0 / total_int_osm
        C_ext_nonpen = ext_nonpen_osm / total_int_osm
        C_ext_pen = ext_pen_osm / total_int_osm
        
        def osmotic_dynamics_lysis(y, t):
            V = max(y[0], 0.1 * V0)
            n_pen = y[1]
            V_osm = max(V - V0 * b, 0.01)
            A = abs(V) ** (2/3)
            C_int_nonpen = n_int_nonpen_0 / V_osm
            C_int_pen = max(n_pen, 0) / V_osm
            # Osmolaridad total (penetrantes + no penetrantes)
            pi_int_total = C_int_nonpen + C_int_pen
            pi_ext_total = C_ext_nonpen + C_ext_pen
            # Si pi_int > pi_ext: agua entra, V aumenta
            dV_dt = Lp * A * (pi_int_total - pi_ext_total)
            dn_pen_dt = Ps * A * (C_ext_pen - C_int_pen)
            return [dV_dt, dn_pen_dt]
        
        # Simular hasta lisis o equilibrio
        t_max = 60
        t = np.linspace(0, t_max, 400)
        y0 = [V0, max(n_int_pen_0, 0)]
        
        try:
            solution = odeint(osmotic_dynamics_lysis, y0, t, rtol=1e-6, atol=1e-8)
            V_t = solution[:, 0]
            V_t = np.maximum(V_t, 0.1 * V0)
        except Exception:
            V_t = np.ones_like(t) * V0
        
        V_percent = (V_t / V0) * 100
        critical_percent = critical_volume * 100
        
        # Encontrar punto de lisis
        lysis_idx = np.where(V_percent >= critical_percent)[0]
        if len(lysis_idx) > 0:
            lysis_time = t[lysis_idx[0]]
            lysis_vol = V_percent[lysis_idx[0]]
        else:
            lysis_time = t_max
            lysis_vol = V_percent[-1]
        
        ax = fig.add_subplot(1, 1, 1)
        
        # Graficar volumen hasta lisis
        if len(lysis_idx) > 0:
            # Antes de lisis
            ax.plot(t[:lysis_idx[0]+1], V_percent[:lysis_idx[0]+1], 
                   color='#5cb85c', linewidth=2.5, label='Volumen celular')
            ax.fill_between(t[:lysis_idx[0]+1], 100, V_percent[:lysis_idx[0]+1], 
                           alpha=0.3, color='#dff0d8')
            
            # Después de lisis (línea punteada indicando ruptura)
            ax.plot(t[lysis_idx[0]:], V_percent[lysis_idx[0]:], 
                   color='#d9534f', linewidth=2, linestyle='--', alpha=0.5)
            
            # Marcar punto de lisis
            ax.scatter([lysis_time], [lysis_vol], color='#d9534f', s=150, 
                      zorder=5, marker='X', label=f'LISIS (t={lysis_time:.1f}s)')
            ax.annotate('[X] LISIS', xy=(lysis_time, lysis_vol),
                       xytext=(lysis_time + 5, lysis_vol + 10),
                       fontsize=11, fontweight='bold', color='#d9534f',
                       arrowprops=dict(arrowstyle='->', color='#d9534f'))
        else:
            ax.plot(t, V_percent, color='#5cb85c', linewidth=2.5, label='Volumen celular')
        
        # Líneas de referencia
        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='V₀ (100%)')
        ax.axhline(y=critical_percent, color='#d9534f', linestyle='-', 
                   linewidth=2, alpha=0.8, label=f'V crítico ({critical_percent:.0f}%)')
        
        # Zona de lisis
        y_max = max(V_percent.max() * 1.1, critical_percent * 1.2)
        ax.axhspan(critical_percent, y_max, alpha=0.15, color='red', label='Zona de lisis')
        
        # Etiquetas y título
        ax.set_xlabel('Tiempo (s)', fontsize=11)
        ax.set_ylabel('Volumen celular (%)', fontsize=11)
        ax.set_title('[!] Dinámica hasta Lisis Celular', fontsize=12, color='#d9534f')
        
        ax.set_xlim(0, t_max)
        ax.set_ylim(min(V_percent.min() * 0.9, 95), y_max)
        
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper left', fontsize=9)
        
        fig.tight_layout()
        self.plot_canvas.draw()
    
    def _plot_volume_dynamics(self, result, internal_solutes: List[Dict], external_solutes: List[Dict]):
        """
        Grafica la dinámica del volumen celular en el tiempo.
        
        Modelo de ecuaciones diferenciales:
        
        Para solutos NO penetrantes:
            dV/dt = -Lp * A * R * T * (Σ(n_ext/V_ext) - Σ(n_int/V))
        
        Para solutos penetrantes (ej: urea):
            dV/dt = -Lp * A * R * T * (π_ext_total - π_int(V) - σ*(C_s_ext - C_s_int(V)))
            dn_s/dt = P_s * A * (C_s_ext - C_s_int(V))
        
        Donde:
            V = volumen celular
            Lp = permeabilidad hidráulica (~1e-12 cm/(s·Pa) para células típicas)
            A = área de membrana (proporcional a V^(2/3))
            n = moles de soluto
            σ = coeficiente de reflexión (0 para penetrantes totales, 1 para no penetrantes)
            P_s = permeabilidad del soluto penetrante
        """
        self.plot_canvas.clear()
        fig = self.plot_canvas.figure
        fig.clear()
        
        # Parámetros del modelo
        V0 = 1.0  # Volumen inicial normalizado
        b = 0.4   # Fracción no osmótica
        V_osm_0 = V0 * (1 - b)  # Volumen osmótico inicial
        
        # Permeabilidad hidráulica (normalizada para visualización)
        Lp = 0.5  # Ajustado para escala de tiempo en segundos
        
        # Calcular permeabilidad efectiva de solutos penetrantes
        # Promediamos ponderado por concentración, o usamos suma si solo hay externos
        ext_penetrants = [s for s in external_solutes if s.get("is_penetrant", False)]
        int_penetrants = [s for s in internal_solutes if s.get("is_penetrant", False)]
        
        # Permeabilidad efectiva: usar la máxima o ponderada por concentración
        total_pen_conc = sum(s.get("concentration", 0) for s in ext_penetrants + int_penetrants)
        if total_pen_conc > 0:
            # Promedio ponderado por concentración (en unidades normalizadas)
            Ps = sum(
                s.get("permeability", 0.0) * s.get("concentration", 0)
                for s in ext_penetrants + int_penetrants
            ) / total_pen_conc
            # Escalar permeabilidad para visualización (cm/s -> unidades normalizadas)
            # Usamos un factor de escala para que valores típicos (1e-5 a 1e-4 cm/s) generen dinámicas visibles
            Ps = Ps * 1e4  # Escala para visualización
        else:
            Ps = 0.0  # Sin solutos penetrantes
        
        # Valor mínimo para evitar dinámicas demasiado lentas
        Ps = max(Ps, 0.01) if any(ext_penetrants) or any(int_penetrants) else 0.0
        
        # Calcular osmolaridades y separar penetrantes/no penetrantes
        # Intracelular
        int_nonpen_osm = sum(
            s["concentration"] * s["j"] 
            for s in internal_solutes if not s.get("is_penetrant", False)
        )
        int_pen_osm = sum(
            s["concentration"] * s["j"]
            for s in internal_solutes if s.get("is_penetrant", False)
        )
        
        # Extracelular
        ext_nonpen_osm = sum(
            s["concentration"] * s["j"]
            for s in external_solutes if not s.get("is_penetrant", False)
        )
        ext_pen_osm = sum(
            s["concentration"] * s["j"]
            for s in external_solutes if s.get("is_penetrant", False)
        )
        
        # Normalizar concentraciones respecto a la intracelular inicial
        total_int_osm = int_nonpen_osm + int_pen_osm
        if total_int_osm <= 0:
            total_int_osm = 280  # Valor por defecto
        
        # Cantidades iniciales de soluto (n = C * V)
        n_int_nonpen_0 = int_nonpen_osm * V_osm_0 / total_int_osm
        n_int_pen_0 = int_pen_osm * V_osm_0 / total_int_osm
        
        # Concentraciones externas normalizadas
        C_ext_nonpen = ext_nonpen_osm / total_int_osm
        C_ext_pen = ext_pen_osm / total_int_osm
        
        # Cantidad externa de penetrante (asumimos volumen externo muy grande, concentración constante)
        # n_ext_pen permanece constante
        
        def osmotic_dynamics(y, t):
            """
            Sistema de ecuaciones diferenciales para dinámica osmótica.
            
            Modelo:
            - Los solutos NO penetrantes determinan la presión osmótica "real" (tonicidad)
            - Los solutos penetrantes atraviesan la membrana según su gradiente de concentración
            - A medida que el penetrante entra, aumenta la osmolaridad TOTAL interna,
              lo que puede causar entrada de agua secundaria
            
            dV/dt = Lp * A * (π_total_ext - π_total_int)
                  donde π_total incluye tanto penetrantes como no penetrantes
                  pero el equilibrio a largo plazo depende de los no-penetrantes
            
            dn_pen/dt = Ps * A * (C_ext_pen - C_int_pen)
            """
            V = y[0]  # Volumen
            n_pen = y[1]  # Moles de soluto penetrante intracelular
            
            # Asegurar que V sea positivo para evitar errores numéricos
            V = max(V, 0.1 * V0)  # Mínimo 10% del volumen inicial
            
            # Volumen osmótico actual
            V_osm = max(V - V0 * b, 0.01)  # Evitar división por cero
            
            # Área de membrana (proporcional a V^(2/3))
            A = abs(V) ** (2/3)
            
            # Concentraciones intracelulares actuales
            C_int_nonpen = n_int_nonpen_0 / V_osm  # No penetrantes (cantidad conservada)
            C_int_pen = max(n_pen, 0) / V_osm  # Penetrantes (cantidad variable)
            
            # Osmolaridad total interna y externa
            # El flujo de agua responde a la diferencia de osmolaridad TOTAL
            # pero los penetrantes eventualmente se equilibran
            pi_int_total = C_int_nonpen + C_int_pen
            pi_ext_total = C_ext_nonpen + C_ext_pen
            
            # Flujo de agua (dV/dt)
            # Si pi_int > pi_ext: agua entra, V aumenta (hipotónico)
            # Si pi_ext > pi_int: agua sale, V disminuye (hipertónico)
            dV_dt = Lp * A * (pi_int_total - pi_ext_total)
            
            # Flujo de soluto penetrante (dn/dt)
            # El penetrante difunde según su gradiente de concentración
            dn_pen_dt = Ps * A * (C_ext_pen - C_int_pen)
            
            return [dV_dt, dn_pen_dt]
        
        # Tiempo de simulación (ajustado para ver la dinámica)
        t_max = 30  # segundos
        t = np.linspace(0, t_max, 300)
        
        # Condiciones iniciales [V, n_penetrante]
        y0 = [V0, max(n_int_pen_0, 0)]
        
        # Resolver ODE con tolerancias ajustadas
        try:
            solution = odeint(osmotic_dynamics, y0, t, rtol=1e-6, atol=1e-8)
            V_t = solution[:, 0]
            n_pen_t = solution[:, 1]
            # Asegurar valores positivos
            V_t = np.maximum(V_t, 0.1 * V0)
        except Exception:
            # Fallback a solución simplificada
            V_t = np.ones_like(t) * V0
            n_pen_t = np.ones_like(t) * max(n_int_pen_0, 0)
        
        # Crear gráfica
        ax = fig.add_subplot(1, 1, 1)
        
        # Normalizar volumen como porcentaje del inicial
        V_percent = (V_t / V0) * 100
        
        # Determinar color según tonicidad
        if result.tonic_classification == "Hipertónica":
            color = '#d9534f'  # Rojo
            fill_color = '#f2dede'
        elif result.tonic_classification == "Hipotónica":
            color = '#5cb85c'  # Verde
            fill_color = '#dff0d8'
        else:
            color = '#5bc0de'  # Azul
            fill_color = '#d9edf7'
        
        # Graficar volumen vs tiempo
        ax.plot(t, V_percent, color=color, linewidth=2.5, label='Volumen celular')
        ax.fill_between(t, 100, V_percent, alpha=0.3, color=fill_color)
        
        # Línea de referencia (volumen inicial)
        ax.axhline(y=100, color='gray', linestyle='--', linewidth=1.5, alpha=0.7, label='V₀ (100%)')
        
        # Calcular y mostrar volumen final de equilibrio
        V_final = V_percent[-1]
        ax.axhline(y=V_final, color=color, linestyle=':', linewidth=1.5, alpha=0.7)
        ax.text(t_max * 0.95, V_final, f'{V_final:.1f}%', 
                va='bottom' if V_final < 100 else 'top', ha='right', 
                fontsize=10, fontweight='bold', color=color)
        
        # Etiquetas y título
        ax.set_xlabel('Tiempo (s)', fontsize=11)
        ax.set_ylabel('Volumen celular (%)', fontsize=11)
        ax.set_title(f'Dinámica del Volumen Celular\n{result.tonic_classification}', fontsize=12)
        
        # Ajustar límites del eje Y
        y_min = min(V_percent.min() * 0.9, 95)
        y_max = max(V_percent.max() * 1.1, 105)
        ax.set_ylim(y_min, y_max)
        ax.set_xlim(0, t_max)
        
        # Grid y leyenda
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)
        
        # Añadir anotación explicativa
        if result.tonic_classification == "Hipertónica":
            annotation = "El agua sale de la célula\n(crenación)"
        elif result.tonic_classification == "Hipotónica":
            annotation = "El agua entra en la célula\n(posible lisis)"
        else:
            annotation = "Sin cambio neto de volumen"
        
        ax.annotate(annotation, xy=(t_max * 0.5, V_percent[len(V_percent)//2]),
                   xytext=(t_max * 0.7, 100),
                   fontsize=9, ha='center',
                   arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
        
        fig.tight_layout()
        self.plot_canvas.draw()
    
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
    
    def _set_example_isotonic(self):
        """Ejemplo de solución isotónica."""
        # Limpiar secciones
        self.internal_section.clear_all()
        self.external_section.clear_all()
        
        # Configurar solutos típicos intracelulares
        # (agregar manualmente ya que no hay método directo)
        # Por ahora solo mostrar mensaje
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
