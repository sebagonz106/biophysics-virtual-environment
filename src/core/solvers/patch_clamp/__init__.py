"""
Módulo de Patch Clamp - Cálculos electrofisiológicos.
"""

from .nernst import NernstSolver
from .goldman import GoldmanHodgkinKatzSolver
from .iv_curve import IVCurveSolver
from .single_channel import SingleChannelSolver

__all__ = [
    "NernstSolver",
    "GoldmanHodgkinKatzSolver",
    "IVCurveSolver",
    "SingleChannelSolver",
]
