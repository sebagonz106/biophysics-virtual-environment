"""
Módulo de Ósmosis - Cálculos relacionados con ósmosis y tonicidad.
"""

from .osmolarity import OsmolaritySolver
from .osmolarity_comparison import OsmolarityComparisonSolver
from .tonicity import TonicityClassifier
from .cell_volume import CellVolumeSolver
from .volume_dynamics import (
    VolumeDynamicsSimulator,
    VolumeDynamicsParams,
    VolumeDynamicsResult,
    simulate_volume_dynamics,
    simulate_lysis_dynamics,
)

__all__ = [
    "OsmolaritySolver",
    "OsmolarityComparisonSolver",
    "TonicityClassifier",
    "CellVolumeSolver",
    "VolumeDynamicsSimulator",
    "VolumeDynamicsParams",
    "VolumeDynamicsResult",
    "simulate_volume_dynamics",
    "simulate_lysis_dynamics",
]
