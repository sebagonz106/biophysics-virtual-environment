"""
Clasificador de tonicidad de soluciones.
"""

from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class TonicityClassification:
    """Resultado de la clasificación de tonicidad."""
    
    osmolarity: float
    tonicity: str  # "hipotónica", "isotónica", "hipertónica"
    relative_to_plasma: float  # Porcentaje respecto al plasma
    category_detail: str  # Descripción más detallada


class TonicityClassifier:
    """
    Clasificador de tonicidad de soluciones respecto al plasma sanguíneo.
    
    La tonicidad describe el efecto de una solución sobre el volumen celular:
    - Hipotónica: causa hinchazón celular
    - Isotónica: no altera el volumen celular  
    - Hipertónica: causa encogimiento celular
    """
    
    # Valores de referencia del plasma (mOsm/L)
    PLASMA_OSMOLARITY = 285
    
    # Rangos de clasificación
    HYPOTONIC_SEVERE = 200      # < 200 mOsm/L
    HYPOTONIC_MODERATE = 250    # 200-250 mOsm/L
    ISOTONIC_MIN = 275          # 275-295 mOsm/L
    ISOTONIC_MAX = 295
    HYPERTONIC_MODERATE = 350   # 295-350 mOsm/L
    HYPERTONIC_SEVERE = 400     # > 400 mOsm/L
    
    def classify(self, osmolarity: float) -> TonicityClassification:
        """
        Clasifica una solución según su osmolaridad.
        
        Args:
            osmolarity: Osmolaridad de la solución en mOsm/L
            
        Returns:
            TonicityClassification con los detalles de la clasificación
        """
        relative = ((osmolarity - self.PLASMA_OSMOLARITY) / self.PLASMA_OSMOLARITY) * 100
        
        if osmolarity < self.HYPOTONIC_SEVERE:
            tonicity = "hipotónica"
            detail = "Severamente hipotónica - Alto riesgo de lisis celular"
        elif osmolarity < self.HYPOTONIC_MODERATE:
            tonicity = "hipotónica"
            detail = "Moderadamente hipotónica - Hinchazón celular significativa"
        elif osmolarity < self.ISOTONIC_MIN:
            tonicity = "hipotónica"
            detail = "Ligeramente hipotónica - Hinchazón celular leve"
        elif osmolarity <= self.ISOTONIC_MAX:
            tonicity = "isotónica"
            detail = "Isotónica - Volumen celular estable"
        elif osmolarity < self.HYPERTONIC_MODERATE:
            tonicity = "hipertónica"
            detail = "Ligeramente hipertónica - Crenación leve"
        elif osmolarity < self.HYPERTONIC_SEVERE:
            tonicity = "hipertónica"
            detail = "Moderadamente hipertónica - Crenación significativa"
        else:
            tonicity = "hipertónica"
            detail = "Severamente hipertónica - Crenación severa"
        
        return TonicityClassification(
            osmolarity=osmolarity,
            tonicity=tonicity,
            relative_to_plasma=round(relative, 2),
            category_detail=detail
        )
    
    def classify_multiple(
        self, 
        solutions: List[Tuple[str, float]]
    ) -> List[Tuple[str, TonicityClassification]]:
        """
        Clasifica múltiples soluciones.
        
        Args:
            solutions: Lista de tuplas (nombre, osmolaridad)
            
        Returns:
            Lista de tuplas (nombre, clasificación)
        """
        return [
            (name, self.classify(osm))
            for name, osm in solutions
        ]
    
    def get_clinical_examples(self) -> dict:
        """
        Retorna ejemplos clínicos de soluciones comunes.
        """
        return {
            "Solución salina 0.9% (NaCl)": {
                "osmolarity": 308,
                "classification": self.classify(308),
                "uso": "Reposición de volumen, dilución de medicamentos"
            },
            "Solución salina 0.45%": {
                "osmolarity": 154,
                "classification": self.classify(154),
                "uso": "Hipernatremia, deshidratación hipertónica"
            },
            "Dextrosa 5%": {
                "osmolarity": 278,
                "classification": self.classify(278),
                "uso": "Aporte calórico, vehículo para medicamentos"
            },
            "Lactato de Ringer": {
                "osmolarity": 273,
                "classification": self.classify(273),
                "uso": "Reposición de volumen en cirugía"
            },
            "Manitol 20%": {
                "osmolarity": 1098,
                "classification": self.classify(1098),
                "uso": "Edema cerebral, diurético osmótico"
            },
        }
