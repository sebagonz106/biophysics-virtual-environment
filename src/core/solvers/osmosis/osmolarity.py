"""
Solver para cálculo de osmolaridad.
"""

from typing import Any, Dict, List, Optional
from ..base_solver import BaseSolver
from ...domain.solver_result import OsmosisResult


class OsmolaritySolver(BaseSolver):
    """
    Calcula la osmolaridad de una solución.
    
    La osmolaridad se calcula como:
        Osmolaridad = Concentración × Coeficiente de disociación × Coeficiente osmótico
        
    Donde:
        - Concentración: en mM (milimolar)
        - Coeficiente de disociación (i): número de partículas por molécula
        - Coeficiente osmótico (φ): factor de corrección para soluciones reales
    """
    
    name = "osmolarity_calculator"
    description = "Calcula la osmolaridad de una solución"
    
    # Coeficientes de disociación para solutos comunes
    DISSOCIATION_COEFFICIENTS = {
        "glucosa": 1,
        "urea": 1,
        "sacarosa": 1,
        "NaCl": 2,
        "KCl": 2,
        "CaCl2": 3,
        "MgCl2": 3,
        "Na2SO4": 3,
        "NaHCO3": 2,
    }
    
    # Coeficientes osmóticos aproximados
    OSMOTIC_COEFFICIENTS = {
        "glucosa": 1.01,
        "urea": 1.02,
        "sacarosa": 1.01,
        "NaCl": 0.93,
        "KCl": 0.92,
        "CaCl2": 0.86,
        "MgCl2": 0.89,
    }
    
    # Osmolaridad de referencia del plasma
    PLASMA_OSMOLARITY = 285  # mOsm/L
    PLASMA_RANGE = (275, 295)
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "concentration_mM": {
                "type": float,
                "description": "Concentración del soluto en milimolar (mM)",
                "unit": "mM",
                "range": (0, 10000),
            },
            "dissociation_coef": {
                "type": int,
                "description": "Coeficiente de disociación (i). Número de partículas por molécula",
                "default": 1,
                "range": (1, 5),
            },
            "osmotic_coef": {
                "type": float,
                "description": "Coeficiente osmótico (φ). Factor de corrección para soluciones reales",
                "default": 1.0,
                "range": (0.5, 1.5),
            },
            "solute_name": {
                "type": str,
                "description": "Nombre del soluto (opcional, para autocompletar coeficientes)",
                "default": None,
            },
        }
    
    def solve(
        self,
        concentration_mM: float,
        dissociation_coef: Optional[int] = None,
        osmotic_coef: Optional[float] = None,
        solute_name: Optional[str] = None,
        **kwargs
    ) -> OsmosisResult:
        """
        Calcula la osmolaridad de una solución.
        
        Args:
            concentration_mM: Concentración en milimolar
            dissociation_coef: Coeficiente de disociación (i)
            osmotic_coef: Coeficiente osmótico (φ)
            solute_name: Nombre del soluto para autocompletar coeficientes
            
        Returns:
            OsmosisResult con la osmolaridad calculada y clasificación
        """
        inputs = {
            "concentration_mM": concentration_mM,
            "solute_name": solute_name,
        }
        
        # Autocompletar coeficientes si se proporciona nombre del soluto
        if solute_name and solute_name.lower() in self.DISSOCIATION_COEFFICIENTS:
            solute_key = solute_name.lower() if solute_name.lower() != "nacl" else "NaCl"
            for key in self.DISSOCIATION_COEFFICIENTS:
                if key.lower() == solute_name.lower():
                    solute_key = key
                    break
            
            if dissociation_coef is None:
                dissociation_coef = self.DISSOCIATION_COEFFICIENTS.get(solute_key, 1)
            if osmotic_coef is None:
                osmotic_coef = self.OSMOTIC_COEFFICIENTS.get(solute_key, 1.0)
        
        # Valores por defecto
        dissociation_coef = dissociation_coef or 1
        osmotic_coef = osmotic_coef or 1.0
        
        inputs["dissociation_coef"] = dissociation_coef
        inputs["osmotic_coef"] = osmotic_coef
        
        # Validar parámetros
        if concentration_mM < 0:
            return OsmosisResult(
                success=False,
                error_message="La concentración no puede ser negativa",
                inputs=inputs
            )
        
        # Calcular osmolaridad
        osmolarity = concentration_mM * dissociation_coef * osmotic_coef
        
        # Clasificar tonicidad
        tonicity = self._classify_tonicity(osmolarity)
        
        # Predecir respuesta celular
        cell_response, volume_change = self._predict_cell_response(osmolarity)
        
        # Generar retroalimentación
        feedback = self._generate_feedback(
            osmolarity, tonicity, cell_response, solute_name or ""
        )
        
        # Generar interpretación
        interpretation = self._generate_interpretation(
            osmolarity, tonicity, cell_response
        )
        
        return OsmosisResult(
            success=True,
            inputs=inputs,
            osmolarity=round(osmolarity, 2),
            tonicity=tonicity,
            cell_response=cell_response,
            volume_change_percent=round(volume_change, 2),
            interpretation=interpretation,
            feedback=feedback,
        )
    
    def _classify_tonicity(self, osmolarity: float) -> str:
        """Clasifica la tonicidad respecto al plasma."""
        if osmolarity < self.PLASMA_RANGE[0]:
            return "hipotónica"
        elif osmolarity > self.PLASMA_RANGE[1]:
            return "hipertónica"
        else:
            return "isotónica"
    
    def _predict_cell_response(self, osmolarity: float) -> tuple[str, float]:
        """
        Predice la respuesta celular basándose en la osmolaridad.
        
        Aplica la ley de Boyle-van't Hoff simplificada.
        """
        # Cambio de volumen relativo (aproximado)
        volume_change = ((self.PLASMA_OSMOLARITY / osmolarity) - 1) * 100
        
        if volume_change > 10:
            response = "hinchazón severa (riesgo de lisis)"
        elif volume_change > 5:
            response = "hinchazón moderada"
        elif volume_change > 2:
            response = "hinchazón leve"
        elif volume_change < -10:
            response = "crenación severa"
        elif volume_change < -5:
            response = "crenación moderada"
        elif volume_change < -2:
            response = "crenación leve"
        else:
            response = "equilibrio (volumen estable)"
        
        return response, volume_change
    
    def _generate_feedback(
        self,
        osmolarity: float,
        tonicity: str,
        cell_response: str,
        solute_name: Optional[str] = None
    ) -> List[str]:
        """Genera puntos de retroalimentación educativa."""
        feedback = []
        
        # Información sobre la osmolaridad
        feedback.append(
            f"Osmolaridad calculada: {osmolarity:.1f} mOsm/L"
        )
        feedback.append(
            f"Osmolaridad del plasma: {self.PLASMA_OSMOLARITY} mOsm/L "
            f"(rango normal: {self.PLASMA_RANGE[0]}-{self.PLASMA_RANGE[1]})"
        )
        
        # Explicación de tonicidad
        if tonicity == "hipotónica":
            feedback.append(
                "Solución HIPOTÓNICA: menor concentración de solutos que el plasma. "
                "El agua entrará a la célula por ósmosis."
            )
        elif tonicity == "hipertónica":
            feedback.append(
                "Solución HIPERTÓNICA: mayor concentración de solutos que el plasma. "
                "El agua saldrá de la célula por ósmosis."
            )
        else:
            feedback.append(
                "Solución ISOTÓNICA: concentración similar al plasma. "
                "No hay movimiento neto de agua."
            )
        
        # Información sobre el soluto si está disponible
        if solute_name:
            if solute_name.lower() in ["nacl", "kcl", "cacl2"]:
                feedback.append(
                    f"Nota: {solute_name} es un electrolito que se disocia en iones, "
                    "aumentando el número de partículas osmóticamente activas."
                )
        
        return feedback
    
    def _generate_interpretation(
        self,
        osmolarity: float,
        tonicity: str,
        cell_response: str
    ) -> str:
        """Genera una interpretación narrativa del resultado."""
        diff = osmolarity - self.PLASMA_OSMOLARITY
        diff_percent = (diff / self.PLASMA_OSMOLARITY) * 100
        
        if tonicity == "isotónica":
            return (
                f"La solución tiene una osmolaridad de {osmolarity:.1f} mOsm/L, "
                f"que se encuentra dentro del rango fisiológico del plasma "
                f"({self.PLASMA_RANGE[0]}-{self.PLASMA_RANGE[1]} mOsm/L). "
                f"Las células mantendrán su volumen normal al estar en equilibrio osmótico."
            )
        elif tonicity == "hipotónica":
            return (
                f"La solución tiene una osmolaridad de {osmolarity:.1f} mOsm/L, "
                f"que es {abs(diff_percent):.1f}% menor que el plasma. "
                f"Esto generará un gradiente osmótico que provocará la entrada de agua "
                f"a las células, resultando en {cell_response}."
            )
        else:  # hipertónica
            return (
                f"La solución tiene una osmolaridad de {osmolarity:.1f} mOsm/L, "
                f"que es {diff_percent:.1f}% mayor que el plasma. "
                f"Esto generará un gradiente osmótico que provocará la salida de agua "
                f"de las células, resultando en {cell_response}."
            )
