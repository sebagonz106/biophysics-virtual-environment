"""
Solver para la ecuación de Nernst.
"""

from typing import Any, Dict, List, Optional
import numpy as np
from ..base_solver import BaseSolver
from ...domain.solver_result import PatchClampResult, NernstResult


class NernstSolver(BaseSolver):
    """
    Calcula el potencial de equilibrio de Nernst para iones.
    
    La ecuación de Nernst describe el potencial eléctrico de equilibrio
    para un ion específico a través de una membrana permeable solo a ese ion:
    
        E = (RT/zF) × ln([ion]_ext / [ion]_int)
        
    En forma simplificada a 37°C:
        E = (61.5/z) × log₁₀([ion]_ext / [ion]_int)  [en mV]
        
    Donde:
        - R: Constante de los gases (8.314 J/(mol·K))
        - T: Temperatura absoluta (K)
        - z: Valencia del ion
        - F: Constante de Faraday (96485 C/mol)
        - [ion]_ext: Concentración extracelular
        - [ion]_int: Concentración intracelular
    """
    
    name = "nernst_calculator"
    description = "Calcula el potencial de equilibrio de Nernst"
    
    # Constantes físicas
    R = 8.314       # J/(mol·K) - Constante de los gases
    F = 96485       # C/mol - Constante de Faraday
    
    # Concentraciones iónicas típicas (mM)
    TYPICAL_CONCENTRATIONS = {
        "K+": {"intracelular": 140, "extracelular": 5, "z": 1},
        "Na+": {"intracelular": 12, "extracelular": 145, "z": 1},
        "Cl-": {"intracelular": 4, "extracelular": 120, "z": -1},
        "Ca2+": {"intracelular": 0.0001, "extracelular": 2.5, "z": 2},
        "Mg2+": {"intracelular": 0.5, "extracelular": 1.5, "z": 2},
    }
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ion": {
                "type": str,
                "description": "Nombre del ion (ej: K+, Na+, Cl-, Ca2+)",
            },
            "z": {
                "type": int,
                "description": "Valencia del ion (carga). Positivo para cationes, negativo para aniones",
                "range": (-3, 3),
            },
            "C_out": {
                "type": float,
                "description": "Concentración extracelular (mM)",
                "unit": "mM",
                "range": (0.00001, 1000),
            },
            "C_in": {
                "type": float,
                "description": "Concentración intracelular (mM)",
                "unit": "mM",
                "range": (0.00001, 1000),
            },
            "temperature_C": {
                "type": float,
                "description": "Temperatura en grados Celsius",
                "unit": "°C",
                "default": 37,
                "range": (0, 50),
            },
        }
    
    def solve(
        self,
        ion: Optional[str] = None,
        z: Optional[int] = None,
        C_out: Optional[float] = None,
        C_in: Optional[float] = None,
        temperature_C: float = 37,
        **kwargs
    ) -> PatchClampResult:
        """
        Calcula el potencial de equilibrio de Nernst.
        
        Args:
            ion: Nombre del ion
            z: Valencia del ion
            C_out: Concentración extracelular (mM)
            C_in: Concentración intracelular (mM)
            temperature_C: Temperatura (°C)
            
        Returns:
            PatchClampResult con el potencial de equilibrio
        """
        # Autocompletar valores si se proporciona el nombre del ion
        if ion and ion in self.TYPICAL_CONCENTRATIONS:
            typical = self.TYPICAL_CONCENTRATIONS[ion]
            if z is None:
                z = typical["z"]
            if C_out is None:
                C_out = typical["extracelular"]
            if C_in is None:
                C_in = typical["intracelular"]
        
        inputs = {
            "ion": ion,
            "z": z,
            "C_out": C_out,
            "C_in": C_in,
            "temperature_C": temperature_C,
        }
        
        # Validaciones
        if z is None or z == 0:
            return PatchClampResult(
                success=False,
                error_message="La valencia (z) es requerida y no puede ser cero",
                inputs=inputs
            )
        
        if C_out is None or C_in is None:
            return PatchClampResult(
                success=False,
                error_message="Las concentraciones intra y extracelular son requeridas",
                inputs=inputs
            )
        
        if C_out <= 0 or C_in <= 0:
            return PatchClampResult(
                success=False,
                error_message="Las concentraciones deben ser mayores que cero",
                inputs=inputs
            )
        
        # Convertir temperatura a Kelvin
        T = temperature_C + 273.15
        
        # Calcular potencial de Nernst
        E_eq = (self.R * T) / (z * self.F) * np.log(C_out / C_in) * 1000  # en mV
        
        # Generar interpretación
        interpretation = self._generate_interpretation(ion or "", z, C_out, C_in, E_eq)
        
        # Crear resultado de Nernst
        nernst_result = NernstResult(
            ion=ion or f"Ion z={z}",
            z=z,
            E_eq=round(E_eq, 2),
            C_out=C_out,
            C_in=C_in,
            temperature_K=T,
            interpretation=interpretation
        )
        
        # Generar retroalimentación
        feedback = self._generate_feedback(ion or "", z, C_out, C_in, T, E_eq)
        
        return PatchClampResult(
            success=True,
            inputs=inputs,
            nernst_results=[nernst_result],
            interpretation=interpretation,
            feedback=feedback,
        )
    
    def solve_multiple(
        self,
        ions: Optional[List[str]] = None,
        temperature_C: float = 37
    ) -> PatchClampResult:
        """
        Calcula potenciales de Nernst para múltiples iones.
        
        Args:
            ions: Lista de iones a calcular. Si es None, calcula todos los típicos.
            temperature_C: Temperatura (°C)
            
        Returns:
            PatchClampResult con todos los potenciales calculados
        """
        if ions is None:
            ions = list(self.TYPICAL_CONCENTRATIONS.keys())
        
        T = temperature_C + 273.15
        nernst_results = []
        
        for ion in ions:
            if ion in self.TYPICAL_CONCENTRATIONS:
                data = self.TYPICAL_CONCENTRATIONS[ion]
                z = data["z"]
                C_out = data["extracelular"]
                C_in = data["intracelular"]
                
                E_eq = (self.R * T) / (z * self.F) * np.log(C_out / C_in) * 1000
                
                nernst_results.append(NernstResult(
                    ion=ion,
                    z=z,
                    E_eq=round(E_eq, 2),
                    C_out=C_out,
                    C_in=C_in,
                    temperature_K=T,
                    interpretation=self._generate_interpretation(ion, z, E_eq, C_out, C_in)
                ))
        
        # Generar retroalimentación comparativa
        feedback = [
            "Potenciales de equilibrio calculados para condiciones fisiológicas típicas:",
            f"Temperatura: {temperature_C}°C ({T:.1f} K)",
            "",
        ]
        
        for nr in nernst_results:
            feedback.append(f"E_{nr.ion} = {nr.E_eq:+.1f} mV")
        
        feedback.append("")
        feedback.append(
            "El potencial de reposo (~-70 mV) está más cerca del E_K+ "
            "porque la membrana en reposo es más permeable al K+."
        )
        
        return PatchClampResult(
            success=True,
            inputs={"ions": ions, "temperature_C": temperature_C},
            nernst_results=nernst_results,
            interpretation="Comparación de potenciales de equilibrio iónicos",
            feedback=feedback,
        )
    
    def _generate_interpretation(
        self,
        ion: str,
        z: int,
        C_out: float,
        C_in: float,
        E_eq: float
    ) -> str:
        """Genera interpretación del resultado."""
        ion_name = ion or f"ion (z={z})"
        
        # Determinar dirección del gradiente
        if C_out > C_in:
            gradient_dir = "hacia el interior"
        else:
            gradient_dir = "hacia el exterior"
        
        # Comparar con potencial de reposo típico
        V_rest = -70  # mV aproximado
        
        if z > 0:  # Catión
            if E_eq < V_rest:
                driving = "salir de la célula"
            else:
                driving = "entrar a la célula"
        else:  # Anión
            if E_eq > V_rest:
                driving = "salir de la célula"
            else:
                driving = "entrar a la célula"
        
        interpretation = (
            f"El potencial de equilibrio para {ion_name} es {E_eq:+.1f} mV. "
            f"El gradiente de concentración favorece el movimiento {gradient_dir}. "
            f"Al potencial de reposo (≈{V_rest} mV), este ion tendería a {driving}."
        )
        
        return interpretation
    
    def _generate_feedback(
        self,
        ion: str,
        z: int,
        C_out: float,
        C_in: float,
        T: float,
        E_eq: float
    ) -> List[str]:
        """Genera retroalimentación educativa."""
        feedback = []
        
        # Fórmula utilizada
        feedback.append(
            f"Ecuación de Nernst: E = (RT/zF) × ln([ion]_ext/[ion]_int)"
        )
        
        # Valores utilizados
        feedback.append(
            f"Parámetros: z = {z}, [ext] = {C_out} mM, [int] = {C_in} mM, T = {T:.1f} K"
        )
        
        # Razón de concentraciones
        ratio = C_out / C_in
        feedback.append(
            f"Razón de concentraciones: {C_out}/{C_in} = {ratio:.4f}"
        )
        
        # Factor RT/zF a esta temperatura
        factor = (self.R * T) / (abs(z) * self.F) * 1000
        feedback.append(
            f"Factor RT/|z|F a {T-273.15:.0f}°C: {factor:.2f} mV"
        )
        
        # Resultado
        feedback.append(
            f"Potencial de equilibrio: E = {E_eq:+.2f} mV"
        )
        
        return feedback
