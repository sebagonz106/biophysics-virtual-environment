"""
Componente de formulario de entrada de datos.
"""

import customtkinter as ctk
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass


@dataclass
class FormField:
    """Define un campo del formulario."""
    name: str
    label: str
    field_type: str = "entry"  # entry, dropdown, checkbox
    default: Any = None
    unit: str = ""
    options: Optional[List[str]] = None  # Para dropdowns
    tooltip: str = ""
    required: bool = True


class InputForm(ctk.CTkFrame):
    """
    Formulario de entrada de datos reutilizable.
    """
    
    def __init__(
        self,
        master,
        fields: List[FormField],
        on_submit: Optional[Callable[[Dict[str, Any]], None]] = None,
        submit_text: str = "Calcular",
        title: Optional[str] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        
        self.fields = fields
        self.on_submit = on_submit
        self.submit_text = submit_text
        self.title = title
        
        self.widgets: Dict[str, Any] = {}
        self.labels: Dict[str, ctk.CTkLabel] = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del formulario."""
        row = 0
        
        # Título opcional
        if self.title:
            title_label = ctk.CTkLabel(
                self,
                text=self.title,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title_label.grid(row=row, column=0, columnspan=3, pady=(0, 15), sticky="w")
            row += 1
        
        # Crear campos
        for field in self.fields:
            self._create_field(field, row)
            row += 1
        
        # Botón de submit
        self.submit_btn = ctk.CTkButton(
            self,
            text=f"🔄 {self.submit_text}",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self._on_submit
        )
        self.submit_btn.grid(row=row, column=0, columnspan=3, pady=(20, 0), sticky="ew")
    
    def _create_field(self, field: FormField, row: int):
        """Crea un campo individual."""
        # Label
        label_text = field.label
        if field.required:
            label_text += " *"
        
        label = ctk.CTkLabel(
            self,
            text=label_text,
            font=ctk.CTkFont(size=13)
        )
        label.grid(row=row, column=0, padx=(0, 10), pady=5, sticky="w")
        self.labels[field.name] = label
        
        # Widget según tipo
        if field.field_type == "entry":
            widget = ctk.CTkEntry(
                self,
                width=150,
                placeholder_text=str(field.default) if field.default else ""
            )
            if field.default is not None:
                widget.insert(0, str(field.default))
                
        elif field.field_type == "dropdown":
            widget = ctk.CTkComboBox(
                self,
                width=150,
                values=field.options or [],
                state="readonly"
            )
            if field.default:
                widget.set(field.default)
            elif field.options:
                widget.set(field.options[0])
                
        elif field.field_type == "checkbox":
            widget = ctk.CTkCheckBox(
                self,
                text="",
                width=50
            )
            if field.default:
                widget.select()
        else:
            widget = ctk.CTkEntry(self, width=150)
        
        widget.grid(row=row, column=1, padx=5, pady=5, sticky="w")
        self.widgets[field.name] = widget
        
        # Unidad
        if field.unit:
            unit_label = ctk.CTkLabel(
                self,
                text=field.unit,
                font=ctk.CTkFont(size=12),
                text_color="gray"
            )
            unit_label.grid(row=row, column=2, padx=(5, 0), pady=5, sticky="w")
    
    def _on_submit(self):
        """Maneja el envío del formulario."""
        if self.on_submit:
            values = self.get_values()
            self.on_submit(values)
    
    def get_values(self) -> Dict[str, Any]:
        """
        Obtiene los valores actuales del formulario.
        
        Returns:
            Diccionario con los valores
        """
        values = {}
        
        for field in self.fields:
            widget = self.widgets[field.name]
            
            if field.field_type == "entry":
                value = widget.get()
                # Intentar convertir a número
                try:
                    if "." in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                    
            elif field.field_type == "dropdown":
                value = widget.get()
                
            elif field.field_type == "checkbox":
                value = widget.get() == 1
            else:
                value = widget.get()
            
            values[field.name] = value
        
        return values
    
    def set_values(self, values: Dict[str, Any]):
        """
        Establece valores en el formulario.
        
        Args:
            values: Diccionario con los valores
        """
        for name, value in values.items():
            if name in self.widgets:
                widget = self.widgets[name]
                
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, str(value))
                elif isinstance(widget, ctk.CTkComboBox):
                    widget.set(str(value))
                elif isinstance(widget, ctk.CTkCheckBox):
                    if value:
                        widget.select()
                    else:
                        widget.deselect()
    
    def clear(self):
        """Limpia todos los campos."""
        for field in self.fields:
            widget = self.widgets[field.name]
            
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                if field.default is not None:
                    widget.insert(0, str(field.default))
            elif isinstance(widget, ctk.CTkComboBox):
                if field.default:
                    widget.set(field.default)
                elif field.options:
                    widget.set(field.options[0])
            elif isinstance(widget, ctk.CTkCheckBox):
                widget.deselect()
                if field.default:
                    widget.select()
    
    def set_field_error(self, field_name: str, has_error: bool = True):
        """Marca un campo con error visual."""
        if field_name in self.labels:
            color = "red" if has_error else ("gray10", "gray90")
            self.labels[field_name].configure(text_color=color)

    def set_value(self, field_name: str, value: Any):
        """Establece el valor de un campo específico."""
        if field_name in self.widgets:
            widget = self.widgets[field_name]
            if isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                widget.insert(0, str(value))
            elif isinstance(widget, ctk.CTkComboBox):
                widget.set(str(value))
            elif isinstance(widget, ctk.CTkCheckBox):
                if bool(value):
                    widget.select()
                else:
                    widget.deselect()
