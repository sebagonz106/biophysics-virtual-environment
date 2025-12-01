"""
Configuración global de la aplicación.
"""

from pathlib import Path

# Rutas base
ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
DATA_DIR = ROOT_DIR / "data"
ASSETS_DIR = ROOT_DIR / "assets"
IMG_DIR = DATA_DIR / "img"

# Logo de la aplicación
APP_LOGO = IMG_DIR / "bia_logo.png"
APP_ICON = IMG_DIR / "bia_icon.ico"  # Icono para barra de tareas
APP_LOGO_CROPPED = IMG_DIR / "bia_logo_crop.png"

# Rutas de datos
CONFERENCES_DIR = DATA_DIR / "conferences"
BIBLIOGRAPHY_DIR = DATA_DIR / "bibliography"
PROBLEMS_DIR = DATA_DIR / "problems"
USER_DATA_DIR = DATA_DIR / "user_data"
CONFIG_FILE = DATA_DIR / "config.json"

# Configuración de la aplicación
APP_NAME = "Entorno Virtual de Biofísica"
APP_VERSION = "1.0.0"
WINDOW_SIZE = (1200, 800)
MIN_WINDOW_SIZE = (900, 600)

# Constantes biofísicas
class PhysiologicalConstants:
    """Constantes fisiológicas de referencia."""
    
    # Osmolaridad plasmática (mOsm/L)
    PLASMA_OSMOLARITY = 285
    PLASMA_OSMOLARITY_RANGE = (275, 295)
    
    # Temperatura corporal (K)
    BODY_TEMPERATURE_K = 310  # 37°C
    ROOM_TEMPERATURE_K = 298  # 25°C
    
    # Constantes físicas
    GAS_CONSTANT = 8.314  # J/(mol·K)
    FARADAY_CONSTANT = 96485  # C/mol
    
    # Concentraciones iónicas típicas (mM)
    IONIC_CONCENTRATIONS = {
        "K+": {"intracelular": 140, "extracelular": 5},
        "Na+": {"intracelular": 12, "extracelular": 145},
        "Cl-": {"intracelular": 4, "extracelular": 120},
        "Ca2+": {"intracelular": 0.0001, "extracelular": 2.5},
    }


# Temas de la aplicación
class AppTheme:
    """Configuración de colores y estilos."""
    
    # Colores principales
    PRIMARY_COLOR = "#1f538d"
    SECONDARY_COLOR = "#14375e"
    ACCENT_COLOR = "#3a7ebf"
    
    # Colores de estado
    SUCCESS_COLOR = "#2d8a4e"
    WARNING_COLOR = "#c4a000"
    ERROR_COLOR = "#c62828"
    
    # Colores de fondo
    BG_LIGHT = "#f5f5f5"
    BG_DARK = "#1a1a2e"
    
    # Tipografía
    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_SMALL = 11
    FONT_SIZE_NORMAL = 13
    FONT_SIZE_LARGE = 16
    FONT_SIZE_TITLE = 20
