"""
Servicio que coordina los diferentes solvers.
"""

from typing import Dict, Any, Optional
from ..solvers.osmosis import OsmolaritySolver, TonicityClassifier, CellVolumeSolver
from ..solvers.patch_clamp import NernstSolver, GoldmanHodgkinKatzSolver, IVCurveSolver
from ..domain.solver_result import OsmosisResult, PatchClampResult


class SolverService:
    """
    Servicio que proporciona acceso unificado a todos los solvers.
    
    Actúa como fachada para los diferentes módulos de cálculo,
    proporcionando una interfaz simple para la capa de presentación.
    """
    
    def __init__(self):
        # Inicializar solvers de ósmosis
        self.osmolarity_solver = OsmolaritySolver()
        self.tonicity_classifier = TonicityClassifier()
        self.cell_volume_solver = CellVolumeSolver()
        
        # Inicializar solvers de Patch Clamp
        self.nernst_solver = NernstSolver()
        self.ghk_solver = GoldmanHodgkinKatzSolver()
        self.iv_curve_solver = IVCurveSolver()
    
    # ==================== MÉTODOS DE ÓSMOSIS ====================
    
    def calculate_osmolarity(
        self,
        concentration_mM: float,
        dissociation_coef: Optional[int] = None,
        osmotic_coef: Optional[float] = None,
        solute_name: Optional[str] = None
    ) -> OsmosisResult:
        """
        Calcula la osmolaridad de una solución.
        
        Args:
            concentration_mM: Concentración en mM
            dissociation_coef: Coeficiente de disociación
            osmotic_coef: Coeficiente osmótico
            solute_name: Nombre del soluto (para autocompletar)
            
        Returns:
            OsmosisResult con osmolaridad y clasificación
        """
        return self.osmolarity_solver.solve(
            concentration_mM=concentration_mM,
            dissociation_coef=dissociation_coef,
            osmotic_coef=osmotic_coef,
            solute_name=solute_name
        )
    
    def calculate_cell_volume(
        self,
        final_osmolarity: float,
        initial_osmolarity: float = 285,
        initial_volume: float = 1.0,
        non_osmotic_fraction: float = 0.4
    ) -> OsmosisResult:
        """
        Calcula el cambio de volumen celular.
        
        Args:
            final_osmolarity: Osmolaridad del nuevo medio
            initial_osmolarity: Osmolaridad inicial
            initial_volume: Volumen inicial normalizado
            non_osmotic_fraction: Fracción no osmótica
            
        Returns:
            OsmosisResult con predicción de volumen
        """
        return self.cell_volume_solver.solve(
            final_osmolarity=final_osmolarity,
            initial_osmolarity=initial_osmolarity,
            initial_volume=initial_volume,
            non_osmotic_fraction=non_osmotic_fraction
        )
    
    def get_clinical_examples(self) -> Dict:
        """Obtiene ejemplos clínicos de soluciones."""
        return self.tonicity_classifier.get_clinical_examples()
    
    def get_boyle_vant_hoff_curve(
        self,
        osmolarity_range: tuple = (100, 600)
    ) -> Dict:
        """Genera datos para la curva de Boyle-van't Hoff."""
        return self.cell_volume_solver.calculate_boyle_vant_hoff_curve(
            osmolarity_range=osmolarity_range
        )
    
    # ==================== MÉTODOS DE PATCH CLAMP ====================
    
    def calculate_nernst(
        self,
        ion: str = "",
        z: int = 0,
        C_out: float = 0.0,
        C_in: float = 0.0,
        temperature_C: float = 37
    ) -> PatchClampResult:
        """
        Calcula el potencial de equilibrio de Nernst.
        
        Args:
            ion: Nombre del ion (K+, Na+, Cl-, Ca2+)
            z: Valencia del ion
            C_out: Concentración extracelular (mM)
            C_in: Concentración intracelular (mM)
            temperature_C: Temperatura (°C)
            
        Returns:
            PatchClampResult con potencial de equilibrio
        """
        return self.nernst_solver.solve(
            ion=ion,
            z=z,
            C_out=C_out,
            C_in=C_in,
            temperature_C=temperature_C
        )
    
    def calculate_nernst_all_ions(
        self,
        temperature_C: float = 37
    ) -> PatchClampResult:
        """Calcula potenciales de Nernst para todos los iones principales."""
        return self.nernst_solver.solve_multiple(temperature_C=temperature_C)
    
    def calculate_membrane_potential(
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
        temperature_C: float = 37
    ) -> PatchClampResult:
        """
        Calcula el potencial de membrana usando GHK.
        
        Returns:
            PatchClampResult con potencial de membrana
        """
        return self.ghk_solver.solve(
            P_K=P_K, P_Na=P_Na, P_Cl=P_Cl,
            K_out=K_out, K_in=K_in,
            Na_out=Na_out, Na_in=Na_in,
            Cl_out=Cl_out, Cl_in=Cl_in,
            temperature_C=temperature_C
        )
    
    def simulate_action_potential(
        self,
        temperature_C: float = 37
    ) -> Dict[str, PatchClampResult]:
        """Simula las fases del potencial de acción."""
        return self.ghk_solver.simulate_action_potential_phases(temperature_C)
    
    def generate_iv_curve(
        self,
        conductance: float = 10,
        reversal_potential: float = -80,
        voltage_range: tuple = (-120, 60)
    ) -> PatchClampResult:
        """
        Genera una curva I-V teórica.
        
        Args:
            conductance: Conductancia del canal (nS)
            reversal_potential: Potencial de reversión (mV)
            voltage_range: Rango de voltajes
            
        Returns:
            PatchClampResult con datos de curva I-V
        """
        return self.iv_curve_solver.solve(
            conductance=conductance,
            reversal_potential=reversal_potential,
            voltage_min=voltage_range[0],
            voltage_max=voltage_range[1]
        )
    
    def analyze_iv_data(
        self,
        voltages: list,
        currents: list
    ) -> PatchClampResult:
        """Analiza datos experimentales de curva I-V."""
        return self.iv_curve_solver.analyze_experimental_data(voltages, currents)
    
    # ==================== MÉTODOS DE INFORMACIÓN ====================
    
    def get_available_solvers(self) -> Dict[str, Dict]:
        """Retorna información sobre los solvers disponibles."""
        return {
            "osmosis": {
                "name": "Módulo de Ósmosis",
                "description": "Cálculos relacionados con ósmosis y tonicidad",
                "solvers": [
                    {
                        "id": "osmolarity",
                        "name": "Calculadora de Osmolaridad",
                        "description": self.osmolarity_solver.description,
                    },
                    {
                        "id": "cell_volume",
                        "name": "Volumen Celular",
                        "description": self.cell_volume_solver.description,
                    },
                ],
            },
            "patch_clamp": {
                "name": "Módulo de Patch Clamp",
                "description": "Cálculos electrofisiológicos",
                "solvers": [
                    {
                        "id": "nernst",
                        "name": "Ecuación de Nernst",
                        "description": self.nernst_solver.description,
                    },
                    {
                        "id": "ghk",
                        "name": "Ecuación de Goldman-Hodgkin-Katz",
                        "description": self.ghk_solver.description,
                    },
                    {
                        "id": "iv_curve",
                        "name": "Curvas I-V",
                        "description": self.iv_curve_solver.description,
                    },
                ],
            },
        }
    
    def get_solver_params(self, solver_id: str) -> Optional[Dict]:
        """Obtiene los parámetros requeridos por un solver."""
        solvers = {
            "osmolarity": self.osmolarity_solver,
            "cell_volume": self.cell_volume_solver,
            "nernst": self.nernst_solver,
            "ghk": self.ghk_solver,
            "iv_curve": self.iv_curve_solver,
        }
        
        if solver_id in solvers:
            return solvers[solver_id].get_required_params()
        return None
