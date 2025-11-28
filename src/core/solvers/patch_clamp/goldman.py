"""
Solver para la ecuación de Goldman-Hodgkin-Katz.
"""

from typing import Any, Dict, List
import numpy as np
from ..base_solver import BaseSolver
from ...domain.solver_result import PatchClampResult, GHKResult


class GoldmanHodgkinKatzSolver(BaseSolver):
    """
    Calcula el potencial de membrana usando la ecuación de Goldman-Hodgkin-Katz (GHK).
    
    La ecuación GHK considera la permeabilidad relativa de múltiples iones:
    
        Vm = (RT/F) × ln[(P_K[K+]_e + P_Na[Na+]_e + P_Cl[Cl-]_i) / 
                         (P_K[K+]_i + P_Na[Na+]_i + P_Cl[Cl-]_e)]
    
    Esta ecuación es más realista que Nernst porque considera que la membrana
    es permeable a múltiples iones simultáneamente.
    
    Donde:
        - P_x: Permeabilidad relativa del ion x
        - [x]_e: Concentración extracelular
        - [x]_i: Concentración intracelular
    """
    
    name = "ghk_calculator"
    description = "Calcula el potencial de membrana (ecuación de Goldman)"
    
    # Constantes físicas
    R = 8.314       # J/(mol·K)
    F = 96485       # C/mol
    
    # Permeabilidades relativas típicas en reposo
    DEFAULT_PERMEABILITIES = {
        "K+": 1.0,      # Referencia
        "Na+": 0.04,    # ~4% de la permeabilidad del K+
        "Cl-": 0.45,    # ~45% de la permeabilidad del K+
    }
    
    # Concentraciones típicas (mM)
    DEFAULT_CONCENTRATIONS = {
        "K+": {"intracelular": 140, "extracelular": 5},
        "Na+": {"intracelular": 12, "extracelular": 145},
        "Cl-": {"intracelular": 4, "extracelular": 120},
    }
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "P_K": {
                "type": float,
                "description": "Permeabilidad relativa al K+ (referencia = 1.0)",
                "default": 1.0,
                "range": (0, 100),
            },
            "P_Na": {
                "type": float,
                "description": "Permeabilidad relativa al Na+",
                "default": 0.04,
                "range": (0, 100),
            },
            "P_Cl": {
                "type": float,
                "description": "Permeabilidad relativa al Cl-",
                "default": 0.45,
                "range": (0, 100),
            },
            "K_out": {
                "type": float,
                "description": "Concentración extracelular de K+ (mM)",
                "default": 5,
                "unit": "mM",
            },
            "K_in": {
                "type": float,
                "description": "Concentración intracelular de K+ (mM)",
                "default": 140,
                "unit": "mM",
            },
            "Na_out": {
                "type": float,
                "description": "Concentración extracelular de Na+ (mM)",
                "default": 145,
                "unit": "mM",
            },
            "Na_in": {
                "type": float,
                "description": "Concentración intracelular de Na+ (mM)",
                "default": 12,
                "unit": "mM",
            },
            "Cl_out": {
                "type": float,
                "description": "Concentración extracelular de Cl- (mM)",
                "default": 120,
                "unit": "mM",
            },
            "Cl_in": {
                "type": float,
                "description": "Concentración intracelular de Cl- (mM)",
                "default": 4,
                "unit": "mM",
            },
            "temperature_C": {
                "type": float,
                "description": "Temperatura (°C)",
                "default": 37,
            },
        }
    
    def solve(
        self,
        P_K: float = 1.0,
        P_Na: float = 0.04,
        P_Cl: float = 0.45,
        K_out: float = 5,
        K_in: float = 140,
        Na_out: float = 145,
        Na_in: float = 12,
        Cl_out: float = 120,
        Cl_in: float = 4,
        temperature_C: float = 37,
        **kwargs
    ) -> PatchClampResult:
        """
        Calcula el potencial de membrana usando la ecuación GHK.
        
        Returns:
            PatchClampResult con el potencial de membrana calculado
        """
        inputs = {
            "permeabilities": {"K+": P_K, "Na+": P_Na, "Cl-": P_Cl},
            "concentrations": {
                "K+": {"in": K_in, "out": K_out},
                "Na+": {"in": Na_in, "out": Na_out},
                "Cl-": {"in": Cl_in, "out": Cl_out},
            },
            "temperature_C": temperature_C,
        }
        
        # Convertir temperatura a Kelvin
        T = temperature_C + 273.15
        
        # Calcular numerador y denominador de la ecuación GHK
        # Nota: Para Cl- (anión), las concentraciones se invierten
        numerator = (P_K * K_out) + (P_Na * Na_out) + (P_Cl * Cl_in)
        denominator = (P_K * K_in) + (P_Na * Na_in) + (P_Cl * Cl_out)
        
        if denominator <= 0 or numerator <= 0:
            return PatchClampResult(
                success=False,
                error_message="Los valores resultantes no permiten calcular el logaritmo",
                inputs=inputs
            )
        
        # Calcular potencial de membrana
        Vm = (self.R * T / self.F) * np.log(numerator / denominator) * 1000  # en mV
        
        # Determinar ion dominante
        contributions: Dict[str, float] = {
            "K+": P_K * (K_out + K_in),
            "Na+": P_Na * (Na_out + Na_in),
            "Cl-": P_Cl * (Cl_out + Cl_in),
        }
        dominant_ion = max(contributions, key=lambda k: contributions[k])
        
        # Generar interpretación
        interpretation = self._generate_interpretation(
            Vm, P_K, P_Na, P_Cl, dominant_ion
        )
        
        # Crear resultado GHK
        ghk_result = GHKResult(
            membrane_potential=round(Vm, 2),
            permeabilities={"K+": P_K, "Na+": P_Na, "Cl-": P_Cl},
            concentrations={
                "K+": {"intracelular": K_in, "extracelular": K_out},
                "Na+": {"intracelular": Na_in, "extracelular": Na_out},
                "Cl-": {"intracelular": Cl_in, "extracelular": Cl_out},
            },
            dominant_ion=dominant_ion,
            interpretation=interpretation,
        )
        
        # Generar retroalimentación
        feedback = self._generate_feedback(
            Vm, P_K, P_Na, P_Cl,
            K_out, K_in, Na_out, Na_in, Cl_out, Cl_in,
            T, dominant_ion
        )
        
        return PatchClampResult(
            success=True,
            inputs=inputs,
            ghk_result=ghk_result,
            interpretation=interpretation,
            feedback=feedback,
        )
    
    def simulate_action_potential_phases(
        self,
        temperature_C: float = 37
    ) -> Dict[str, PatchClampResult]:
        """
        Simula las diferentes fases del potencial de acción
        mostrando cómo cambian las permeabilidades.
        """
        phases = {
            "reposo": {"P_K": 1.0, "P_Na": 0.04, "P_Cl": 0.45},
            "despolarizacion": {"P_K": 1.0, "P_Na": 20.0, "P_Cl": 0.45},
            "repolarizacion": {"P_K": 5.0, "P_Na": 0.04, "P_Cl": 0.45},
            "hiperpolarizacion": {"P_K": 3.0, "P_Na": 0.04, "P_Cl": 0.45},
        }
        
        results = {}
        for phase_name, perms in phases.items():
            results[phase_name] = self.solve(
                P_K=perms["P_K"],
                P_Na=perms["P_Na"],
                P_Cl=perms["P_Cl"],
                temperature_C=temperature_C
            )
        
        return results
    
    def _generate_interpretation(
        self,
        Vm: float,
        P_K: float,
        P_Na: float,
        P_Cl: float,
        dominant_ion: str
    ) -> str:
        """Genera interpretación del resultado."""
        interpretation = (
            f"El potencial de membrana calculado es {Vm:+.1f} mV. "
        )
        
        # Comparar con valores típicos
        if -80 <= Vm <= -60:
            interpretation += (
                "Este valor está dentro del rango típico del potencial de reposo "
                "(-60 a -80 mV). "
            )
        elif Vm > 0:
            interpretation += (
                "Este valor positivo es típico de la fase de despolarización "
                "del potencial de acción. "
            )
        elif Vm < -80:
            interpretation += (
                "Este valor muy negativo sugiere una fase de hiperpolarización. "
            )
        
        interpretation += f"El ion dominante es {dominant_ion}."
        
        # Explicar efecto de las permeabilidades
        if P_Na > P_K:
            interpretation += (
                " La alta permeabilidad al Na+ desplaza el potencial hacia valores positivos."
            )
        elif P_K > 2:
            interpretation += (
                " La alta permeabilidad al K+ mantiene el potencial negativo."
            )
        
        return interpretation
    
    def _generate_feedback(
        self,
        Vm: float,
        P_K: float, P_Na: float, P_Cl: float,
        K_out: float, K_in: float,
        Na_out: float, Na_in: float,
        Cl_out: float, Cl_in: float,
        T: float,
        dominant_ion: str
    ) -> List[str]:
        """Genera retroalimentación educativa."""
        feedback = []
        
        feedback.append(
            "Ecuación de Goldman-Hodgkin-Katz para el potencial de membrana:"
        )
        feedback.append(
            "Vm = (RT/F) × ln[(P_K[K]_e + P_Na[Na]_e + P_Cl[Cl]_i) / "
            "(P_K[K]_i + P_Na[Na]_i + P_Cl[Cl]_e)]"
        )
        
        feedback.append("")
        feedback.append("Permeabilidades relativas utilizadas:")
        feedback.append(f"  P_K = {P_K:.2f}, P_Na = {P_Na:.2f}, P_Cl = {P_Cl:.2f}")
        
        feedback.append("")
        feedback.append("Concentraciones (mM):")
        feedback.append(f"  K+:  [ext]={K_out}, [int]={K_in}")
        feedback.append(f"  Na+: [ext]={Na_out}, [int]={Na_in}")
        feedback.append(f"  Cl-: [ext]={Cl_out}, [int]={Cl_in}")
        
        feedback.append("")
        feedback.append(f"Potencial de membrana resultante: Vm = {Vm:+.2f} mV")
        feedback.append(f"Ion con mayor influencia: {dominant_ion}")
        
        # Comparación con potenciales de Nernst
        E_K = (self.R * T / self.F) * np.log(K_out / K_in) * 1000
        E_Na = (self.R * T / self.F) * np.log(Na_out / Na_in) * 1000
        
        feedback.append("")
        feedback.append("Comparación con potenciales de Nernst:")
        feedback.append(f"  E_K = {E_K:+.1f} mV")
        feedback.append(f"  E_Na = {E_Na:+.1f} mV")
        feedback.append(f"  Vm está entre E_K y E_Na, más cerca de E_K en reposo")
        
        return feedback
