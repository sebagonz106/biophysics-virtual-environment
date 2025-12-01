"""
Simulador de dinámica de volumen celular.

Este módulo contiene la lógica para simular cambios de volumen celular
en el tiempo usando ecuaciones diferenciales ordinarias (ODE).
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from scipy.integrate import odeint


@dataclass
class VolumeDynamicsParams:
    """Parámetros para la simulación de dinámica de volumen."""
    V0: float = 1.0  # Volumen inicial normalizado
    b: float = 0.4   # Fracción no osmótica (0.0-0.4 típico)
    Lp: float = 0.5  # Permeabilidad hidráulica (normalizada)
    t_max: float = 30.0  # Tiempo máximo de simulación (s)
    n_points: int = 300  # Número de puntos en la simulación


@dataclass
class VolumeDynamicsResult:
    """Resultado de la simulación de dinámica de volumen."""
    time: np.ndarray
    volume: np.ndarray
    volume_percent: np.ndarray
    n_penetrant: np.ndarray
    lysis_detected: bool = False
    lysis_time: Optional[float] = None
    lysis_volume_percent: Optional[float] = None
    final_volume_percent: float = 100.0


class VolumeDynamicsSimulator:
    """
    Simulador de dinámica de volumen celular.
    
    Modelo de ecuaciones diferenciales:
    
    Para solutos NO penetrantes:
        dV/dt = Lp * A * (π_int - π_ext)
    
    Para solutos penetrantes:
        dn_s/dt = P_s * A * (C_s_ext - C_s_int)
    
    Donde:
        V = volumen celular
        Lp = permeabilidad hidráulica
        A = área de membrana (proporcional a V^(2/3))
        n = moles de soluto
        P_s = permeabilidad del soluto penetrante
    """
    
    def __init__(self, params: Optional[VolumeDynamicsParams] = None):
        """
        Inicializa el simulador.
        
        Args:
            params: Parámetros de simulación. Si es None, usa valores por defecto.
        """
        self.params = params or VolumeDynamicsParams()
    
    def calculate_effective_permeability(
        self,
        internal_solutes: List[Dict],
        external_solutes: List[Dict]
    ) -> float:
        """
        Calcula la permeabilidad efectiva de solutos penetrantes.
        
        Usa un promedio ponderado por concentración.
        
        Args:
            internal_solutes: Lista de solutos intracelulares
            external_solutes: Lista de solutos extracelulares
            
        Returns:
            Permeabilidad efectiva (escalada para visualización)
        """
        ext_penetrants = [s for s in external_solutes if s.get("is_penetrant", False)]
        int_penetrants = [s for s in internal_solutes if s.get("is_penetrant", False)]
        
        total_pen_conc = sum(
            s.get("concentration", 0) 
            for s in ext_penetrants + int_penetrants
        )
        
        if total_pen_conc > 0:
            Ps = sum(
                s.get("permeability", 0.0) * s.get("concentration", 0)
                for s in ext_penetrants + int_penetrants
            ) / total_pen_conc
            # Escalar para visualización (cm/s -> unidades normalizadas)
            Ps = Ps * 1e4
        else:
            Ps = 0.0
        
        # Valor mínimo si hay penetrantes
        if any(ext_penetrants) or any(int_penetrants):
            Ps = max(Ps, 0.01)
        
        return Ps
    
    def calculate_osmolarities(
        self,
        internal_solutes: List[Dict],
        external_solutes: List[Dict]
    ) -> Dict[str, float]:
        """
        Calcula las osmolaridades de ambos compartimentos.
        
        Args:
            internal_solutes: Lista de solutos intracelulares
            external_solutes: Lista de solutos extracelulares
            
        Returns:
            Diccionario con osmolaridades calculadas
        """
        # Intracelular
        int_nonpen_osm = sum(
            s["concentration"] * s["j"] 
            for s in internal_solutes if not s.get("is_penetrant", False)
        )
        int_pen_osm = sum(
            s["concentration"] * s["j"]
            for s in internal_solutes if s.get("is_penetrant", False)
        )
        
        # Extracelular
        ext_nonpen_osm = sum(
            s["concentration"] * s["j"]
            for s in external_solutes if not s.get("is_penetrant", False)
        )
        ext_pen_osm = sum(
            s["concentration"] * s["j"]
            for s in external_solutes if s.get("is_penetrant", False)
        )
        
        total_int_osm = int_nonpen_osm + int_pen_osm
        if total_int_osm <= 0:
            total_int_osm = 280  # Valor por defecto
        
        return {
            "int_nonpen": int_nonpen_osm,
            "int_pen": int_pen_osm,
            "ext_nonpen": ext_nonpen_osm,
            "ext_pen": ext_pen_osm,
            "total_int": total_int_osm
        }
    
    def simulate(
        self,
        internal_solutes: List[Dict],
        external_solutes: List[Dict],
        critical_volume: Optional[float] = None
    ) -> VolumeDynamicsResult:
        """
        Simula la dinámica del volumen celular.
        
        Args:
            internal_solutes: Lista de solutos intracelulares
            external_solutes: Lista de solutos extracelulares
            critical_volume: Volumen crítico para lisis (V/V0). None = sin detección de lisis.
            
        Returns:
            VolumeDynamicsResult con los resultados de la simulación
        """
        V0 = self.params.V0
        b = self.params.b
        Lp = self.params.Lp
        V_osm_0 = V0 * (1 - b)
        
        # Calcular permeabilidad efectiva
        Ps = self.calculate_effective_permeability(internal_solutes, external_solutes)
        
        # Calcular osmolaridades
        osm = self.calculate_osmolarities(internal_solutes, external_solutes)
        total_int_osm = osm["total_int"]
        
        # Cantidades iniciales de soluto (n = C * V)
        n_int_nonpen_0 = osm["int_nonpen"] * V_osm_0 / total_int_osm
        n_int_pen_0 = osm["int_pen"] * V_osm_0 / total_int_osm
        
        # Concentraciones externas normalizadas
        C_ext_nonpen = osm["ext_nonpen"] / total_int_osm
        C_ext_pen = osm["ext_pen"] / total_int_osm
        
        def osmotic_dynamics(y, t):
            """Sistema de ecuaciones diferenciales."""
            V = y[0]
            n_pen = y[1]
            
            # Asegurar V positivo
            V = max(V, 0.1 * V0)
            
            # Volumen osmótico actual
            V_osm = max(V - V0 * b, 0.01)
            
            # Área de membrana
            A = abs(V) ** (2/3)
            
            # Concentraciones intracelulares actuales
            C_int_nonpen = n_int_nonpen_0 / V_osm
            C_int_pen = max(n_pen, 0) / V_osm
            
            # Osmolaridades totales
            pi_int_total = C_int_nonpen + C_int_pen
            pi_ext_total = C_ext_nonpen + C_ext_pen
            
            # Flujo de agua
            # Si pi_int > pi_ext: agua entra, V aumenta (hipotónico)
            # Si pi_ext > pi_int: agua sale, V disminuye (hipertónico)
            dV_dt = Lp * A * (pi_int_total - pi_ext_total)
            
            # Flujo de soluto penetrante
            dn_pen_dt = Ps * A * (C_ext_pen - C_int_pen)
            
            return [dV_dt, dn_pen_dt]
        
        # Tiempo de simulación
        t = np.linspace(0, self.params.t_max, self.params.n_points)
        
        # Condiciones iniciales
        y0 = [V0, max(n_int_pen_0, 0)]
        
        # Resolver ODE
        try:
            solution = odeint(osmotic_dynamics, y0, t, rtol=1e-6, atol=1e-8)
            V_t = solution[:, 0]
            n_pen_t = solution[:, 1]
            V_t = np.maximum(V_t, 0.1 * V0)
        except Exception:
            V_t = np.ones_like(t) * V0
            n_pen_t = np.ones_like(t) * max(n_int_pen_0, 0)
        
        # Normalizar como porcentaje
        V_percent = (V_t / V0) * 100
        
        # Detectar lisis si se especificó volumen crítico
        lysis_detected = False
        lysis_time = None
        lysis_volume_percent = None
        
        if critical_volume is not None:
            critical_percent = critical_volume * 100
            lysis_idx = np.where(V_percent >= critical_percent)[0]
            if len(lysis_idx) > 0:
                lysis_detected = True
                lysis_time = t[lysis_idx[0]]
                lysis_volume_percent = V_percent[lysis_idx[0]]
        
        return VolumeDynamicsResult(
            time=t,
            volume=V_t,
            volume_percent=V_percent,
            n_penetrant=n_pen_t,
            lysis_detected=lysis_detected,
            lysis_time=lysis_time,
            lysis_volume_percent=lysis_volume_percent,
            final_volume_percent=V_percent[-1]
        )
    
    def simulate_until_lysis(
        self,
        internal_solutes: List[Dict],
        external_solutes: List[Dict],
        critical_volume: float
    ) -> VolumeDynamicsResult:
        """
        Simula la dinámica del volumen específicamente para casos de lisis.
        
        Usa parámetros ajustados para visualizar mejor el proceso de lisis.
        
        Args:
            internal_solutes: Lista de solutos intracelulares
            external_solutes: Lista de solutos extracelulares
            critical_volume: Volumen crítico para lisis (V/V0)
            
        Returns:
            VolumeDynamicsResult con los resultados de la simulación
        """
        # Usar parámetros específicos para lisis
        original_b = self.params.b
        original_t_max = self.params.t_max
        original_n_points = self.params.n_points
        
        # Ajustar para visualización de lisis
        self.params.b = 0.0  # Sin fracción no osmótica para modelo simplificado
        self.params.t_max = 60.0  # Más tiempo para ver la dinámica
        self.params.n_points = 400
        
        result = self.simulate(internal_solutes, external_solutes, critical_volume)
        
        # Restaurar parámetros
        self.params.b = original_b
        self.params.t_max = original_t_max
        self.params.n_points = original_n_points
        
        return result


# Instancia global del simulador con parámetros por defecto
default_simulator = VolumeDynamicsSimulator()


def simulate_volume_dynamics(
    internal_solutes: List[Dict],
    external_solutes: List[Dict],
    critical_volume: Optional[float] = None,
    params: Optional[VolumeDynamicsParams] = None
) -> VolumeDynamicsResult:
    """
    Función de conveniencia para simular dinámica de volumen.
    
    Args:
        internal_solutes: Lista de solutos intracelulares
        external_solutes: Lista de solutos extracelulares
        critical_volume: Volumen crítico para lisis (V/V0). None = sin detección.
        params: Parámetros de simulación. None = usar valores por defecto.
        
    Returns:
        VolumeDynamicsResult con los resultados
    """
    if params:
        simulator = VolumeDynamicsSimulator(params)
    else:
        simulator = default_simulator
    
    return simulator.simulate(internal_solutes, external_solutes, critical_volume)


def simulate_lysis_dynamics(
    internal_solutes: List[Dict],
    external_solutes: List[Dict],
    critical_volume: float,
    params: Optional[VolumeDynamicsParams] = None
) -> VolumeDynamicsResult:
    """
    Función de conveniencia para simular dinámica hasta lisis.
    
    Args:
        internal_solutes: Lista de solutos intracelulares
        external_solutes: Lista de solutos extracelulares
        critical_volume: Volumen crítico para lisis (V/V0)
        params: Parámetros de simulación. None = usar valores por defecto.
        
    Returns:
        VolumeDynamicsResult con los resultados
    """
    if params:
        simulator = VolumeDynamicsSimulator(params)
    else:
        simulator = VolumeDynamicsSimulator()
    
    return simulator.simulate_until_lysis(
        internal_solutes, external_solutes, critical_volume
    )
