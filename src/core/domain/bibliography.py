"""
Modelo de datos para Bibliografía.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class BibliographyItem(BaseModel):
    """Clase base para items bibliográficos."""
    
    id: str = Field(..., description="Identificador único")
    title: str = Field(..., description="Título del recurso")
    authors: List[str] = Field(..., description="Lista de autores")
    year: int = Field(..., description="Año de publicación")
    
    type: Literal["book", "paper", "resource"] = Field(..., description="Tipo de recurso")
    
    local_path: Optional[str] = Field(None, description="Ruta relativa al PDF local")
    url: Optional[str] = Field(None, description="URL externa si está disponible")
    
    topics: List[str] = Field(default_factory=list, description="Temas relacionados")
    notes: Optional[str] = Field(None, description="Notas personales")
    is_primary: bool = Field(default=False, description="Si es bibliografía principal")


class Book(BibliographyItem):
    """Representa un libro de texto."""
    
    type: Literal["book"] = "book"
    
    edition: Optional[str] = Field(None, description="Edición del libro")
    publisher: Optional[str] = Field(None, description="Editorial")
    isbn: Optional[str] = Field(None, description="ISBN")
    
    chapters_relevant: List[dict] = Field(
        default_factory=list,
        description="Capítulos relevantes para el curso"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "lehninger",
                "title": "Principios de Bioquímica de Lehninger",
                "authors": ["David L. Nelson", "Michael M. Cox"],
                "year": 2017,
                "type": "book",
                "edition": "7th",
                "publisher": "W.H. Freeman",
                "isbn": "978-1464126116",
                "local_path": "bibliography/pdfs/lehninger_7th.pdf",
                "topics": ["bioquímica", "bioenergética", "membranas"],
                "is_primary": True,
                "chapters_relevant": [
                    {"number": 11, "title": "Membranas biológicas y transporte"},
                    {"number": 13, "title": "Bioenergética y tipos de reacciones"}
                ],
                "notes": "Texto principal del curso"
            }
        }


class Paper(BibliographyItem):
    """Representa un artículo científico."""
    
    type: Literal["paper"] = "paper"
    
    journal: Optional[str] = Field(None, description="Revista científica")
    volume: Optional[str] = Field(None, description="Volumen")
    pages: Optional[str] = Field(None, description="Páginas")
    doi: Optional[str] = Field(None, description="DOI del artículo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "neher_sakmann_1976",
                "title": "Single-channel currents recorded from membrane of denervated frog muscle fibres",
                "authors": ["Erwin Neher", "Bert Sakmann"],
                "year": 1976,
                "type": "paper",
                "journal": "Nature",
                "volume": "260",
                "pages": "799-802",
                "doi": "10.1038/260799a0",
                "topics": ["patch clamp", "canales iónicos"],
                "notes": "Artículo fundacional de la técnica Patch Clamp"
            }
        }
