"""
Modelos de resultados de los Solvers.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
import numpy as np


class SolverResult(BaseModel):
    """Clase base para resultados de solvers."""
    
    solver_name: str = Field(default="", description="Nombre del solver utilizado")
    success: bool = Field(default=True, description="Si el cálculo fue exitoso")
    error_message: Optional[str] = Field(default=None, description="Mensaje de error si falló")
    
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Parámetros de entrada")
    
    class Config:
        arbitrary_types_allowed = True


class OsmosisResult(SolverResult):
    """Resultado del módulo de Ósmosis."""
    
    solver_name: str = "osmosis"
    
    # Resultados principales
    osmolarity: Optional[float] = Field(default=None, description="Osmolaridad calculada (mOsm/L)")
    tonicity: Optional[str] = Field(default=None, description="Clasificación de tonicidad")
    
    # Respuesta celular
    cell_response: Optional[str] = Field(default=None, description="Respuesta celular predicha")
    volume_change_percent: Optional[float] = Field(default=None, description="Cambio de volumen (%)")
    
    # Para gráficos
    volume_data: Optional[Dict[str, List[float]]] = Field(
        default=None,
        description="Datos para gráfico de volumen (tiempo, volumen)"
    )
    
    # Retroalimentación
    interpretation: Optional[str] = Field(default=None, description="Interpretación del resultado")
    feedback: List[str] = Field(default_factory=list, description="Puntos de retroalimentación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "solver_name": "osmosis",
                "success": True,
                "inputs": {
                    "solute": "NaCl",
                    "concentration_mM": 150,
                    "dissociation_coef": 2
                },
                "osmolarity": 300,
                "tonicity": "isotónica",
                "cell_response": "equilibrio",
                "volume_change_percent": 0,
                "interpretation": "La célula mantiene su volumen normal en esta solución isotónica.",
                "feedback": [
                    "La osmolaridad (300 mOsm/L) está dentro del rango fisiológico",
                    "No hay gradiente osmótico neto a través de la membrana"
                ]
            }
        }


class NernstResult(BaseModel):
    """Resultado del cálculo de potencial de Nernst."""
    
    ion: str = Field(..., description="Ion evaluado")
    z: int = Field(..., description="Valencia del ion")
    E_eq: float = Field(..., description="Potencial de equilibrio (mV)")
    
    C_out: float = Field(..., description="Concentración extracelular (mM)")
    C_in: float = Field(..., description="Concentración intracelular (mM)")
    temperature_K: float = Field(..., description="Temperatura (K)")
    
    interpretation: str = Field(..., description="Interpretación del resultado")


class GHKResult(BaseModel):
    """Resultado de la ecuación de Goldman-Hodgkin-Katz."""
    
    membrane_potential: float = Field(..., description="Potencial de membrana (mV)")
    
    permeabilities: Dict[str, float] = Field(..., description="Permeabilidades relativas")
    concentrations: Dict[str, Dict[str, float]] = Field(..., description="Concentraciones iónicas")
    
    dominant_ion: str = Field(..., description="Ion dominante en el potencial")
    interpretation: str = Field(..., description="Interpretación del resultado")


class IVCurveData(BaseModel):
    """Datos para curva I-V."""
    
    voltage: List[float] = Field(..., description="Valores de voltaje (mV)")
    current: List[float] = Field(..., description="Valores de corriente (pA o nA)")
    
    reversal_potential: float = Field(..., description="Potencial de reversión (mV)")
    conductance: float = Field(..., description="Conductancia (nS)")


class PatchClampResult(SolverResult):
    """Resultado del módulo de Patch Clamp."""
    
    solver_name: str = "patch_clamp"
    
    # Resultados de Nernst
    nernst_results: List[NernstResult] = Field(
        default_factory=list,
        description="Potenciales de equilibrio calculados"
    )
    
    # Resultado de GHK
    ghk_result: Optional[GHKResult] = Field(default=None, description="Resultado de ecuación GHK")
    
    # Curva I-V
    iv_curve: Optional[IVCurveData] = Field(default=None, description="Datos de curva I-V")
    
    # Interpretación del experimento
    experiment_type: Optional[str] = Field(
        default=None,
        description="Tipo de configuración (cell-attached, whole-cell, etc.)"
    )
    interpretation: Optional[str] = Field(default=None, description="Interpretación general")
    feedback: List[str] = Field(default_factory=list, description="Puntos de retroalimentación")
    
    class Config:
        json_schema_extra = {
            "example": {
                "solver_name": "patch_clamp",
                "success": True,
                "inputs": {
                    "ion": "K+",
                    "K_out": 5,
                    "K_in": 140,
                    "temperature": 310
                },
                "nernst_results": [
                    {
                        "ion": "K+",
                        "z": 1,
                        "E_eq": -89.1,
                        "C_out": 5,
                        "C_in": 140,
                        "temperature_K": 310,
                        "interpretation": "El potencial de equilibrio del K+ es cercano al potencial de reposo"
                    }
                ],
                "interpretation": "El K+ tiende a salir de la célula siguiendo su gradiente electroquímico"
            }
        }
