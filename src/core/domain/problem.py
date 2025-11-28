"""
Modelo de datos para Problemas y Ejercicios.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class ProblemStep(BaseModel):
    """Representa un paso en la solución de un problema."""
    
    step_number: int = Field(..., description="Número del paso")
    description: str = Field(..., description="Descripción del paso")
    formula: Optional[str] = Field(None, description="Fórmula aplicada (LaTeX)")
    calculation: Optional[str] = Field(None, description="Cálculo realizado")
    result: Optional[Dict[str, Any]] = Field(None, description="Resultado del paso")
    explanation: Optional[str] = Field(None, description="Explicación adicional")


class ProblemSolution(BaseModel):
    """Representa la solución completa de un problema."""
    
    steps: List[ProblemStep] = Field(..., description="Pasos de la solución")
    final_answer: Dict[str, Any] = Field(..., description="Respuesta final")
    interpretation: Optional[str] = Field(None, description="Interpretación del resultado")
    
    tips: List[str] = Field(default_factory=list, description="Consejos adicionales")


class Problem(BaseModel):
    """Representa un problema o ejercicio propuesto."""
    
    id: str = Field(..., description="Identificador único del problema")
    title: str = Field(..., description="Título del problema")
    
    category: str = Field(..., description="Categoría principal (osmosis, patch_clamp, etc.)")
    subcategory: Optional[str] = Field(None, description="Subcategoría")
    
    difficulty: Literal[1, 2, 3, 4, 5] = Field(
        default=3,
        description="Nivel de dificultad (1=muy fácil, 5=muy difícil)"
    )
    
    tags: List[str] = Field(default_factory=list, description="Etiquetas")
    
    # Enunciado
    statement: str = Field(..., description="Enunciado del problema")
    given_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Datos proporcionados"
    )
    
    # Solución
    solution: Optional[ProblemSolution] = Field(None, description="Solución detallada")
    
    # Relación con solvers interactivos
    related_solver: Optional[str] = Field(
        None,
        description="Nombre del solver interactivo relacionado"
    )
    solver_params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parámetros predefinidos para el solver"
    )
    
    # Metadatos
    references: List[str] = Field(
        default_factory=list,
        description="Referencias bibliográficas relacionadas"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "osm_001",
                "title": "Cálculo de osmolaridad de solución salina",
                "category": "osmosis",
                "subcategory": "osmolaridad",
                "difficulty": 2,
                "tags": ["osmolaridad", "NaCl", "tonicidad"],
                "statement": "Se prepara una solución de NaCl al 0.9% (p/v). Calcule la osmolaridad de esta solución y clasifíquela según su tonicidad respecto al plasma sanguíneo.",
                "given_data": {
                    "soluto": "NaCl",
                    "concentracion_porcentaje": 0.9,
                    "peso_molecular_NaCl": {"value": 58.44, "unit": "g/mol"},
                    "coef_disociacion": 2,
                    "osmolaridad_plasma": {"value": 285, "unit": "mOsm/L"}
                },
                "solution": {
                    "steps": [
                        {
                            "step_number": 1,
                            "description": "Convertir concentración a molaridad",
                            "formula": "M = (% p/v × 10) / PM",
                            "calculation": "M = (0.9 × 10) / 58.44 = 0.154 M = 154 mM",
                            "result": {"value": 154, "unit": "mM"}
                        },
                        {
                            "step_number": 2,
                            "description": "Calcular osmolaridad",
                            "formula": "Osm = M × i",
                            "calculation": "Osm = 154 mM × 2 = 308 mOsm/L",
                            "result": {"value": 308, "unit": "mOsm/L"}
                        }
                    ],
                    "final_answer": {"value": 308, "unit": "mOsm/L"},
                    "interpretation": "La solución es ligeramente hipertónica respecto al plasma (308 > 285 mOsm/L)"
                },
                "related_solver": "osmolarity_calculator",
                "references": ["lehninger_ch11"]
            }
        }
