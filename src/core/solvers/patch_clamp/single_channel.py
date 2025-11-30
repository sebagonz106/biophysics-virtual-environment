"""
Solver para simulación de registro de canal único (Patch Clamp).

Genera datos de corriente en función del tiempo para un canal iónico,
simulando el comportamiento estocástico de apertura/cierre del canal.
"""

from typing import Any, Dict, List, Tuple, Optional
from random import uniform
from dataclasses import dataclass
from ..base_solver import BaseSolver


@dataclass
class SingleChannelData:
    """Datos de un registro de canal único."""
    
    intensity: float  # Corriente en pA
    is_fast: bool  # Si el canal tiene cinética rápida (Na+) o lenta (K+)
    activation_intervals: List[Tuple[float, float]]  # Intervalos de apertura [0,1]
    time_intervals_ms: List[Tuple[float, float]]  # Intervalos escalados a ms
    ion: str  # Ion del canal
    membrane_potential: float  # Potencial de membrana aplicado
    equilibrium_potential: float  # Potencial de equilibrio
    conductance: float  # Conductancia del canal
    time_range_ms: float  # Rango de tiempo total en ms


@dataclass
class SingleChannelResult:
    """Resultado completo de la simulación de canal único."""
    
    success: bool
    channel_data: Optional[SingleChannelData]
    time_points: List[float]  # Puntos de tiempo para graficar
    current_points: List[float]  # Valores de corriente para graficar
    interpretation: str
    feedback: List[str]
    error_message: Optional[str] = None


