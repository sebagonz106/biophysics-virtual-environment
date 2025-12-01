"""
Componentes de UI específicos para el módulo de Ósmosis.

Contiene widgets reutilizables para entrada de solutos.
"""

import customtkinter as ctk
from typing import List, Dict, Optional, Callable


# Constantes: Solutos predefinidos con sus propiedades
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


class SoluteEntryRow(ctk.CTkFrame):
    """
    Fila para entrada de datos de un soluto.
    
    Muestra controles para:
    - Selección de soluto (predefinido o personalizado)
    - Concentración (mM)
    - Coeficiente de disociación (j)
    - Permeabilidad (cm/s)
    - Es penetrante (checkbox)
    - Botón eliminar
    """
    
    def __init__(
        self, 
        master, 
        on_remove: Optional[Callable] = None,
        predefined_solutes: Optional[Dict] = None,
        **kwargs
    ):
        """
        Inicializa la fila de entrada de soluto.
        
        Args:
            master: Widget padre
            on_remove: Callback cuando se elimina la fila
            predefined_solutes: Diccionario de solutos predefinidos (opcional)
        """
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.on_remove = on_remove
        self.solutes_data = predefined_solutes or PREDEFINED_SOLUTES
        
        self._create_widgets()
        self._on_solute_change(self.solute_var.get())
    
    def _create_widgets(self):
        """Crea los widgets de la fila."""
        # Selector de soluto
        self.solute_var = ctk.StringVar(value="NaCl")
        self.solute_combo = ctk.CTkComboBox(
            self,
            values=list(self.solutes_data.keys()),
            variable=self.solute_var,
            width=105,
            command=self._on_solute_change
        )
        self.solute_combo.grid(row=0, column=0, padx=(0, 8))
        
        # Concentración
        ctk.CTkLabel(self, text="C:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=1, padx=(0, 2)
        )
        self.conc_entry = ctk.CTkEntry(self, width=55, placeholder_text="mM")
        self.conc_entry.grid(row=0, column=2, padx=(0, 8))
        self.conc_entry.insert(0, "140")
        
        # Factor j
        ctk.CTkLabel(self, text="j:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=3, padx=(0, 2)
        )
        self.j_entry = ctk.CTkEntry(self, width=35, placeholder_text="j")
        self.j_entry.grid(row=0, column=4, padx=(0, 8))
        self.j_entry.insert(0, "2")
        self.j_entry.configure(state="disabled")

        # Permeabilidad
        ctk.CTkLabel(self, text="Perm:", font=ctk.CTkFont(size=10)).grid(
            row=0, column=5, padx=(0, 2)
        )
        self.perm_entry = ctk.CTkEntry(self, width=70, placeholder_text="cm/s")
        self.perm_entry.grid(row=0, column=6, padx=(0, 8))
        self.perm_entry.insert(0, "0.0")

        # Checkbox penetrante
        ctk.CTkLabel(self, text="P:", font=ctk.CTkFont(size=11)).grid(
            row=0, column=7, padx=(0, 2)
        )
        self.penetrant_var = ctk.BooleanVar(value=False)
        self.penetrant_check = ctk.CTkCheckBox(
            self,
            text="",
            variable=self.penetrant_var,
            width=20,
            checkbox_width=18,
            checkbox_height=18,
            command=self._on_penetrant_change
        )
        self.penetrant_check.grid(row=0, column=8, padx=(0, 8))
        self.penetrant_check.configure(state="disabled")
        
        # Botón eliminar
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
    
    def _on_penetrant_change(self):
        """Maneja el cambio del checkbox de penetrante."""
        current = self.solute_var.get()
        if current != "Personalizado":
            current_j = self.j_entry.get()
            self.solute_var.set("Personalizado")
            self.j_entry.configure(state="normal")
            self.j_entry.delete(0, "end")
            self.j_entry.insert(0, current_j)
            self.penetrant_check.configure(state="normal")
            self.perm_entry.configure(state="normal")
    
    def _on_solute_change(self, choice: str):
        """Actualiza campos según el soluto seleccionado."""
        if choice == "Personalizado":
            self.j_entry.configure(state="normal")
            self.penetrant_check.configure(state="normal")
        else:
            info = self.solutes_data.get(
                choice, 
                {"j": 1, "penetrant": False, "permeability": 0.0}
            )
            # Actualizar j
            self.j_entry.configure(state="normal")
            self.j_entry.delete(0, "end")
            self.j_entry.insert(0, str(info["j"]))
            self.j_entry.configure(state="disabled")
            
            # Actualizar penetrante
            self.penetrant_var.set(info["penetrant"])
            self.penetrant_check.configure(state="disabled")
            
            # Actualizar permeabilidad
            perm = info.get("permeability", 0.0)
            self.perm_entry.delete(0, "end")
            self.perm_entry.insert(0, str(perm))
    
    def _remove(self):
        """Elimina esta fila."""
        if self.on_remove:
            self.on_remove(self)
        self.destroy()
    
    def get_data(self) -> Dict:
        """
        Obtiene los datos del soluto.
        
        Returns:
            Diccionario con name, concentration, j, is_penetrant, permeability
        """
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
    
    def set_data(self, data: Dict):
        """
        Establece los datos del soluto.
        
        Args:
            data: Diccionario con name, concentration, j, is_penetrant, permeability
        """
        name = data.get("name", "Personalizado")
        self.solute_var.set(name)
        self._on_solute_change(name)
        
        # Concentración
        self.conc_entry.delete(0, "end")
        self.conc_entry.insert(0, str(data.get("concentration", 0)))
        
        # Si es personalizado, permitir edición de j y penetrante
        if name == "Personalizado":
            self.j_entry.delete(0, "end")
            self.j_entry.insert(0, str(data.get("j", 1)))
            self.penetrant_var.set(data.get("is_penetrant", False))
        
        # Permeabilidad
        self.perm_entry.delete(0, "end")
        self.perm_entry.insert(0, str(data.get("permeability", 0.0)))


class SoluteSection(ctk.CTkFrame):
    """
    Sección para agregar múltiples solutos.
    
    Contiene un título, botón para agregar solutos, y una lista
    de filas SoluteEntryRow.
    """
    
    def __init__(self, master, title: str, **kwargs):
        """
        Inicializa la sección de solutos.
        
        Args:
            master: Widget padre
            title: Título de la sección
        """
        super().__init__(master, **kwargs)
        
        self.solute_rows: List[SoluteEntryRow] = []
        
        self.grid_columnconfigure(0, weight=1)
        
        self._create_widgets(title)
        self._add_solute()  # Agregar un soluto por defecto
    
    def _create_widgets(self, title: str):
        """Crea los widgets de la sección."""
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
        """
        Obtiene datos de todos los solutos.
        
        Returns:
            Lista de diccionarios con datos de cada soluto
        """
        return [row.get_data() for row in self.solute_rows if row.winfo_exists()]
    
    def set_all_solutes(self, solutes: List[Dict]):
        """
        Establece todos los solutos.
        
        Args:
            solutes: Lista de diccionarios con datos de solutos
        """
        self.clear_all()
        for i, solute_data in enumerate(solutes):
            if i > 0:
                self._add_solute()
            if self.solute_rows:
                self.solute_rows[-1].set_data(solute_data)
    
    def clear_all(self):
        """Elimina todos los solutos y agrega uno por defecto."""
        for row in self.solute_rows[:]:
            row.destroy()
        self.solute_rows.clear()
        self._add_solute()
