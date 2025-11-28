"""
Canvas para gráficos Matplotlib embebidos.
"""

import customtkinter as ctk
from typing import Optional, Callable
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np


class PlotCanvas(ctk.CTkFrame):
    """
    Canvas para mostrar gráficos Matplotlib embebidos en CustomTkinter.
    """
    
    def __init__(
        self,
        master,
        figsize: tuple = (6, 4),
        dpi: int = 100,
        show_toolbar: bool = True,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.figsize = figsize
        self.dpi = dpi
        self.show_toolbar = show_toolbar
        
        self._create_canvas()
    
    def _create_canvas(self):
        """Crea el canvas de matplotlib."""
        # Crear figura
        self.figure = Figure(figsize=self.figsize, dpi=self.dpi)
        self.ax = self.figure.add_subplot(111)
        
        # Crear canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill="both", expand=True)
        
        # Toolbar opcional
        if self.show_toolbar:
            self.toolbar_frame = ctk.CTkFrame(self)
            self.toolbar_frame.pack(fill="x")
            self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
            self.toolbar.update()
    
    def clear(self):
        """Limpia el gráfico."""
        self.ax.clear()
        self.canvas.draw()

    def draw(self):
        """Redibuja el canvas (compatibilidad con vistas)."""
        self.canvas.draw()
    
    def plot(
        self,
        x: list,
        y: list,
        xlabel: str = "X",
        ylabel: str = "Y",
        title: str = "",
        color: str = "blue",
        linestyle: str = "-",
        marker: Optional[str] = None,
        label: Optional[str] = None,
        clear_first: bool = True,
        grid: bool = True
    ):
        """
        Dibuja una línea en el gráfico.
        
        Args:
            x: Datos del eje X
            y: Datos del eje Y
            xlabel: Etiqueta del eje X
            ylabel: Etiqueta del eje Y
            title: Título del gráfico
            color: Color de la línea
            linestyle: Estilo de línea
            marker: Marcador de puntos
            label: Etiqueta para la leyenda
            clear_first: Si limpiar antes de dibujar
            grid: Si mostrar cuadrícula
        """
        if clear_first:
            self.ax.clear()
        
        self.ax.plot(x, y, color=color, linestyle=linestyle, marker=marker, label=label)
        
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        if title:
            self.ax.set_title(title)
        if grid:
            self.ax.grid(True, alpha=0.3)
        if label:
            self.ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_volume_change(
        self,
        time: list,
        volume: list,
        title: str = "Cambio de Volumen Celular"
    ):
        """Gráfico específico para cambio de volumen celular."""
        self.clear()
        
        self.ax.plot(time, volume, color="#2196F3", linewidth=2)
        self.ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5, label="V₀")
        self.ax.fill_between(time, 1.0, volume, alpha=0.3, color="#2196F3")
        
        self.ax.set_xlabel("Tiempo (u.a.)")
        self.ax.set_ylabel("Volumen Relativo (V/V₀)")
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_iv_curve(
        self,
        voltage: list,
        current: list,
        reversal_potential: Optional[float] = None,
        title: str = "Curva I-V"
    ):
        """Gráfico específico para curvas I-V."""
        self.clear()
        
        self.ax.plot(voltage, current, color="#4CAF50", linewidth=2)
        self.ax.axhline(y=0, color="gray", linestyle="-", alpha=0.5)
        self.ax.axvline(x=0, color="gray", linestyle="-", alpha=0.5)
        
        if reversal_potential is not None:
            self.ax.axvline(
                x=reversal_potential,
                color="red",
                linestyle="--",
                alpha=0.7,
                label=f"E_rev = {reversal_potential:.1f} mV"
            )
            self.ax.plot(reversal_potential, 0, 'ro', markersize=8)
        
        self.ax.set_xlabel("Voltaje (mV)")
        self.ax.set_ylabel("Corriente (pA)")
        self.ax.set_title(title)
        self.ax.grid(True, alpha=0.3)
        if reversal_potential is not None:
            self.ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def plot_boyle_vant_hoff(
        self,
        osmolarity: list,
        volume: list,
        plasma_osm: float = 285
    ):
        """Gráfico de la curva de Boyle-van't Hoff."""
        self.clear()
        
        self.ax.plot(osmolarity, volume, color="#9C27B0", linewidth=2)
        self.ax.axvline(
            x=plasma_osm,
            color="red",
            linestyle="--",
            alpha=0.7,
            label=f"Plasma = {plasma_osm} mOsm/L"
        )
        self.ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.5)
        
        # Marcar zonas
        self.ax.fill_between(
            [min(osmolarity), plasma_osm * 0.95],
            0, 2,
            alpha=0.1, color="blue",
            label="Hipotónico"
        )
        self.ax.fill_between(
            [plasma_osm * 1.05, max(osmolarity)],
            0, 2,
            alpha=0.1, color="orange",
            label="Hipertónico"
        )
        
        self.ax.set_xlabel("Osmolaridad (mOsm/L)")
        self.ax.set_ylabel("Volumen Relativo (V/V₀)")
        self.ax.set_title("Curva de Boyle-van't Hoff")
        self.ax.set_ylim(0.5, 2.0)
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc="upper right", fontsize=8)
        
        self.figure.tight_layout()
        self.canvas.draw()

    def plot_boyle_vant_hoff_params(
        self,
        initial_volume: float,
        non_osmotic_fraction: float,
        internal_osmolarity: float,
        external_osmolarity_current: float,
        plasma_osm: float = 285
    ):
        """Genera y dibuja la curva con parámetros (compatibilidad con vistas)."""
        b = non_osmotic_fraction
        osm_range = np.linspace(100, 600, 100)
        volumes = b + (1 - b) * (internal_osmolarity / osm_range)
        self.plot_boyle_vant_hoff(osmolarity=osm_range.tolist(), volume=volumes.tolist(), plasma_osm=plasma_osm)
    
    def plot_nernst_comparison(self, nernst_results: list):
        """Gráfico comparativo de potenciales de Nernst."""
        self.clear()
        
        ions = [r.ion for r in nernst_results]
        potentials = [r.E_eq for r in nernst_results]
        
        colors = ["#F44336", "#2196F3", "#4CAF50", "#FF9800", "#9C27B0"]
        
        bars = self.ax.barh(ions, potentials, color=colors[:len(ions)])
        
        # Línea de potencial de reposo
        self.ax.axvline(x=-70, color="black", linestyle="--", alpha=0.7, label="V_reposo ≈ -70 mV")
        self.ax.axvline(x=0, color="gray", linestyle="-", alpha=0.3)
        
        self.ax.set_xlabel("Potencial de Equilibrio (mV)")
        self.ax.set_title("Potenciales de Nernst")
        self.ax.legend(loc="lower right")
        self.ax.grid(True, alpha=0.3, axis="x")
        
        # Añadir valores en las barras
        for bar, val in zip(bars, potentials):
            self.ax.text(
                val + (5 if val >= 0 else -5),
                bar.get_y() + bar.get_height()/2,
                f"{val:.1f}",
                va="center",
                ha="left" if val >= 0 else "right",
                fontsize=9
            )
        
        self.figure.tight_layout()
        self.canvas.draw()
