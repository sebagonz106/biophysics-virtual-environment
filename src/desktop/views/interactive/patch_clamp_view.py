"""
Vista interactiva del módulo de Patch Clamp.
"""

import customtkinter as ctk
import numpy as np
from typing import Optional

from ...components.input_form import InputForm, FormField
from ...components.result_panel import ResultPanel
from ...components.plot_canvas import PlotCanvas


class PatchClampView(ctk.CTkFrame):
    """
    Vista interactiva para el módulo de Patch Clamp.
    
    Permite calcular:
    - Potencial de Nernst
    - Potencial de Goldman-Hodgkin-Katz
    - Curvas I-V
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
            text="⚡ Módulo Interactivo de Patch Clamp",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(
            header,
            text="Potenciales de Nernst, Goldman-Hodgkin-Katz y Curvas I-V",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, sticky="w")
        
        # Panel principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew")
        self.main_frame.grid_columnconfigure((0, 1), weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - Tabs de cálculos
        self.tabs = ctk.CTkTabview(self.main_frame, width=420)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        self.tab_nernst = self.tabs.add("Nernst")
        self.tab_ghk = self.tabs.add("Goldman (GHK)")
        self.tab_iv = self.tabs.add("Curva I-V")
        
        self._setup_nernst_tab()
        self._setup_ghk_tab()
        self._setup_iv_tab()
        
        # Panel derecho - Resultados y gráficos
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure((0, 1), weight=1)
        
        self.result_panel = ResultPanel(self.right_panel)
        self.result_panel.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.plot_canvas = PlotCanvas(self.right_panel, figsize=(5, 4))
        self.plot_canvas.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
    
    def _setup_nernst_tab(self):
        """Configura el tab de Nernst."""
        self.tab_nernst.grid_columnconfigure(0, weight=1)
        
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
        
        # Formulario
        self.nernst_form = InputForm(
            self.tab_nernst,
            title="Parámetros del Ion",
            fields=[
                FormField(
                    "ion", "Ion", "combobox",
                    options=["K⁺", "Na⁺", "Ca²⁺", "Cl⁻", "H⁺", "Mg²⁺", "HCO₃⁻"]
                ),
                FormField("conc_out", "Concentración externa (mM)", "entry", "5"),
                FormField("conc_in", "Concentración interna (mM)", "entry", "140"),
                FormField("temperature", "Temperatura (°C)", "entry", "37"),
                FormField("valence", "Valencia (z)", "entry", "1",
                         tooltip="Se autocompleta al seleccionar ion conocido"),
            ],
            on_submit=self._calculate_nernst,
            submit_text="Calcular Potencial de Nernst"
        )
        self.nernst_form.grid(row=1, column=0, sticky="ew", padx=5)
        
        # Valores típicos
        typical_frame = ctk.CTkFrame(self.tab_nernst)
        typical_frame.grid(row=2, column=0, sticky="ew", pady=15, padx=5)
        
        ctk.CTkLabel(
            typical_frame,
            text="📋 Valores Típicos (Neurona):",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        typical_ions = [
            ("K⁺", "5", "140", "+1"),
            ("Na⁺", "145", "12", "+1"),
            ("Ca²⁺", "2", "0.0001", "+2"),
            ("Cl⁻", "110", "4", "-1"),
        ]
        
        for i, (ion, out, inn, z) in enumerate(typical_ions):
            btn = ctk.CTkButton(
                typical_frame,
                text=ion,
                width=60,
                height=28,
                command=lambda io=ion, o=out, i=inn, v=z: self._set_nernst_example(io, o, i, v)
            )
            btn.grid(row=1, column=i, padx=5, pady=(5, 10))
    
    def _setup_ghk_tab(self):
        """Configura el tab de Goldman-Hodgkin-Katz."""
        self.tab_ghk.grid_columnconfigure(0, weight=1)
        
        # Información
        info = ctk.CTkLabel(
            self.tab_ghk,
            text="Potencial de membrana considerando múltiples iones\n"
                 "Vm = (RT/F) × ln[(Pₖ[K⁺]ₑ + Pₙₐ[Na⁺]ₑ + Pₒₗ[Cl⁻]ᵢ) / (Pₖ[K⁺]ᵢ + Pₙₐ[Na⁺]ᵢ + Pₒₗ[Cl⁻]ₑ)]",
            font=ctk.CTkFont(size=10),
            text_color="gray",
            justify="left",
            wraplength=380
        )
        info.grid(row=0, column=0, sticky="w", pady=(10, 15))
        
        # Scroll frame para el formulario largo
        form_scroll = ctk.CTkScrollableFrame(self.tab_ghk, height=280)
        form_scroll.grid(row=1, column=0, sticky="ew", padx=5)
        form_scroll.grid_columnconfigure(0, weight=1)
        
        # Formulario
        self.ghk_form = InputForm(
            form_scroll,
            title="Concentraciones y Permeabilidades",
            fields=[
                FormField("k_out", "[K⁺] externa (mM)", "entry", "5"),
                FormField("k_in", "[K⁺] interna (mM)", "entry", "140"),
                FormField("p_k", "Permeabilidad K⁺ (Pₖ)", "entry", "1.0"),
                FormField("na_out", "[Na⁺] externa (mM)", "entry", "145"),
                FormField("na_in", "[Na⁺] interna (mM)", "entry", "12"),
                FormField("p_na", "Permeabilidad Na⁺ (Pₙₐ)", "entry", "0.04"),
                FormField("cl_out", "[Cl⁻] externa (mM)", "entry", "110"),
                FormField("cl_in", "[Cl⁻] interna (mM)", "entry", "4"),
                FormField("p_cl", "Permeabilidad Cl⁻ (Pₒₗ)", "entry", "0.45"),
                FormField("temperature", "Temperatura (°C)", "entry", "37"),
            ],
            on_submit=self._calculate_ghk,
            submit_text="Calcular Vm (GHK)"
        )
        self.ghk_form.grid(row=0, column=0, sticky="ew")
        
        # Escenarios
        scenarios_frame = ctk.CTkFrame(self.tab_ghk)
        scenarios_frame.grid(row=2, column=0, sticky="ew", pady=10, padx=5)
        
        ctk.CTkLabel(
            scenarios_frame,
            text="🧪 Escenarios:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        btn1 = ctk.CTkButton(
            scenarios_frame,
            text="Reposo",
            width=100,
            height=28,
            command=lambda: self._set_ghk_scenario("rest")
        )
        btn1.grid(row=1, column=0, padx=5, pady=(5, 10))
        
        btn2 = ctk.CTkButton(
            scenarios_frame,
            text="Despolarizado",
            width=100,
            height=28,
            command=lambda: self._set_ghk_scenario("depol")
        )
        btn2.grid(row=1, column=1, padx=5, pady=(5, 10))
        
        btn3 = ctk.CTkButton(
            scenarios_frame,
            text="Hiperpolarizado",
            width=100,
            height=28,
            command=lambda: self._set_ghk_scenario("hyper")
        )
        btn3.grid(row=1, column=2, padx=5, pady=(5, 10))
    
    def _setup_iv_tab(self):
        """Configura el tab de curva I-V."""
        self.tab_iv.grid_columnconfigure(0, weight=1)
        
        # Información
        info = ctk.CTkLabel(
            self.tab_iv,
            text="Generar curva corriente-voltaje\n"
                 "I = g × (Vm - Erev)",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            justify="left"
        )
        info.grid(row=0, column=0, sticky="w", pady=(10, 15))
        
        # Formulario
        self.iv_form = InputForm(
            self.tab_iv,
            title="Parámetros del Canal",
            fields=[
                FormField("conductance", "Conductancia (nS)", "entry", "1.0"),
                FormField("reversal_potential", "Potencial de reversión (mV)", "entry", "-80"),
                FormField("v_min", "Voltaje mínimo (mV)", "entry", "-100"),
                FormField("v_max", "Voltaje máximo (mV)", "entry", "50"),
                FormField("v_step", "Paso de voltaje (mV)", "entry", "10"),
            ],
            on_submit=self._calculate_iv,
            submit_text="Generar Curva I-V"
        )
        self.iv_form.grid(row=1, column=0, sticky="ew", padx=5)
        
        # Canales típicos
        channels_frame = ctk.CTkFrame(self.tab_iv)
        channels_frame.grid(row=2, column=0, sticky="ew", pady=15, padx=5)
        
        ctk.CTkLabel(
            channels_frame,
            text="📋 Canales Típicos:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))
        
        channels = [
            ("Canal K⁺", "1.0", "-80"),
            ("Canal Na⁺", "1.5", "+60"),
            ("Canal Cl⁻", "0.5", "-70"),
        ]
        
        for i, (name, g, e_rev) in enumerate(channels):
            btn = ctk.CTkButton(
                channels_frame,
                text=name,
                width=90,
                height=28,
                command=lambda cond=g, rev=e_rev: self._set_iv_example(cond, rev)
            )
            btn.grid(row=1, column=i, padx=5, pady=(5, 10))
    
    def _calculate_nernst(self, data: dict):
        """Calcula el potencial de Nernst."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener valores
            ion = data.get("ion", "K⁺")
            conc_out = float(data.get("conc_out", 5))
            conc_in = float(data.get("conc_in", 140))
            temp = float(data.get("temperature", 37))
            valence_str = data.get("valence", "1")
            valence = int(valence_str) if valence_str else 1
            
            # Mapear valencia según ion
            ion_valences = {
                "K⁺": 1, "Na⁺": 1, "H⁺": 1,
                "Ca²⁺": 2, "Mg²⁺": 2,
                "Cl⁻": -1, "HCO₃⁻": -1
            }
            if ion in ion_valences:
                valence = ion_valences[ion]
            
            # Calcular
            result = self.solver_service.calculate_nernst(
                ion_name=ion.replace("⁺", "+").replace("⁻", "-").replace("²", "2"),
                concentration_out=conc_out,
                concentration_in=conc_in,
                valence=valence,
                temperature_celsius=temp
            )
            
            # Mostrar resultados
            results_data = {
                "Ion": ion,
                "Potencial de Nernst": f"{result.equilibrium_potential:.2f} mV",
                "[Ion] externa": f"{result.concentration_out:.2f} mM",
                "[Ion] interna": f"{result.concentration_in:.2f} mM",
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
    
    def _calculate_ghk(self, data: dict):
        """Calcula el potencial de membrana con GHK."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Construir diccionarios de concentraciones y permeabilidades
            concentrations_out = {
                "K": float(data.get("k_out", 5)),
                "Na": float(data.get("na_out", 145)),
                "Cl": float(data.get("cl_out", 110))
            }
            
            concentrations_in = {
                "K": float(data.get("k_in", 140)),
                "Na": float(data.get("na_in", 12)),
                "Cl": float(data.get("cl_in", 4))
            }
            
            permeabilities = {
                "K": float(data.get("p_k", 1.0)),
                "Na": float(data.get("p_na", 0.04)),
                "Cl": float(data.get("p_cl", 0.45))
            }
            
            temp = float(data.get("temperature", 37))
            
            # Calcular
            result = self.solver_service.calculate_membrane_potential(
                concentrations_out=concentrations_out,
                concentrations_in=concentrations_in,
                permeabilities=permeabilities,
                temperature_celsius=temp
            )
            
            # Mostrar resultados
            results_data = {
                "Potencial de Membrana (Vm)": f"{result.membrane_potential:.2f} mV",
                "Contribución K⁺": f"{result.ion_contributions.get('K', 0):.1%}",
                "Contribución Na⁺": f"{result.ion_contributions.get('Na', 0):.1%}",
                "Contribución Cl⁻": f"{result.ion_contributions.get('Cl', 0):.1%}",
                "Temperatura": f"{result.temperature_kelvin - 273.15:.1f}°C"
            }
            
            self.result_panel.show_results(
                title="📊 Potencial de Membrana (GHK)",
                results=results_data,
                interpretation=result.interpretation,
                feedback=result.feedback
            )
            
            # Graficar contribuciones
            self._plot_ghk_contributions(result)
            
        except ValueError as e:
            self.result_panel.show_error(f"Error en los datos: {e}")
        except Exception as e:
            self.result_panel.show_error(f"Error de cálculo: {e}")
    
    def _calculate_iv(self, data: dict):
        """Genera la curva I-V."""
        if not self.solver_service:
            self.result_panel.show_error("Servicio no disponible")
            return
        
        try:
            # Obtener valores
            g = float(data.get("conductance", 1.0))
            e_rev = float(data.get("reversal_potential", -80))
            v_min = float(data.get("v_min", -100))
            v_max = float(data.get("v_max", 50))
            v_step = float(data.get("v_step", 10))
            
            # Generar voltajes
            voltages = list(np.arange(v_min, v_max + v_step, v_step))
            
            # Calcular
            result = self.solver_service.generate_iv_curve(
                conductance=g,
                reversal_potential=e_rev,
                voltage_range=(v_min, v_max),
                voltage_step=v_step
            )
            
            # Mostrar resultados
            results_data = {
                "Conductancia": f"{g:.2f} nS",
                "Potencial de reversión": f"{e_rev:.1f} mV",
                "Rango de voltaje": f"{v_min:.0f} a {v_max:.0f} mV",
                "Puntos generados": str(len(result.voltages))
            }
            
            self.result_panel.show_results(
                title="📊 Curva I-V Generada",
                results=results_data,
                interpretation=f"Potencial de reversión en {e_rev:.1f} mV. "
                              f"La corriente cambia de dirección en este punto."
            )
            
            # Graficar curva I-V
            if result.iv_curve:
                self.plot_canvas.plot_iv_curve(
                    voltage=result.iv_curve.voltage,
                    current=result.iv_curve.current,
                    reversal_potential=e_rev,
                    title="Curva I-V"
                )
            
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
        
        self.plot_canvas.draw()
    
    def _plot_ghk_contributions(self, result):
        """Grafica contribuciones de cada ion al Vm."""
        self.plot_canvas.clear()
        
        ions = list(result.ion_contributions.keys())
        contributions = [result.ion_contributions[ion] * 100 for ion in ions]
        
        colors = ["steelblue", "coral", "seagreen"]
        bars = self.plot_canvas.ax.bar(ions, contributions, color=colors[:len(ions)])
        
        self.plot_canvas.ax.set_ylabel("Contribución (%)")
        self.plot_canvas.ax.set_title(f"Contribución al Vm = {result.membrane_potential:.1f} mV")
        self.plot_canvas.ax.set_ylim(0, 100)
        
        # Anotar valores
        for bar, val in zip(bars, contributions):
            self.plot_canvas.ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 2,
                f"{val:.1f}%",
                ha="center",
                fontsize=10
            )
        
        self.plot_canvas.draw()
    
    def _set_nernst_example(self, ion: str, out: str, inn: str, valence: str):
        """Establece valores de ejemplo para Nernst."""
        self.nernst_form.set_value("ion", ion)
        self.nernst_form.set_value("conc_out", out)
        self.nernst_form.set_value("conc_in", inn)
        self.nernst_form.set_value("valence", valence.replace("+", ""))
    
    def _set_ghk_scenario(self, scenario: str):
        """Establece un escenario predefinido para GHK."""
        if scenario == "rest":
            self.ghk_form.set_value("p_na", "0.04")
            self.ghk_form.set_value("p_k", "1.0")
            self.ghk_form.set_value("p_cl", "0.45")
        elif scenario == "depol":
            # Durante potencial de acción
            self.ghk_form.set_value("p_na", "15.0")
            self.ghk_form.set_value("p_k", "1.0")
            self.ghk_form.set_value("p_cl", "0.45")
        elif scenario == "hyper":
            # Hiperpolarización
            self.ghk_form.set_value("p_na", "0.01")
            self.ghk_form.set_value("p_k", "5.0")
            self.ghk_form.set_value("p_cl", "0.45")
    
    def _set_iv_example(self, conductance: str, reversal: str):
        """Establece valores de ejemplo para curva I-V."""
        self.iv_form.set_value("conductance", conductance)
        self.iv_form.set_value("reversal_potential", reversal)
