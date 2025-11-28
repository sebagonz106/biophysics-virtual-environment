"""
Gestor de archivos para la aplicación.
"""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional, List


class FileManager:
    """
    Gestor de archivos para operaciones comunes.
    
    Proporciona métodos para abrir PDFs, gestionar rutas
    y operaciones de archivo.
    """
    
    def __init__(self, data_dir: Path):
        """
        Inicializa el gestor de archivos.
        
        Args:
            data_dir: Directorio base de datos
        """
        self.data_dir = Path(data_dir)
    
    def open_file(self, relative_path: str) -> bool:
        """
        Abre un archivo con la aplicación predeterminada del sistema.
        
        Args:
            relative_path: Ruta relativa al directorio de datos
            
        Returns:
            True si se abrió correctamente
        """
        full_path = self.data_dir / relative_path
        
        if not full_path.exists():
            print(f"Archivo no encontrado: {full_path}")
            return False
        
        return self._open_with_default_app(full_path)
    
    def open_pdf(self, relative_path: str) -> bool:
        """
        Abre un archivo PDF.
        
        Args:
            relative_path: Ruta relativa al PDF
            
        Returns:
            True si se abrió correctamente
        """
        return self.open_file(relative_path)
    
    def _open_with_default_app(self, path: Path) -> bool:
        """
        Abre un archivo con la aplicación predeterminada del SO.
        
        Args:
            path: Ruta absoluta al archivo
            
        Returns:
            True si se abrió correctamente
        """
        try:
            system = platform.system()
            
            if system == "Windows":
                os.startfile(str(path))
            elif system == "Darwin":  # macOS
                subprocess.run(["open", str(path)], check=True)
            else:  # Linux y otros
                subprocess.run(["xdg-open", str(path)], check=True)
            
            return True
        except Exception as e:
            print(f"Error al abrir archivo: {e}")
            return False
    
    def get_absolute_path(self, relative_path: str) -> Path:
        """
        Convierte una ruta relativa a absoluta.
        
        Args:
            relative_path: Ruta relativa al directorio de datos
            
        Returns:
            Ruta absoluta
        """
        return self.data_dir / relative_path
    
    def file_exists(self, relative_path: str) -> bool:
        """
        Verifica si un archivo existe.
        
        Args:
            relative_path: Ruta relativa al archivo
            
        Returns:
            True si existe
        """
        return (self.data_dir / relative_path).exists()
    
    def list_pdfs(self, directory: str) -> List[Path]:
        """
        Lista todos los PDFs en un directorio.
        
        Args:
            directory: Ruta relativa al directorio
            
        Returns:
            Lista de rutas a archivos PDF
        """
        dir_path = self.data_dir / directory
        
        if not dir_path.exists():
            return []
        
        return list(dir_path.glob("**/*.pdf"))
    
    def get_pdf_info(self, relative_path: str) -> Optional[dict]:
        """
        Obtiene información básica de un PDF.
        
        Args:
            relative_path: Ruta relativa al PDF
            
        Returns:
            Diccionario con información del archivo
        """
        full_path = self.data_dir / relative_path
        
        if not full_path.exists():
            return None
        
        stat = full_path.stat()
        
        return {
            "name": full_path.name,
            "path": str(relative_path),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": stat.st_mtime,
        }
    
    def ensure_directory(self, relative_path: str) -> Path:
        """
        Asegura que un directorio existe, creándolo si es necesario.
        
        Args:
            relative_path: Ruta relativa al directorio
            
        Returns:
            Ruta absoluta al directorio
        """
        dir_path = self.data_dir / relative_path
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    def get_conferences_pdfs(self) -> List[Path]:
        """Obtiene todos los PDFs de conferencias."""
        return self.list_pdfs("conferences/pdfs")
    
    def get_bibliography_pdfs(self) -> List[Path]:
        """Obtiene todos los PDFs de bibliografía."""
        return self.list_pdfs("bibliography/pdfs")
