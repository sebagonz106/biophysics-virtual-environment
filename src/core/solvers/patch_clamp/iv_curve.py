"""
Solver para generación de curvas I-V (Corriente-Voltaje).
"""

from typing import Any, Dict, List, Tuple
import numpy as np
from ..base_solver import BaseSolver
from ...domain.solver_result import PatchClampResult, IVCurveData


class IVCurveSolver(BaseSolver):
    """
    Genera y analiza curvas de corriente-voltaje (I-V) para canales iónicos.
    
    La relación I-V describe cómo la corriente a través de un canal
    varía con el potencial de membrana. Para un canal óhmico:
    
        I = g × (V - E_rev)
        
    Donde:
        - I: Corriente (pA o nA)
        - g: Conductancia del canal (nS)
        - V: Potencial de membrana (mV)
        - E_rev: Potencial de reversión (mV)
    
    El potencial de reversión es el voltaje donde la corriente es cero,
    y corresponde al potencial de equilibrio de Nernst para el ion.
    """
    
    name = "iv_curve_generator"
    description = "Genera curvas de corriente-voltaje para canales iónicos"
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "conductance": {
                "type": float,
                "description": "Conductancia del canal (nS)",
                "unit": "nS",
                "default": 10,
                "range": (0.1, 1000),
            },
            "reversal_potential": {
                "type": float,
                "description": "Potencial de reversión/equilibrio (mV)",
                "unit": "mV",
                "default": -80,
                "range": (-150, 100),
            },
            "voltage_min": {
                "type": float,
                "description": "Voltaje mínimo para la curva (mV)",
                "unit": "mV",
                "default": -120,
            },
            "voltage_max": {
                "type": float,
                "description": "Voltaje máximo para la curva (mV)",
                "unit": "mV",
                "default": 60,
            },
            "num_points": {
                "type": int,
                "description": "Número de puntos en la curva",
                "default": 50,
                "range": (10, 200),
            },
        }
    
    def solve(
        self,
        conductance: float = 10,
        reversal_potential: float = -80,
        voltage_min: float = -120,
        voltage_max: float = 60,
        num_points: int = 50,
        **kwargs
    ) -> PatchClampResult:
        """
        Genera una curva I-V teórica.
        
        Returns:
            PatchClampResult con los datos de la curva I-V
        """
        inputs = {
            "conductance": conductance,
            "reversal_potential": reversal_potential,
            "voltage_range": (voltage_min, voltage_max),
            "num_points": num_points,
        }
        
        # Generar valores de voltaje
        voltages = np.linspace(voltage_min, voltage_max, num_points)
        
        # Calcular corrientes (ley de Ohm)
        currents = conductance * (voltages - reversal_potential)  # en pA si g en nS
        
        # Crear datos de curva I-V
        iv_data = IVCurveData(
            voltage=voltages.tolist(),
            current=currents.tolist(),
            reversal_potential=reversal_potential,
            conductance=conductance,
        )
        
        # Generar interpretación
        interpretation = self._generate_interpretation(
            conductance, reversal_potential
        )
        
        # Generar retroalimentación
        feedback = self._generate_feedback(
            conductance, reversal_potential, voltages, currents
        )
        
        return PatchClampResult(
            success=True,
            inputs=inputs,
            iv_curve=iv_data,
            interpretation=interpretation,
            feedback=feedback,
        )
    
    def analyze_experimental_data(
        self,
        voltages: List[float],
        currents: List[float]
    ) -> PatchClampResult:
        """
        Analiza datos experimentales de una curva I-V.
        
        Realiza una regresión lineal para determinar:
        - Conductancia (pendiente)
        - Potencial de reversión (intersección con eje X)
        
        Args:
            voltages: Lista de voltajes aplicados (mV)
            currents: Lista de corrientes medidas (pA)
            
        Returns:
            PatchClampResult con el análisis
        """
        inputs = {
            "voltages": voltages,
            "currents": currents,
            "n_points": len(voltages),
        }
        
        if len(voltages) != len(currents):
            return PatchClampResult(
                success=False,
                error_message="Las listas de voltajes y corrientes deben tener la misma longitud",
                inputs=inputs
            )
        
        if len(voltages) < 2:
            return PatchClampResult(
                success=False,
                error_message="Se necesitan al menos 2 puntos para el análisis",
                inputs=inputs
            )
        
        # Convertir a arrays
        V = np.array(voltages)
        I = np.array(currents)
        
        # Regresión lineal: I = g*V - g*E_rev
        # y = mx + b, donde m = g, b = -g*E_rev
        coeffs = np.polyfit(V, I, 1)
        g = coeffs[0]  # Conductancia (pendiente)
        
        if abs(g) < 1e-10:
            return PatchClampResult(
                success=False,
                error_message="La conductancia calculada es prácticamente cero",
                inputs=inputs
            )
        
        E_rev = -coeffs[1] / g  # Potencial de reversión
        
        # Calcular R² (coeficiente de determinación)
        I_pred = g * V + coeffs[1]
        ss_res = np.sum((I - I_pred) ** 2)
        ss_tot = np.sum((I - np.mean(I)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        # Crear datos de curva I-V
        iv_data = IVCurveData(
            voltage=voltages,
            current=currents,
            reversal_potential=round(E_rev, 2),
            conductance=round(g, 4),
        )
        
        interpretation = (
            f"Análisis de curva I-V experimental:\n"
            f"- Conductancia: {g:.2f} nS\n"
            f"- Potencial de reversión: {E_rev:.1f} mV\n"
            f"- R² = {r_squared:.4f} (ajuste lineal)"
        )
        
        feedback = [
            f"Se analizaron {len(voltages)} puntos experimentales",
            f"Conductancia calculada: g = {g:.2f} nS",
            f"Potencial de reversión: E_rev = {E_rev:.1f} mV",
            f"Coeficiente de determinación: R² = {r_squared:.4f}",
        ]
        
        if r_squared > 0.99:
            feedback.append("✓ Excelente ajuste lineal - comportamiento óhmico")
        elif r_squared > 0.95:
            feedback.append("✓ Buen ajuste lineal")
        elif r_squared > 0.9:
            feedback.append("⚠ Ajuste moderado - posible rectificación")
        else:
            feedback.append("⚠ Ajuste pobre - el canal puede no ser óhmico")
        
        return PatchClampResult(
            success=True,
            inputs=inputs,
            iv_curve=iv_data,
            interpretation=interpretation,
            feedback=feedback,
        )
    
    def generate_rectifying_channel(
        self,
        conductance: float = 10,
        reversal_potential: float = -80,
        rectification_type: str = "inward",
        voltage_range: Tuple[float, float] = (-120, 60),
        num_points: int = 50
    ) -> PatchClampResult:
        """
        Genera una curva I-V para un canal rectificador.
        
        Los canales rectificadores permiten el paso de corriente
        preferentemente en una dirección.
        
        Args:
            rectification_type: "inward" o "outward"
        """
        V = np.linspace(voltage_range[0], voltage_range[1], num_points)
        
        # Modelo simplificado de rectificación
        if rectification_type == "inward":
            # Mayor conductancia para V < E_rev (corriente entrante)
            g_effective = conductance * (1 + 0.5 * np.tanh(-(V - reversal_potential) / 20))
        else:  # outward
            # Mayor conductancia para V > E_rev (corriente saliente)
            g_effective = conductance * (1 + 0.5 * np.tanh((V - reversal_potential) / 20))
        
        I = g_effective * (V - reversal_potential)
        
        iv_data = IVCurveData(
            voltage=V.tolist(),
            current=I.tolist(),
            reversal_potential=reversal_potential,
            conductance=conductance,
        )
        
        interpretation = (
            f"Curva I-V para canal rectificador {rectification_type}. "
            f"La conductancia varía con el voltaje, siendo mayor para "
            f"{'voltajes negativos' if rectification_type == 'inward' else 'voltajes positivos'}."
        )
        
        return PatchClampResult(
            success=True,
            inputs={
                "conductance": conductance,
                "reversal_potential": reversal_potential,
                "rectification_type": rectification_type,
            },
            iv_curve=iv_data,
            interpretation=interpretation,
            feedback=[
                f"Tipo de rectificación: {rectification_type}",
                f"Conductancia base: {conductance} nS",
                f"Potencial de reversión: {reversal_potential} mV",
            ],
        )
    
    def _generate_interpretation(
        self,
        conductance: float,
        reversal_potential: float
    ) -> str:
        """Genera interpretación del resultado."""
        interpretation = (
            f"Curva I-V teórica para un canal con conductancia g = {conductance} nS "
            f"y potencial de reversión E_rev = {reversal_potential} mV.\n\n"
        )
        
        # Identificar el tipo de canal probable
        if -95 <= reversal_potential <= -75:
            interpretation += (
                "El potencial de reversión sugiere un canal selectivo para K+. "
            )
        elif 50 <= reversal_potential <= 70:
            interpretation += (
                "El potencial de reversión sugiere un canal selectivo para Na+. "
            )
        elif -20 <= reversal_potential <= 20:
            interpretation += (
                "El potencial de reversión cercano a 0 mV sugiere un canal "
                "no selectivo para cationes. "
            )
        elif -80 <= reversal_potential <= -60:
            interpretation += (
                "El potencial de reversión sugiere un canal selectivo para Cl-. "
            )
        
        interpretation += (
            f"\nLa corriente es cero a V = {reversal_potential} mV, "
            "positiva (saliente) para V > E_rev, y negativa (entrante) para V < E_rev."
        )
        
        return interpretation
    
    def _generate_feedback(
        self,
        conductance: float,
        reversal_potential: float,
        voltages: np.ndarray,
        currents: np.ndarray
    ) -> List[str]:
        """Genera retroalimentación educativa."""
        feedback = []
        
        feedback.append("Relación corriente-voltaje (Ley de Ohm para canales):")
        feedback.append("I = g × (V - E_rev)")
        
        feedback.append("")
        feedback.append(f"Parámetros del canal:")
        feedback.append(f"  Conductancia (g): {conductance} nS")
        feedback.append(f"  Potencial de reversión (E_rev): {reversal_potential} mV")
        
        feedback.append("")
        feedback.append("Puntos clave de la curva:")
        feedback.append(f"  En V = E_rev = {reversal_potential} mV: I = 0 pA")
        
        # Encontrar corriente a potencial de reposo típico (-70 mV)
        v_rest = -70
        i_rest = conductance * (v_rest - reversal_potential)
        feedback.append(f"  En V = -70 mV (reposo): I = {i_rest:.1f} pA")
        
        # Encontrar corriente a 0 mV
        i_zero = conductance * (0 - reversal_potential)
        feedback.append(f"  En V = 0 mV: I = {i_zero:.1f} pA")
        
        feedback.append("")
        feedback.append(
            "La pendiente de la recta es igual a la conductancia (g = ΔI/ΔV)"
        )
        
        return feedback
