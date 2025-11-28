"""
Solver para cálculos de volumen celular.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from ..base_solver import BaseSolver
from ...domain.solver_result import OsmosisResult


class CellVolumeSolver(BaseSolver):
    """
    Calcula y predice cambios en el volumen celular por ósmosis.
    
    Utiliza la ley de Boyle-van't Hoff:
        V₁ × π₁ = V₂ × π₂
        
    Donde:
        - V: Volumen celular
        - π: Presión osmótica (proporcional a la osmolaridad)
    
    Esta ecuación permite predecir el volumen final de una célula
    cuando se expone a una solución de diferente osmolaridad.
    """
    
    name = "cell_volume_calculator"
    description = "Calcula cambios en el volumen celular por ósmosis"
    
    # Osmolaridad de referencia del plasma
    PLASMA_OSMOLARITY = 285  # mOsm/L
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "initial_osmolarity": {
                "type": float,
                "description": "Osmolaridad inicial del medio (mOsm/L)",
                "unit": "mOsm/L",
                "default": 285,
                "range": (1, 2000),
            },
            "final_osmolarity": {
                "type": float,
                "description": "Osmolaridad final del medio (mOsm/L)",
                "unit": "mOsm/L",
                "range": (1, 2000),
            },
            "initial_volume": {
                "type": float,
                "description": "Volumen celular inicial (unidades relativas o µm³)",
                "unit": "relativo",
                "default": 1.0,
                "range": (0.01, 1000),
            },
            "non_osmotic_fraction": {
                "type": float,
                "description": "Fracción no osmótica del volumen celular (b). Típicamente 0.3-0.4",
                "default": 0.4,
                "range": (0, 0.9),
            },
        }
    
    def solve(
        self,
        final_osmolarity: float,
        initial_osmolarity: float = 285,
        initial_volume: float = 1.0,
        non_osmotic_fraction: float = 0.4,
        **kwargs
    ) -> OsmosisResult:
        """
        Calcula el volumen celular final.
        
        Args:
            initial_osmolarity: Osmolaridad inicial (mOsm/L)
            final_osmolarity: Osmolaridad final (mOsm/L)
            initial_volume: Volumen inicial (normalizado a 1)
            non_osmotic_fraction: Fracción no osmótica (b)
            
        Returns:
            OsmosisResult con el volumen final y datos para gráfico
        """
        inputs = {
            "initial_osmolarity": initial_osmolarity,
            "final_osmolarity": final_osmolarity,
            "initial_volume": initial_volume,
            "non_osmotic_fraction": non_osmotic_fraction,
        }
        
        # Validaciones
        if final_osmolarity <= 0:
            return OsmosisResult(
                success=False,
                error_message="La osmolaridad final debe ser mayor que cero",
                inputs=inputs
            )
        
        # Calcular volumen final usando Boyle-van't Hoff modificada
        # V = b + (1-b) × (π_inicial / π_final)
        b = non_osmotic_fraction
        osmotic_volume_initial = initial_volume * (1 - b)
        
        final_volume = (b * initial_volume) + (
            osmotic_volume_initial * (initial_osmolarity / final_osmolarity)
        )
        
        # Calcular cambio porcentual
        volume_change_percent = ((final_volume / initial_volume) - 1) * 100
        
        # Clasificar tonicidad y respuesta celular
        tonicity = self._classify_tonicity(final_osmolarity)
        cell_response = self._predict_cell_response(volume_change_percent)
        
        # Generar datos para gráfico temporal
        volume_data = self._generate_volume_curve(
            initial_volume, final_volume, time_points=50
        )
        
        # Generar retroalimentación
        feedback = self._generate_feedback(
            initial_osmolarity, final_osmolarity,
            initial_volume, final_volume,
            volume_change_percent, cell_response
        )
        
        interpretation = self._generate_interpretation(
            initial_osmolarity, final_osmolarity,
            volume_change_percent, cell_response
        )
        
        return OsmosisResult(
            success=True,
            inputs=inputs,
            osmolarity=final_osmolarity,
            tonicity=tonicity,
            cell_response=cell_response,
            volume_change_percent=round(volume_change_percent, 2),
            volume_data=volume_data,
            interpretation=interpretation,
            feedback=feedback,
        )
    
    def calculate_boyle_vant_hoff_curve(
        self,
        osmolarity_range: Tuple[float, float] = (100, 600),
        initial_osmolarity: float = 285,
        non_osmotic_fraction: float = 0.4,
        num_points: int = 100
    ) -> Dict[str, List[float]]:
        """
        Genera la curva de Boyle-van't Hoff completa.
        
        Útil para visualizar la relación entre osmolaridad y volumen.
        """
        osmolarities = np.linspace(osmolarity_range[0], osmolarity_range[1], num_points)
        
        b = non_osmotic_fraction
        volumes = []
        
        for osm in osmolarities:
            v = b + (1 - b) * (initial_osmolarity / osm)
            volumes.append(v)
        
        return {
            "osmolarity": osmolarities.tolist(),
            "relative_volume": volumes,
        }
    
    def _classify_tonicity(self, osmolarity: float) -> str:
        """Clasifica la tonicidad de la solución."""
        if osmolarity < 275:
            return "hipotónica"
        elif osmolarity > 295:
            return "hipertónica"
        return "isotónica"
    
    def _predict_cell_response(self, volume_change_percent: float) -> str:
        """Predice la respuesta celular según el cambio de volumen."""
        if volume_change_percent > 50:
            return "lisis celular"
        elif volume_change_percent > 20:
            return "hinchazón severa"
        elif volume_change_percent > 5:
            return "hinchazón moderada"
        elif volume_change_percent < -30:
            return "crenación severa"
        elif volume_change_percent < -15:
            return "crenación moderada"
        elif volume_change_percent < -5:
            return "crenación leve"
        else:
            return "equilibrio"
    
    def _generate_volume_curve(
        self,
        v_initial: float,
        v_final: float,
        time_points: int = 50
    ) -> Dict[str, List[float]]:
        """
        Genera una curva de cambio de volumen en el tiempo.
        
        Usa un modelo exponencial para simular la cinética osmótica.
        """
        # Constante de tiempo (arbitraria para visualización)
        tau = 10  # unidades de tiempo
        
        t = np.linspace(0, 5 * tau, time_points)
        
        # Modelo exponencial: V(t) = V_final + (V_initial - V_final) * exp(-t/tau)
        v_t = v_final + (v_initial - v_final) * np.exp(-t / tau)
        
        return {
            "time": t.tolist(),
            "volume": v_t.tolist(),
        }
    
    def _generate_feedback(
        self,
        osm_initial: float,
        osm_final: float,
        v_initial: float,
        v_final: float,
        change_percent: float,
        cell_response: str
    ) -> List[str]:
        """Genera retroalimentación educativa."""
        feedback = []
        
        feedback.append(
            f"Cambio de osmolaridad: {osm_initial:.0f} → {osm_final:.0f} mOsm/L"
        )
        
        feedback.append(
            f"Cambio de volumen: {v_initial:.3f} → {v_final:.3f} "
            f"({change_percent:+.1f}%)"
        )
        
        if osm_final < osm_initial:
            feedback.append(
                "El medio es hipotónico → entrada de agua → aumento de volumen"
            )
        elif osm_final > osm_initial:
            feedback.append(
                "El medio es hipertónico → salida de agua → disminución de volumen"
            )
        else:
            feedback.append(
                "El medio es isotónico → sin movimiento neto de agua"
            )
        
        # Advertencias clínicas
        if "lisis" in cell_response.lower():
            feedback.append(
                "⚠️ ADVERTENCIA: Riesgo de lisis celular. "
                "Esto puede ocurrir con soluciones muy hipotónicas."
            )
        elif "severa" in cell_response.lower():
            feedback.append(
                "⚠️ Cambio de volumen significativo que puede afectar la función celular."
            )
        
        return feedback
    
    def _generate_interpretation(
        self,
        osm_initial: float,
        osm_final: float,
        change_percent: float,
        cell_response: str
    ) -> str:
        """Genera interpretación narrativa."""
        direction = "aumentará" if change_percent > 0 else "disminuirá"
        if abs(change_percent) < 2:
            direction = "se mantendrá prácticamente estable"
        
        return (
            f"Al pasar de un medio con osmolaridad {osm_initial:.0f} mOsm/L "
            f"a uno de {osm_final:.0f} mOsm/L, el volumen celular {direction}. "
            f"Se espera un cambio de {abs(change_percent):.1f}% en el volumen, "
            f"resultando en {cell_response}."
        )
