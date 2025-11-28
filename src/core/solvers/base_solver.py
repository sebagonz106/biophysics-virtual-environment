"""
Clase base abstracta para todos los Solvers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
from ..domain.solver_result import SolverResult


class BaseSolver(ABC):
    """
    Clase base abstracta para todos los solvers del sistema.
    
    Cada solver debe implementar el método `solve` que recibe
    los parámetros de entrada y retorna un resultado estructurado.
    """
    
    name: str = "base_solver"
    description: str = "Solver base"
    
    @abstractmethod
    def solve(self, **kwargs) -> SolverResult:
        """
        Ejecuta el cálculo del solver.
        
        Args:
            **kwargs: Parámetros específicos del solver
            
        Returns:
            SolverResult: Resultado estructurado del cálculo
        """
        pass
    
    @abstractmethod
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        """
        Retorna los parámetros requeridos por el solver.
        
        Returns:
            Dict con nombre del parámetro y sus propiedades:
            - type: Tipo de dato esperado
            - description: Descripción del parámetro
            - unit: Unidad de medida (opcional)
            - default: Valor por defecto (opcional)
            - range: Rango válido (opcional)
        """
        pass
    
    def validate_params(self, **kwargs) -> tuple[bool, str]:
        """
        Valida los parámetros de entrada.
        
        Returns:
            Tupla (es_válido, mensaje_error)
        """
        required = self.get_required_params()
        
        for param_name, param_info in required.items():
            if param_name not in kwargs:
                if "default" not in param_info:
                    return False, f"Parámetro requerido faltante: {param_name}"
            else:
                value = kwargs[param_name]
                
                # Validar rango si está definido
                if "range" in param_info:
                    min_val, max_val = param_info["range"]
                    if not (min_val <= value <= max_val):
                        return False, f"{param_name} debe estar entre {min_val} y {max_val}"
        
        return True, ""
