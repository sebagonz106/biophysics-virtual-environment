"""
Punto de entrada principal de la aplicación.
Entorno Virtual para la Enseñanza de la Biofísica
"""

import sys
from pathlib import Path

# Asegurar que el directorio src está en el path
src_dir = Path(__file__).resolve().parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from config import APP_NAME, APP_VERSION, DATA_DIR
from desktop.app import BiofisicaApp


def ensure_data_directories():
    """Crea los directorios de datos si no existen."""
    directories = [
        DATA_DIR / "conferences" / "pdfs",
        DATA_DIR / "bibliography" / "pdfs",
        DATA_DIR / "problems" / "osmosis",
        DATA_DIR / "problems" / "patch_clamp",
        DATA_DIR / "user_data",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def main():
    """Función principal que inicia la aplicación."""
    print(f"Iniciando {APP_NAME} v{APP_VERSION}...")
    
    # Asegurar que existen los directorios necesarios
    ensure_data_directories()
    
    # Crear e iniciar la aplicación
    app = BiofisicaApp()
    app.run()


if __name__ == "__main__":
    main()
