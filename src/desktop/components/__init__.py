"""
Componentes de interfaz reutilizables.
"""

from .sidebar import Sidebar
from .input_form import InputForm, FormField
from .result_panel import ResultPanel
from .plot_canvas import PlotCanvas
from .solute_widgets import SoluteEntryRow, SoluteSection, PREDEFINED_SOLUTES

__all__ = [
    "Sidebar",
    "InputForm",
    "FormField",
    "ResultPanel",
    "PlotCanvas",
    "SoluteEntryRow",
    "SoluteSection",
    "PREDEFINED_SOLUTES",
]
