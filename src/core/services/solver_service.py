"""
Servicio que coordina los diferentes solvers.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from ..solvers.osmosis import OsmolaritySolver, OsmolarityComparisonSolver, TonicityClassifier, CellVolumeSolver
from ..solvers.patch_clamp import NernstSolver, GoldmanHodgkinKatzSolver, IVCurveSolver, SingleChannelSolver
from ..solvers.patch_clamp.single_channel import SingleChannelResult
from ..solvers.osmosis.osmolarity_comparison import OsmolarityComparisonResult
from ..domain.solver_result import OsmosisResult, PatchClampResult, IVCurveData


# ==================== CLASES DE RESULTADO ADAPTADAS ====================
# Estas clases adaptan los resultados internos al formato que espera la GUI

@dataclass
class OsmolarityResultAdapted:
    """Resultado adaptado para la GUI de osmolaridad."""
    osmolarity: float
    concentration_mM: float
    n: int  # Coeficiente de disociación
    g: float  # Coeficiente osmótico
    tonicity_classification: Optional[str]
    clinical_interpretation: Optional[str]
    feedback: List[str]


@dataclass
class VolumeResultAdapted:
    """Resultado adaptado para la GUI de volumen celular."""
    initial_volume: float
    final_volume: float
    internal_osmolarity: float
    external_osmolarity: float
    tonicity: Optional[str]
    interpretation: Optional[str]
    feedback: List[str]


@dataclass
class NernstResultAdapted:
    """Resultado adaptado para la GUI de Nernst."""
    equilibrium_potential: float
    concentration_out: float
    concentration_in: float
    valence: int
    temperature_kelvin: float
    interpretation: Optional[str]
    feedback: List[str]


@dataclass
class GHKResultAdapted:
    """Resultado adaptado para la GUI de Goldman."""
    membrane_potential: float
    ion_contributions: Dict[str, float]
    temperature_kelvin: float
    interpretation: Optional[str]
    feedback: List[str]


@dataclass
class IVCurveResultAdapted:
    """Resultado adaptado para la GUI de curva I-V."""
    voltages: List[float]
    currents: List[float]
    reversal_potential: float
    conductance: float
    iv_curve: Any  # Para compatibilidad con el objeto IVCurveData


class SolverService:
    """
    Servicio que proporciona acceso unificado a todos los solvers.
    
    Actúa como fachada para los diferentes módulos de cálculo,
    proporcionando una interfaz simple para la capa de presentación.
    """
    
    def __init__(self):
        # Inicializar solvers de ósmosis
        self.osmolarity_solver = OsmolaritySolver()
        self.osmolarity_comparison_solver = OsmolarityComparisonSolver()
        self.tonicity_classifier = TonicityClassifier()
        self.cell_volume_solver = CellVolumeSolver()
        
        # Inicializar solvers de Patch Clamp
        self.nernst_solver = NernstSolver()
        self.ghk_solver = GoldmanHodgkinKatzSolver()
        self.iv_curve_solver = IVCurveSolver()
        self.single_channel_solver = SingleChannelSolver()
    
    # ==================== MÉTODOS DE ÓSMOSIS ====================
    
    def calculate_osmolarity(
        self,
        concentration_mM: float = 0,
        solute_name: Optional[str] = None,
        g: Optional[float] = None,
        n: Optional[int] = None,
        # Parámetros alternativos para compatibilidad
        dissociation_coef: Optional[int] = None,
        osmotic_coef: Optional[float] = None,
    ) -> OsmolarityResultAdapted:
        """
        Calcula la osmolaridad de una solución.
        
        Args:
            concentration_mM: Concentración en mM
            solute_name: Nombre del soluto (para autocompletar)
            g: Coeficiente osmótico (alias de osmotic_coef)
            n: Coeficiente de disociación (alias de dissociation_coef)
            
        Returns:
            OsmolarityResultAdapted con osmolaridad y clasificación
        """
        # Usar aliases si se proporcionan
        dissociation = n or dissociation_coef
        osmotic = g or osmotic_coef
        
        result = self.osmolarity_solver.solve(
            concentration_mM=concentration_mM,
            dissociation_coef=dissociation,
            osmotic_coef=osmotic,
            solute_name=solute_name
        )
        
        # Adaptar resultado
        return OsmolarityResultAdapted(
            osmolarity=result.osmolarity or 0.0,
            concentration_mM=concentration_mM,
            n=result.inputs.get("dissociation_coef", 1),
            g=result.inputs.get("osmotic_coef", 1.0),
            tonicity_classification=result.tonicity,
            clinical_interpretation=result.interpretation,
            feedback=result.feedback or []
        )
    
    def calculate_cell_volume(
        self,
        initial_volume: float = 1.0,
        internal_osmolarity: float = 285,
        external_osmolarity: float = 285,
        non_osmotic_fraction: float = 0.4,
        # Alias para compatibilidad
        final_osmolarity: Optional[float] = None,
        initial_osmolarity: Optional[float] = None,
    ) -> VolumeResultAdapted:
        """
        Calcula el cambio de volumen celular.
        
        Args:
            initial_volume: Volumen inicial
            internal_osmolarity: Osmolaridad interna (inicial)
            external_osmolarity: Osmolaridad externa (final)
            non_osmotic_fraction: Fracción no osmótica
            
        Returns:
            VolumeResultAdapted con predicción de volumen
        """
        # Usar parámetros correctos
        osm_initial = initial_osmolarity or internal_osmolarity
        osm_final = final_osmolarity or external_osmolarity
        
        result = self.cell_volume_solver.solve(
            final_osmolarity=osm_final,
            initial_osmolarity=osm_initial,
            initial_volume=initial_volume,
            non_osmotic_fraction=non_osmotic_fraction
        )
        
        # Calcular volumen final
        b = non_osmotic_fraction
        final_vol = (b * initial_volume) + (
            initial_volume * (1 - b) * (osm_initial / osm_final)
        )
        
        return VolumeResultAdapted(
            initial_volume=initial_volume,
            final_volume=final_vol,
            internal_osmolarity=osm_initial,
            external_osmolarity=osm_final,
            tonicity=result.tonicity,
            interpretation=result.interpretation,
            feedback=result.feedback or []
        )
    
    def get_clinical_examples(self) -> Dict:
        """Obtiene ejemplos clínicos de soluciones."""
        return self.tonicity_classifier.get_clinical_examples()
    
    def compare_osmolarities(
        self,
        internal_solutes: List[Dict],
        external_solutes: List[Dict],
    ) -> OsmolarityComparisonResult:
        """
        Compara osmolaridades entre medio intracelular y extracelular.
        
        Args:
            internal_solutes: Lista de solutos intracelulares
                Cada soluto: {name, concentration, j, is_penetrant}
            external_solutes: Lista de solutos extracelulares
                Cada soluto: {name, concentration, j, is_penetrant}
            
        Returns:
            OsmolarityComparisonResult con clasificaciones y coeficiente
        """
        return self.osmolarity_comparison_solver.solve(
            internal_solutes=internal_solutes,
            external_solutes=external_solutes
        )
    
    def get_predefined_solutes(self) -> Dict[str, Dict]:
        """Obtiene la lista de solutos predefinidos con sus propiedades."""
        return self.osmolarity_comparison_solver.PREDEFINED_SOLUTES
    
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
        temperature_C: float = 37,
        # Aliases para compatibilidad con la GUI
        ion_name: Optional[str] = None,
        concentration_out: Optional[float] = None,
        concentration_in: Optional[float] = None,
        valence: Optional[int] = None,
        temperature_celsius: Optional[float] = None,
    ) -> NernstResultAdapted:
        """
        Calcula el potencial de equilibrio de Nernst.
        
        Args:
            ion: Nombre del ion (K+, Na+, Cl-, Ca2+)
            z: Valencia del ion
            C_out: Concentración extracelular (mM)
            C_in: Concentración intracelular (mM)
            temperature_C: Temperatura (°C)
            
        Returns:
            NernstResultAdapted con potencial de equilibrio
        """
        # Usar aliases si están disponibles
        ion_final = ion_name or ion
        z_final = valence if valence is not None else z
        c_out_final = concentration_out if concentration_out is not None else C_out
        c_in_final = concentration_in if concentration_in is not None else C_in
        temp_final = temperature_celsius if temperature_celsius is not None else temperature_C
        
        result = self.nernst_solver.solve(
            ion=ion_final,
            z=z_final,
            C_out=c_out_final,
            C_in=c_in_final,
            temperature_C=temp_final
        )
        
        # Extraer resultado de Nernst
        nernst_data = result.nernst_results[0] if result.nernst_results else None
        
        return NernstResultAdapted(
            equilibrium_potential=nernst_data.E_eq if nernst_data else 0.0,
            concentration_out=c_out_final,
            concentration_in=c_in_final,
            valence=z_final,
            temperature_kelvin=temp_final + 273.15,
            interpretation=result.interpretation,
            feedback=result.feedback or []
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
        temperature_C: float = 37,
        # Aliases para compatibilidad con la GUI
        concentrations_out: Optional[Dict[str, float]] = None,
        concentrations_in: Optional[Dict[str, float]] = None,
        permeabilities: Optional[Dict[str, float]] = None,
        temperature_celsius: Optional[float] = None,
    ) -> GHKResultAdapted:
        """
        Calcula el potencial de membrana usando GHK.
        
        Returns:
            GHKResultAdapted con potencial de membrana
        """
        # Usar diccionarios si están disponibles
        if concentrations_out and concentrations_in and permeabilities:
            K_out = concentrations_out.get("K", K_out)
            Na_out = concentrations_out.get("Na", Na_out)
            Cl_out = concentrations_out.get("Cl", Cl_out)
            K_in = concentrations_in.get("K", K_in)
            Na_in = concentrations_in.get("Na", Na_in)
            Cl_in = concentrations_in.get("Cl", Cl_in)
            P_K = permeabilities.get("K", P_K)
            P_Na = permeabilities.get("Na", P_Na)
            P_Cl = permeabilities.get("Cl", P_Cl)
        
        temp = temperature_celsius if temperature_celsius is not None else temperature_C
        
        # Construir diccionario de iones para el solver
        ions = {
            'K': {'C_out': K_out, 'C_in': K_in, 'P': P_K},
            'Na': {'C_out': Na_out, 'C_in': Na_in, 'P': P_Na},
            'Cl': {'C_out': Cl_out, 'C_in': Cl_in, 'P': P_Cl}
        }
        
        result = self.ghk_solver.solve(
            ions=ions,
            temperature_C=temp
        )
        
        # Calcular contribuciones relativas (simplificado)
        ghk = result.ghk_result
        contributions = {}
        if ghk:
            # Las contribuciones son relativas a las permeabilidades
            total_p = P_K + P_Na + P_Cl
            contributions = {
                "K": P_K / total_p,
                "Na": P_Na / total_p,
                "Cl": P_Cl / total_p
            }
        
        return GHKResultAdapted(
            membrane_potential=ghk.membrane_potential if ghk else 0.0,
            ion_contributions=contributions,
            temperature_kelvin=temp + 273.15,
            interpretation=result.interpretation,
            feedback=result.feedback or []
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
        voltage_range: tuple = (-120, 60),
        voltage_step: float = 10,
    ) -> IVCurveResultAdapted:
        """
        Genera una curva I-V teórica.
        
        Args:
            conductance: Conductancia del canal (nS)
            reversal_potential: Potencial de reversión (mV)
            voltage_range: Rango de voltajes
            voltage_step: Paso de voltaje
            
        Returns:
            IVCurveResultAdapted con datos de curva I-V
        """
        import numpy as np
        
        # Generar voltajes
        voltages = list(np.arange(voltage_range[0], voltage_range[1] + voltage_step, voltage_step))
        
        # Calcular corrientes: I = g * (V - E_rev)
        currents = [conductance * (v - reversal_potential) for v in voltages]
        
        # Crear objeto de curva I-V compatible
        iv_curve = IVCurveData(
            voltage=voltages,
            current=currents,
            reversal_potential=reversal_potential,
            conductance=conductance
        )
        
        return IVCurveResultAdapted(
            voltages=voltages,
            currents=currents,
            reversal_potential=reversal_potential,
            conductance=conductance,
            iv_curve=iv_curve
        )
    
    def analyze_iv_data(
        self,
        voltages: list,
        currents: list
    ) -> PatchClampResult:
        """Analiza datos experimentales de curva I-V."""
        return self.iv_curve_solver.analyze_experimental_data(voltages, currents)
    
    def simulate_single_channel(
        self,
        ion: str,
        membrane_potential: float,
        conductance: float = 20.0,
        equilibrium_potential: Optional[float] = None,
        time_range_ms: float = 10.0,
    ) -> SingleChannelResult:
        """
        Simula un registro de canal único.
        
        Args:
            ion: Tipo de canal ("Na+" o "K+")
            membrane_potential: Potencial de membrana aplicado (mV)
            conductance: Conductancia del canal (pS). Por defecto 20 pS
            equilibrium_potential: Potencial de equilibrio (mV).
                                   Por defecto +50 mV para Na+, -80 mV para K+
            time_range_ms: Duración del registro en ms. Por defecto 10 ms
            
        Returns:
            SingleChannelResult con los datos de la simulación
        """
        return self.single_channel_solver.solve(
            ion=ion,
            membrane_potential=membrane_potential,
            conductance=conductance,
            equilibrium_potential=equilibrium_potential,
            time_range_ms=time_range_ms
        )
    
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
