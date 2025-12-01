"""
Solver para cálculo de osmolaridad con solutos múltiples.
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from ..base_solver import BaseSolver


@dataclass
class Solute:
    """Representa un soluto en la solución."""
    name: str
    concentration_mM: float
    dissociation_coefficient: int  # Factor j (coeficiente de disociación)
    is_penetrant: bool = False  # Si atraviesa la membrana
    permeability_cm_s: float = 0.0  # Permeabilidad en cm/s (para solutos penetrantes)
    
    @property
    def osmolarity_contribution(self) -> float:
        """Contribución a la osmolaridad en mOsm/L."""
        return self.concentration_mM * self.dissociation_coefficient


@dataclass
class OsmolarityComparisonResult:
    """Resultado de la comparación de osmolaridades."""
    success: bool
    
    # Osmolaridades totales
    internal_osmolarity: float = 0.0
    external_osmolarity: float = 0.0
    
    # Presión osmótica real (solo no penetrantes)
    internal_effective_osmolarity: float = 0.0
    external_effective_osmolarity: float = 0.0
    
    # Coeficiente de presión osmótica real (Osm_int_eff / Osm_ext_eff)
    effective_osmolarity_ratio: float = 1.0
    
    # Clasificaciones
    osmotic_classification: str = ""  # Hiperosmótica, Hiposmótica, Isosmótica
    tonic_classification: str = ""    # Hipertónica, Hipotónica, Isotónica
    
    # Detalles de solutos
    internal_solutes: List[Solute] = field(default_factory=list)
    external_solutes: List[Solute] = field(default_factory=list)
    
    interpretation: str = ""
    feedback: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class OsmolarityComparisonSolver(BaseSolver):
    """
    Calcula y compara osmolaridades entre medio intracelular y extracelular.
    
    Permite:
    - Múltiples solutos por compartimento
    - Clasificación osmótica (basada en osmolaridad total)
    - Clasificación tónica (basada en solutos no penetrantes)
    - Cálculo de volumen final celular
    """
    
    name = "osmolarity_comparison"
    description = "Compara osmolaridades intracelular y extracelular"
    
    # Solutos predefinidos con sus propiedades
    # (nombre, factor_j, es_penetrante)
    PREDEFINED_SOLUTES = {
        # Electrolitos (no penetrantes por defecto)
        "NaCl": {"j": 2, "penetrant": False, "description": "Cloruro de sodio"},
        "KCl": {"j": 2, "penetrant": False, "description": "Cloruro de potasio"},
        "CaCl₂": {"j": 3, "penetrant": False, "description": "Cloruro de calcio"},
        "MgCl₂": {"j": 3, "penetrant": False, "description": "Cloruro de magnesio"},
        "NaHCO₃": {"j": 2, "penetrant": False, "description": "Bicarbonato de sodio"},
        
        # No electrolitos
        "Glucosa": {"j": 1, "penetrant": False, "description": "Glucosa (no penetrante)"},
        "Sacarosa": {"j": 1, "penetrant": False, "description": "Sacarosa (no penetrante)"},
        "Manitol": {"j": 1, "penetrant": False, "description": "Manitol (no penetrante)"},
        "Urea": {"j": 1, "penetrant": True, "description": "Urea (penetrante)"},
    }
    
    # Osmolaridad de referencia del plasma
    PLASMA_OSMOLARITY = 285  # mOsm/L
    TOLERANCE = 5  # mOsm/L para considerar isotónico
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "internal_solutes": {
                "type": list,
                "description": "Lista de solutos intracelulares",
            },
            "external_solutes": {
                "type": list,
                "description": "Lista de solutos extracelulares",
            },
        }
    
    def solve(
        self,
        internal_solutes: List[Dict],
        external_solutes: List[Dict],
        **kwargs
    ) -> OsmolarityComparisonResult:
        """
        Calcula y compara osmolaridades.
        
        Args:
            internal_solutes: Lista de dicts con {name, concentration, j, is_penetrant}
            external_solutes: Lista de dicts con {name, concentration, j, is_penetrant}
            
        Returns:
            OsmolarityComparisonResult con todos los cálculos
        """
        # Convertir a objetos Solute
        int_solutes = [
            Solute(
                name=s.get("name", "Unknown"),
                concentration_mM=float(s.get("concentration", 0)),
                dissociation_coefficient=int(s.get("j", 1)),
                is_penetrant=bool(s.get("is_penetrant", False)),
                permeability_cm_s=float(s.get("permeability", 0.0))
            )
            for s in internal_solutes
        ]
        
        ext_solutes = [
            Solute(
                name=s.get("name", "Unknown"),
                concentration_mM=float(s.get("concentration", 0)),
                dissociation_coefficient=int(s.get("j", 1)),
                is_penetrant=bool(s.get("is_penetrant", False)),
                permeability_cm_s=float(s.get("permeability", 0.0))
            )
            for s in external_solutes
        ]
        
        # Calcular osmolaridades totales
        internal_osm = sum(s.osmolarity_contribution for s in int_solutes)
        external_osm = sum(s.osmolarity_contribution for s in ext_solutes)
        
        # Calcular presiones osmóticas reales (solo no penetrantes)
        internal_effective = sum(
            s.osmolarity_contribution for s in int_solutes if not s.is_penetrant
        )
        external_effective = sum(
            s.osmolarity_contribution for s in ext_solutes if not s.is_penetrant
        )
        
        # Clasificación osmótica (basada en totales)
        osmotic_class = self._classify_osmotic(external_osm, internal_osm)
        
        # Calcular coeficiente de presión osmótica real
        eff_ratio = self._calculate_effective_ratio(internal_effective, external_effective)
        
        # Clasificación tónica (basada en coeficiente de presión osmótica real)
        tonic_class = self._classify_tonic(eff_ratio)
        
        # Generar interpretación y feedback
        interpretation = self._generate_interpretation(
            internal_osm, external_osm,
            internal_effective, external_effective,
            osmotic_class, tonic_class,
            eff_ratio
        )
        
        feedback = self._generate_feedback(
            int_solutes, ext_solutes,
            internal_osm, external_osm,
            internal_effective, external_effective,
            osmotic_class, tonic_class
        )
        
        return OsmolarityComparisonResult(
            success=True,
            internal_osmolarity=round(internal_osm, 2),
            external_osmolarity=round(external_osm, 2),
            internal_effective_osmolarity=round(internal_effective, 2),
            external_effective_osmolarity=round(external_effective, 2),
            effective_osmolarity_ratio=round(eff_ratio, 4),
            osmotic_classification=osmotic_class,
            tonic_classification=tonic_class,
            internal_solutes=int_solutes,
            external_solutes=ext_solutes,
            interpretation=interpretation,
            feedback=feedback
        )
    
    def _classify_osmotic(self, external: float, internal: float) -> str:
        """Clasifica la solución según osmolaridad total."""
        diff = external - internal
        if diff > self.TOLERANCE:
            return "Hiperosmótica"
        elif diff < -self.TOLERANCE:
            return "Hiposmótica"
        else:
            return "Isosmótica"
    
    def _calculate_effective_ratio(
        self,
        internal_effective: float,
        external_effective: float
    ) -> float:
        """
        Calcula el coeficiente de presión osmótica real:
        coef = Pi_int_real / Pi_ext_real
        
        Este coeficiente indica:
        - coef < 1: Hipertónica (célula se encoge)
        - coef > 1: Hipotónica (célula se hincha)
        - coef ≈ 1: Isotónica (volumen estable)
        """
        if external_effective <= 0:
            # Evitar división por cero - célula lisaría
            return 10.0  # Valor muy alto indica lisis
        
        return internal_effective / external_effective
    
    def _classify_tonic(self, eff_ratio: float) -> str:
        """
        Clasifica la tonicidad según el coeficiente de presión osmótica real.
        
        coef < 1: Hipertónica (Pi_ext_real > Pi_int_real → agua sale → célula se encoge)
        coef > 1: Hipotónica (Pi_int_real > Pi_ext_real → agua entra → célula se hincha)
        coef ≈ 1: Isotónica (equilibrio → volumen estable)
        """
        tolerance = 0.02  # 2% de tolerancia
        
        if eff_ratio < (1 - tolerance):
            return "Hipertónica"
        elif eff_ratio > (1 + tolerance):
            return "Hipotónica"
        else:
            return "Isotónica"
    
    def _generate_interpretation(
        self,
        int_osm: float, ext_osm: float,
        int_eff: float, ext_eff: float,
        osm_class: str, ton_class: str,
        eff_ratio: float
    ) -> str:
        """Genera interpretación del resultado."""
        interpretation = (
            f"La solución extracelular tiene una osmolaridad total de {ext_osm:.1f} mOsm/L "
            f"comparada con {int_osm:.1f} mOsm/L intracelular.\n\n"
        )
        
        if int_eff != int_osm or ext_eff != ext_osm:
            interpretation += (
                f"Considerando solo solutos no penetrantes:\n"
                f"- Presión osmótica real interna: {int_eff:.1f} mOsm/L\n"
                f"- Presión osmótica real externa: {ext_eff:.1f} mOsm/L\n\n"
            )
        
        # Clasificaciones destacadas
        interpretation += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        interpretation += f"🌡️ CLASIFICACIÓN SEGÚN OSMOTICIDAD: {osm_class}\n"
        interpretation += f"💧 CLASIFICACIÓN SEGÚN TONICIDAD: {ton_class}\n"
        interpretation += f"   Coeficiente de presión osmótica real: {eff_ratio:.4f}\n"
        interpretation += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if ton_class == "Hipertónica":
            interpretation += (
                "⚠️ Coef < 1: La célula perderá agua y se encogerá (disecación). "
                "Los solutos no penetrantes externos crean un gradiente osmótico "
                "que extrae agua de la célula."
            )
        elif ton_class == "Hipotónica":
            interpretation += (
                "⚠️ Coef > 1: La célula ganará agua y se hinchará. "
                "Puede llegar a lisarse si la diferencia es muy grande. "
                "El agua entra para diluir los solutos no penetrantes internos."
            )
        else:
            interpretation += (
                "✓ Coef ≈ 1: La célula mantiene su volumen. No hay movimiento neto de agua "
                "porque las presiones osmóticas reales están equilibradas."
            )
        
        return interpretation
    
    def _generate_feedback(
        self,
        int_solutes: List[Solute],
        ext_solutes: List[Solute],
        int_osm: float, ext_osm: float,
        int_eff: float, ext_eff: float,
        osm_class: str, ton_class: str
    ) -> List[str]:
        """Genera retroalimentación educativa."""
        feedback = []
        
        # Resumen de solutos
        feedback.append("📋 Solutos intracelulares:")
        for s in int_solutes:
            pen_str = "(penetrante)" if s.is_penetrant else "(no penetrante)"
            feedback.append(
                f"  • {s.name}: {s.concentration_mM} mM × j={s.dissociation_coefficient} = "
                f"{s.osmolarity_contribution:.1f} mOsm/L {pen_str}"
            )
        
        feedback.append("")
        feedback.append("📋 Solutos extracelulares:")
        for s in ext_solutes:
            pen_str = "(penetrante)" if s.is_penetrant else "(no penetrante)"
            feedback.append(
                f"  • {s.name}: {s.concentration_mM} mM × j={s.dissociation_coefficient} = "
                f"{s.osmolarity_contribution:.1f} mOsm/L {pen_str}"
            )
        
        feedback.append("")
        feedback.append("📖 Conceptos clave:")
        
        if osm_class != ton_class.replace("tónica", "smótica"):
            feedback.append(
                "⚡ La clasificación osmótica y tónica son diferentes porque "
                "hay solutos penetrantes que contribuyen a la osmolaridad total "
                "pero no afectan el volumen celular."
            )
        
        feedback.append(
            "• Osmolaridad: concentración total de partículas osmóticamente activas"
        )
        feedback.append(
            "• Tonicidad: efecto sobre el volumen celular (solo solutos no penetrantes)"
        )
        feedback.append(
            "• Solutos penetrantes (ej: urea) atraviesan la membrana y no causan "
            "movimiento neto de agua a largo plazo"
        )
        
        return feedback
    
    def get_predefined_solute(self, name: str) -> Optional[Dict]:
        """Obtiene información de un soluto predefinido."""
        return self.PREDEFINED_SOLUTES.get(name)
    
    def list_predefined_solutes(self) -> List[str]:
        """Lista los nombres de solutos predefinidos."""
        return list(self.PREDEFINED_SOLUTES.keys())
