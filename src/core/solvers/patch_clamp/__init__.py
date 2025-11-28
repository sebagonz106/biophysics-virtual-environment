"""
Módulo de Patch Clamp - Cálculos electrofisiológicos.
"""

from .nernst import NernstSolver
from .goldman import GoldmanHodgkinKatzSolver
from .iv_curve import IVCurveSolver

__all__ = [
    "NernstSolver",
    "GoldmanHodgkinKatzSolver",
    "IVCurveSolver",
]