class SingleChannelSolver(BaseSolver):
    """
    Simula el registro de corriente de un canal iónico único.
    
    Modela el comportamiento estocástico de apertura y cierre de canales
    iónicos dependientes de voltaje, típico de experimentos de patch clamp
    en configuración de canal único (single-channel recording).
    
    Características del modelo:
    - La probabilidad de apertura aumenta con la despolarización
    - Los canales de Na+ tienen cinética rápida (activación e inactivación)
    - Los canales de K+ tienen cinética lenta (solo activación)
    - La corriente sigue la ley de Ohm: I = g × (Vm - Eeq)
    """
    
    name = "single_channel_simulator"
    description = "Simula registros de corriente de canal único"
    
    # Valores por defecto típicos
    DEFAULT_CONDUCTANCE_NA = 20.0  # pS (picosiemens)
    DEFAULT_CONDUCTANCE_K = 20.0   # pS
    DEFAULT_E_NA = 50.0   # mV (potencial de equilibrio Na+)
    DEFAULT_E_K = -80.0   # mV (potencial de equilibrio K+)
    DEFAULT_V_REST = -70.0  # mV (potencial de reposo)
    DEFAULT_TIME_RANGE = 10.0  # ms (rango típico de registro)
    
    def get_required_params(self) -> Dict[str, Dict[str, Any]]:
        return {
            "ion": {
                "type": str,
                "description": "Tipo de canal iónico (Na+ o K+)",
                "options": ["Na+", "K+"],
            },
            "membrane_potential": {
                "type": float,
                "description": "Potencial de membrana aplicado (mV)",
                "unit": "mV",
                "range": (-100, 100),
            },
            "conductance": {
                "type": float,
                "description": "Conductancia del canal (pS)",
                "unit": "pS",
                "default": 20.0,
                "range": (1, 100),
            },
            "equilibrium_potential": {
                "type": float,
                "description": "Potencial de equilibrio del ion (mV)",
                "unit": "mV",
                "default": 50.0,  # Para Na+
                "range": (-150, 100),
            },
            "time_range_ms": {
                "type": float,
                "description": "Duración del registro (ms)",
                "unit": "ms",
                "default": 10.0,
                "range": (1, 100),
            },
        }
    
    def solve(
        self,
        ion: str,
        membrane_potential: float,
        conductance: Optional[float] = None,
        equilibrium_potential: Optional[float] = None,
        time_range_ms: float = 20.0,
        **kwargs
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
        # Validar ion
        if ion not in ["Na+", "K+"]:
            return SingleChannelResult(
                success=False,
                channel_data=None,
                time_points=[],
                current_points=[],
                interpretation="",
                feedback=[],
                error_message=f"Ion no soportado: {ion}. Use 'Na+' o 'K+'"
            )
        
        # Establecer valores por defecto según el ion
        if conductance is None:
            conductance = self.DEFAULT_CONDUCTANCE_NA if ion == "Na+" else self.DEFAULT_CONDUCTANCE_K
        
        if equilibrium_potential is None:
            equilibrium_potential = self.DEFAULT_E_NA if ion == "Na+" else self.DEFAULT_E_K
        
        # Generar datos del canal
        intensity, is_fast, activation_intervals = self._simulate_channel(
            ion=ion,
            membrane_potential=membrane_potential,
            conductance=conductance,
            equilibrium_potential=equilibrium_potential
        )
        
        # Escalar intervalos al rango de tiempo
        idle = time_range_ms / 20
        stop = time_range_ms / 5
        relative_time_range_ms = time_range_ms - 2  * idle - stop

        if not is_fast: idle += stop

        time_intervals_ms = [
            (idle + t0 * relative_time_range_ms, idle + t1 * relative_time_range_ms)
            for t0, t1 in activation_intervals
        ]
        
        # Generar puntos para la gráfica
        time_points, current_points = self._generate_plot_data(
            intensity=intensity,
            activation_intervals=time_intervals_ms,
            time_range_ms=time_range_ms
        )
        
        # Crear datos del canal
        channel_data = SingleChannelData(
            intensity=round(intensity, 2),
            is_fast=is_fast,
            activation_intervals=activation_intervals,
            time_intervals_ms=time_intervals_ms,
            ion=ion,
            membrane_potential=membrane_potential,
            equilibrium_potential=equilibrium_potential,
            conductance=conductance,
            time_range_ms=time_range_ms
        )
        
        # Generar interpretación y feedback
        interpretation = self._generate_interpretation(channel_data)
        feedback = self._generate_feedback(channel_data)
        
        return SingleChannelResult(
            success=True,
            channel_data=channel_data,
            time_points=time_points,
            current_points=current_points,
            interpretation=interpretation,
            feedback=feedback
        )
    
    def _simulate_channel(
        self,
        ion: str,
        membrane_potential: float,
        conductance: float,
        equilibrium_potential: float
    ) -> Tuple[float, bool, List[Tuple[float, float]]]:
        """
        Simula el comportamiento del canal iónico.
        
        Implementa el algoritmo estocástico para generar
        intervalos de apertura del canal.
        
        Returns:
            Tuple con (intensidad, es_rápido, intervalos_activación)
        """
        resting_potential = self.DEFAULT_V_REST
        data: List[Tuple[float, float]] = []
        
        # Calcular intensidad de corriente: I = g × (Vm - Eeq)
        intensity = conductance * (membrane_potential - equilibrium_potential)
        
        # Determinar cinética (rápida para Na+, lenta para K+)
        is_fast = (ion == "Na+")
        
        # Si el potencial es hiperpolarizante, el canal no se abre
        if membrane_potential <= resting_potential:
            return (0.0, is_fast, data)
        
        # Caso especial: Na+ en su potencial de equilibrio
        if ion == "Na+" and abs(membrane_potential - equilibrium_potential) < 0.1:
            # El canal está abierto pero no hay corriente neta
            return (0.0, is_fast, data)
        
        # Calcular probabilidad de apertura
        # Aumenta con la despolarización, máximo ~0.75
        p = min(
            0.75,
            (3 * (membrane_potential - resting_potential)) / 
            (4 * (self.DEFAULT_CONDUCTANCE_NA - resting_potential))
        )
        
        # Asegurar probabilidad no negativa
        p = max(0.0, p)
        
        # Generar intervalos de apertura estocásticos
        rate = 2
        min_interval = 0.025 * rate
        print("Probabilidad de apertura:", p, "\n\n")
        real_prob = 1.0
        while real_prob > p or real_prob < 5 * p / 6:
            x_0 = 0.0
            last = rate * 1.0
            data = []

            if(ion == "Na+"):
                x_0 = uniform(min_interval, p/2)
                data.append((0.0, x_0))
            if(ion == "K+"):
                last -= uniform(min_interval, p/2)
                data.append((last, rate * 1.0))

            while x_0 < last:
                u = uniform(0, 1)
                if u < p:
                    # Canal se abre
                    duration = uniform(min_interval, p/2)
                    x_1 = min(last, x_0 + duration)
                    data.append((x_0, x_1))
                    x_0 = x_1
                else:
                    # Canal permanece cerrado
                    x_0 += uniform(min_interval, (1 - p) / 2)
            
            real_prob = sum(t1 - t0 for t0, t1 in data) / rate

            data = sorted(data, key=lambda x: x[0])
            print(real_prob, data, "\n")

        # Procesar datos para evitar solapamientos y duraciones excesivas
        prev = (0.0, 0.0)
        processed_data = []
        
        for t0, t1 in data:
            t0 /= rate
            t1 /= rate
            
            if t0 <= prev[1]:
                prev = (prev[0], t1)
            else:
                if prev != (0.0, 0.0): processed_data.append(prev)
                prev = (t0, t1)
            
            t0 = prev[0]
            t1 = prev[1]

            if t1-t0 > 0.4:
                new_t1 = t0 + uniform(0.025, 0.4)
                new_t0 = (3 * new_t1 + t1) / 4
                processed_data.append((t0, new_t1))
                prev = (new_t0, t1)
        
        if prev != (0.0, 0.0) and prev not in processed_data:
            processed_data.append(prev)

        print(processed_data)

        return (intensity, is_fast, processed_data)
    
    def _generate_plot_data(
        self,
        intensity: float,
        activation_intervals: List[Tuple[float, float]],
        time_range_ms: float,
        resolution: int = 1000
    ) -> Tuple[List[float], List[float]]:
        """
        Genera los puntos de datos para la gráfica rectangular.
        
        Args:
            intensity: Intensidad de corriente cuando el canal está abierto
            activation_intervals: Intervalos de apertura en el intervalo requerido
            time_range_ms: Rango de tiempo total en ms
            resolution: Número de puntos para la gráfica
            
        Returns:
            Tuple con (lista_tiempos, lista_corrientes)
        """
        time_points = []
        current_points = []
        
        # Crear puntos para gráfica rectangular (step plot)
        for t0, t1 in activation_intervals:
            # Punto de inicio (subida)
            time_points.extend([t0, t0])
            current_points.extend([0.0, intensity])
            
            # Punto de fin (bajada)
            time_points.extend([t1, t1])
            current_points.extend([intensity, 0.0])

        # Si no hay activaciones, crear línea base
        if not activation_intervals:
            time_points = [0.0, time_range_ms]
            current_points = [0.0, 0.0]
        else:
            # Añadir puntos inicial y final si es necesario
            if time_points[0] > 0:
                time_points.insert(0, 0.0)
                current_points.insert(0, 0.0)
            if time_points[-1] < time_range_ms:
                time_points.append(time_range_ms)
                current_points.append(0.0)
        
        return time_points, current_points
    
    def _generate_interpretation(self, data: SingleChannelData) -> str:
        """Genera interpretación del resultado."""
        if data.intensity == 0 and not data.activation_intervals:
            if data.membrane_potential < self.DEFAULT_V_REST:
                return (
                    f"El canal de {data.ion} permanece cerrado porque el potencial "
                    f"de membrana ({data.membrane_potential} mV) es hiperpolarizante "
                    f"respecto al potencial de reposo ({self.DEFAULT_V_REST} mV). "
                    "Los canales dependientes de voltaje requieren despolarización para abrirse."
                )
            else:
                return (
                    f"No se registró corriente. El potencial de membrana está cerca "
                    f"del potencial de equilibrio del {data.ion}."
                )
        
        direction = "entrante (negativa)" if data.intensity < 0 else "saliente (positiva)"
        kinetics = "rápida (activación e inactivación)" if data.is_fast else "lenta (solo activación)"
        
        num_openings = len(data.activation_intervals)
        total_open_time = sum(t1 - t0 for t0, t1 in data.time_intervals_ms)
        open_probability = total_open_time / data.time_range_ms if data.time_range_ms > 0 else 0
        
        return (
            f"Registro de canal de {data.ion} a Vm = {data.membrane_potential} mV.\n\n"
            f"Se registró una corriente {direction} de {abs(data.intensity):.1f} pA "
            f"cuando el canal está abierto.\n\n"
            f"El canal mostró {num_openings} eventos de apertura durante los "
            f"{data.time_range_ms:.1f} ms de registro, con una probabilidad de "
            f"apertura aproximada de {open_probability:.1%}.\n\n"
            f"Cinética del canal: {kinetics}."
        )
    
    def _generate_feedback(self, data: SingleChannelData) -> List[str]:
        """Genera retroalimentación educativa."""
        feedback = []
        
        feedback.append(
            f"Canal: {data.ion} | Conductancia: {data.conductance} pS"
        )
        
        feedback.append(
            f"Potencial de membrana: {data.membrane_potential} mV | "
            f"Potencial de equilibrio: {data.equilibrium_potential} mV"
        )
        
        feedback.append(
            f"Fuerza impulsora: ΔV = {data.membrane_potential - data.equilibrium_potential:.1f} mV"
        )
        
        feedback.append(
            f"Corriente unitaria: I = g × ΔV = {data.conductance} × "
            f"{data.membrane_potential - data.equilibrium_potential:.1f} = {data.intensity:.1f} pA"
        )
        
        if data.activation_intervals:
            total_open = sum(t1 - t0 for t0, t1 in data.time_intervals_ms)
            feedback.append(
                f"Tiempo total de apertura: {total_open:.2f} ms de {data.time_range_ms} ms"
            )
        
        if data.is_fast:
            feedback.append(
                "Los canales de Na+ muestran activación rápida seguida de inactivación, "
                "lo que limita la duración de la corriente."
            )
        else:
            feedback.append(
                "Los canales de K+ muestran activación más lenta y sostenida, "
                "sin inactivación significativa durante el estímulo."
            )
        
        return feedback
