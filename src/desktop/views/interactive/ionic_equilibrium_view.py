"""
Vista interactiva del módulo de Equilibrio Iónico.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Optional

from ...components.input_form import InputForm, FormField
from ...components.result_panel import ResultPanel
from ...components.plot_canvas import PlotCanvas


class IonicEquilibriumView(ctk.CTkFrame):
    """
    Vista interactiva para el módulo de Equilibrio Iónico.
    
    Permite calcular:
    - Potencial de Nernst (iones predefinidos y personalizados)
    """
    
    # Iones predefinidos con sus propiedades
    PREDEFINED_IONS = {
        "K⁺": {"valencia": 1, "conc_ext": 5, "conc_int": 140},
        "Na⁺": {"valencia": 1, "conc_ext": 145, "conc_int": 12},
        "Ca²⁺": {"valencia": 2, "conc_ext": 2, "conc_int": 0.0001},
        "Cl⁻": {"valencia": -1, "conc_ext": 110, "conc_int": 4},
        "H⁺": {"valencia": 1, "conc_ext": 0.00004, "conc_int": 0.0001},
        "Mg²⁺": {"valencia": 2, "conc_ext": 1.5, "conc_int": 0.5},
        "HCO₃⁻": {"valencia": -1, "conc_ext": 24, "conc_int": 10},
        "Personalizado": {"valencia": 1, "conc_ext": 1, "conc_int": 1},
    }
    
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
            text="⚖️ Módulo de Equilibrio Iónico",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(
            header,
            text="Potencial de Nernst y equilibrio electroquímico",
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
        
        # Panel izquierdo - Tabs de cálculos
        left_frame = ctk.CTkFrame(self.main_paned)
        left_frame.grid_columnconfigure(0, weight=1)
        left_frame.grid_rowconfigure(0, weight=1)
        
        self.tabs = ctk.CTkTabview(left_frame, width=400)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.tab_nernst = self.tabs.add("Nernst")
        
        self._setup_nernst_tab()
        
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
        
        # Añadir paneles al PanedWindow vertical
        self.right_paned.add(result_container, minsize=150, stretch="always")
        self.right_paned.add(plot_container, minsize=200, stretch="always")
        
        # Añadir paneles al PanedWindow horizontal
        self.main_paned.add(left_frame, minsize=380, stretch="always")
        self.main_paned.add(right_outer, minsize=400, stretch="always")
    
    def _setup_nernst_tab(self):
        """Configura el tab de Nernst."""
        self.tab_nernst.grid_columnconfigure(0, weight=1)
        self.tab_nernst.grid_rowconfigure(1, weight=1)
        
        # Información
        info = ctk.CTkLabel(
            self.tab_nernst,
            text="Potencial de equilibrio de un ion\n"
                 "Eᵢ = (RT/zF) × ln([ion]ₑ/[ion]ᵢ)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        info.grid(row=0, column=0, sticky="w", pady=(10, 15))
        
        # Frame principal para el formulario (sin scroll)
        form_frame = ctk.CTkFrame(self.tab_nernst, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=5)
        form_frame.grid_columnconfigure(0, weight=1)
        
        # Selector de ion predefinido
        ion_frame = ctk.CTkFrame(form_frame)
        ion_frame.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        ion_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            ion_frame,
            text="Seleccionar Ion:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.ion_selector = ctk.CTkComboBox(
            ion_frame,
            values=list(self.PREDEFINED_IONS.keys()),
            command=self._on_ion_selected,
            width=200
        )
        self.ion_selector.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        self.ion_selector.set("K⁺")
        
        # Nota sobre ion personalizado
        note = ctk.CTkLabel(
            form_frame,
            text="💡 Selecciona 'Personalizado' para introducir un ion diferente",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        note.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 10))
        
        # Frame para nombre de ion personalizado (inicialmente oculto)
        self.custom_ion_frame = ctk.CTkFrame(form_frame)
        self.custom_ion_frame.grid(row=2, column=0, sticky="ew", pady=5)
        self.custom_ion_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            self.custom_ion_frame,
            text="Nombre del ion:",
            font=ctk.CTkFont(size=11)
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        
        self.custom_ion_name = ctk.CTkEntry(
            self.custom_ion_frame,
            placeholder_text="Ej: Fe³⁺, Zn²⁺",
            width=150
        )
        self.custom_ion_name.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Ocultar inicialmente
        self.custom_ion_frame.grid_remove()
        
        # Formulario principal
        self.nernst_form = InputForm(
            form_frame,
            title="Parámetros del Ion",
            fields=[
                FormField("conc_out", "Concentración externa (mM)", "entry", "5"),
                FormField("conc_in", "Concentración interna (mM)", "entry", "140"),
                FormField("valence", "Valencia (z)", "entry", "1",
                         tooltip="Positivo para cationes (+1, +2), negativo para aniones (-1, -2)"),
                FormField("temperature", "Temperatura (°C)", "entry", "37"),
            ],
            on_submit=self._calculate_nernst,
            submit_text="Calcular Potencial de Nernst"
        )
        self.nernst_form.grid(row=3, column=0, sticky="ew")
    
    def _on_ion_selected(self, choice: str):
        """Maneja la selección de un ion en el combobox."""
        if choice == "Personalizado":
            self.custom_ion_frame.grid()
        else:
            self.custom_ion_frame.grid_remove()
            # Autocompletar valores
            if choice in self.PREDEFINED_IONS:
                ion_data = self.PREDEFINED_IONS[choice]
                self.nernst_form.set_value("conc_out", str(ion_data["conc_ext"]))
                self.nernst_form.set_value("conc_in", str(ion_data["conc_int"]))
                self.nernst_form.set_value("valence", str(ion_data["valencia"]))
    
    def _calculate_nernst(self, data: dict):
        """Calcula el potencial de Nernst."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener ion
            selected_ion = self.ion_selector.get()
            if selected_ion == "Personalizado":
                ion = self.custom_ion_name.get().strip()
                if not ion:
                    self.result_panel.show_error("Por favor, introduce el nombre del ion personalizado")
                    return
            else:
                ion = selected_ion
            
            # Obtener valores
            conc_out = float(data.get("conc_out", 5))
            conc_in = float(data.get("conc_in", 140))
            temp = float(data.get("temperature", 37))
            valence_str = data.get("valence", "1")
            valence = int(float(valence_str)) if valence_str else 1
            
            # Validar valencia
            if valence == 0:
                self.result_panel.show_error("La valencia no puede ser cero")
                return
            
            # Calcular
            result = self.solver_service.calculate_nernst(
                ion_name=ion.replace("⁺", "+").replace("⁻", "-").replace("²", "2").replace("³", "3"),
                concentration_out=conc_out,
                concentration_in=conc_in,
                valence=valence,
                temperature_celsius=temp
            )
            
            # Mostrar resultados
            results_data = {
                "Ion": ion,
                "Potencial de Nernst": f"{result.equilibrium_potential:.2f} mV",
                "[Ion] externa": f"{result.concentration_out:.4g} mM",
                "[Ion] interna": f"{result.concentration_in:.4g} mM",
                "Valencia": f"{result.valence:+d}",
                "Temperatura": f"{result.temperature_kelvin - 273.15:.1f}°C"
            }
            
            self.result_panel.show_results(
                title="📊 Potencial de Nernst",
                results=results_data,
                interpretation=result.interpretation,
                feedback=result.feedback
            )
            
            # Graficar comparación con otros iones
            self._plot_nernst_comparison(ion, result.equilibrium_potential)
            
        except ValueError as e:
            self.result_panel.show_error(f"Error en los datos: {e}")
        except Exception as e:
            self.result_panel.show_error(f"Error de cálculo: {e}")
    
    def _plot_nernst_comparison(self, current_ion: str, current_potential: float):
        """Grafica comparación de potenciales de Nernst."""
        # Valores típicos de referencia
        typical = {
            "K⁺": -90.0,
            "Na⁺": 60.0,
            "Ca²⁺": 120.0,
            "Cl⁻": -70.0
        }
        
        # Actualizar con el valor calculado
        typical[current_ion] = float(current_potential)
        
        ions = list(typical.keys())
        potentials = list(typical.values())
        colors = ["steelblue" if ion != current_ion else "orange" for ion in ions]
        
        self.plot_canvas.clear()
        bars = self.plot_canvas.ax.barh(ions, potentials, color=colors)
        self.plot_canvas.ax.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
        self.plot_canvas.ax.axvline(x=-70, color="red", linestyle=":", alpha=0.5, label="Vm reposo")
        self.plot_canvas.ax.set_xlabel("Potencial (mV)")
        self.plot_canvas.ax.set_title("Potenciales de Equilibrio")
        
        # Anotar valores
        for bar, val in zip(bars, potentials):
            self.plot_canvas.ax.text(
                val + 3 if val >= 0 else val - 3,
                bar.get_y() + bar.get_height()/2,
                f"{val:.0f}",
                va="center",
                ha="left" if val >= 0 else "right",
                fontsize=9
            )
        
        self.plot_canvas.ax.legend(loc="lower right", fontsize=8)
        self.plot_canvas.draw()
