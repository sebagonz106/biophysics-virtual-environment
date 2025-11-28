"""
Aplicación principal de escritorio.
"""

import customtkinter as ctk
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import APP_NAME, APP_VERSION, WINDOW_SIZE, MIN_WINDOW_SIZE, DATA_DIR
from core.services.solver_service import SolverService
from infrastructure.json_repository import ConferenceRepository, BibliographyRepository, ProblemRepository
from infrastructure.file_manager import FileManager

from .components.sidebar import Sidebar
from .views.home_view import HomeView
from .views.conferences_view import ConferencesView
from .views.bibliography_view import BibliographyView
from .views.problems_view import ProblemsView
from .views.interactive.osmosis_view import OsmosisView
from .views.interactive.patch_clamp_view import PatchClampView


class BiofisicaApp(ctk.CTk):
    """
    Aplicación principal del Entorno Virtual de Biofísica.
    """
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana
        self.title(f"{APP_NAME} v{APP_VERSION}")
        self.geometry(f"{WINDOW_SIZE[0]}x{WINDOW_SIZE[1]}")
        self.minsize(MIN_WINDOW_SIZE[0], MIN_WINDOW_SIZE[1])
        
        # Configurar tema
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Inicializar servicios
        self._init_services()
        
        # Configurar layout
        self._setup_layout()
        
        # Crear componentes
        self._create_widgets()
        
        # Mostrar vista inicial
        self.show_view("home")
    
    def _init_services(self):
        """Inicializa los servicios de la aplicación."""
        self.solver_service = SolverService()
        self.file_manager = FileManager(DATA_DIR)
        
        # Repositorios
        self.conference_repo = ConferenceRepository(DATA_DIR)
        self.bibliography_repo = BibliographyRepository(DATA_DIR)
        self.problem_repo = ProblemRepository(DATA_DIR)
    
    def _setup_layout(self):
        """Configura el layout de la ventana."""
        # Configurar grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
    
    def _create_widgets(self):
        """Crea los widgets de la aplicación."""
        # Sidebar de navegación
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_view
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Frame contenedor principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Diccionario de vistas
        self.views = {}
        self.current_view = None
    
    def show_view(self, view_name: str):
        """
        Muestra una vista específica.
        
        Args:
            view_name: Nombre de la vista a mostrar
        """
        # Ocultar vista actual
        if self.current_view and self.current_view in self.views:
            self.views[self.current_view].grid_forget()
        
        # Crear vista si no existe
        if view_name not in self.views:
            self.views[view_name] = self._create_view(view_name)
        
        # Mostrar nueva vista
        self.views[view_name].grid(row=0, column=0, sticky="nsew")
        self.current_view = view_name
        
        # Actualizar sidebar
        self.sidebar.set_active(view_name)
    
    def _create_view(self, view_name: str) -> ctk.CTkFrame:
        """
        Crea una vista según su nombre.
        
        Args:
            view_name: Nombre de la vista
            
        Returns:
            Frame de la vista
        """
        view_classes = {
            "home": HomeView,
            "conferences": ConferencesView,
            "bibliography": BibliographyView,
            "problems": ProblemsView,
            "osmosis": OsmosisView,
            "patch_clamp": PatchClampView,
        }
        
        if view_name in view_classes:
            return view_classes[view_name](
                self.main_frame,
                app=self
            )
        
        # Vista por defecto si no existe
        return HomeView(self.main_frame, app=self)
    
    def run(self):
        """Inicia la aplicación."""
        self.mainloop()
