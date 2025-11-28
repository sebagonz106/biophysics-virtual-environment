"""
Modelo de datos para Conferencias Digitales.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date


class Conference(BaseModel):
    """Representa una conferencia digital del curso."""
    
    id: str = Field(..., description="Identificador único de la conferencia")
    title: str = Field(..., description="Título de la conferencia")
    topic: str = Field(..., description="Tema o unidad a la que pertenece")
    order: int = Field(default=1, description="Orden dentro del tema")
    
    description: Optional[str] = Field(None, description="Descripción breve del contenido")
    objectives: List[str] = Field(default_factory=list, description="Objetivos de aprendizaje")
    
    local_path: Optional[str] = Field(None, description="Ruta relativa al archivo PDF")
    duration_minutes: Optional[int] = Field(None, description="Duración estimada en minutos")
    
    date_created: Optional[date] = Field(None, description="Fecha de creación")
    keywords: List[str] = Field(default_factory=list, description="Palabras clave")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "conf_osmosis_01",
                "title": "Introducción a la Ósmosis",
                "topic": "Transporte a través de membranas",
                "order": 1,
                "description": "Conceptos fundamentales de ósmosis y presión osmótica",
                "objectives": [
                    "Definir ósmosis y presión osmótica",
                    "Calcular osmolaridad de soluciones",
                    "Clasificar soluciones según su tonicidad"
                ],
                "local_path": "conferences/pdfs/osmosis_introduccion.pdf",
                "duration_minutes": 45,
                "keywords": ["ósmosis", "tonicidad", "osmolaridad"]
            }
        }
