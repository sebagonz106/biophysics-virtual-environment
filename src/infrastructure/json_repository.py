"""
Repositorio basado en archivos JSON.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class JsonRepository:
    """
    Repositorio genérico para almacenamiento en archivos JSON.
    
    Proporciona operaciones CRUD básicas sobre archivos JSON,
    con soporte para modelos Pydantic.
    """
    
    def __init__(self, data_dir: Path):
        """
        Inicializa el repositorio.
        
        Args:
            data_dir: Directorio base de datos
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _read_json(self, filepath: Path) -> Any:
        """Lee un archivo JSON."""
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _write_json(self, filepath: Path, data: Any) -> None:
        """Escribe datos a un archivo JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _model_to_dict(self, model: BaseModel) -> Dict:
        """Convierte un modelo Pydantic a diccionario."""
        return model.model_dump()
    
    def _dict_to_model(self, data: Dict, model_class: Type[T]) -> T:
        """Convierte un diccionario a modelo Pydantic."""
        return model_class(**data)


class ConferenceRepository(JsonRepository):
    """Repositorio para conferencias."""
    
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self.conferences_dir = self.data_dir / "conferences"
        self.index_file = self.conferences_dir / "_index.json"
    
    def get_all(self) -> List[Dict]:
        """
        Obtiene todas las conferencias en formato plano.
        
        Transforma la estructura de topics con files en una lista
        plana de conferencias con local_path construido.
        """
        data = self._read_json(self.index_file)
        if not data:
            return []
        
        conferences = []
        topics = data.get("topics", [])
        
        for topic in topics:
            topic_title = topic.get("title", "General")
            folder = topic.get("folder", "")
            topic_order = topic.get("order", 0)
            
            files = topic.get("files", [])
            for i, file_info in enumerate(files):
                # Construir la ruta local al PDF
                filename = file_info.get("filename", "")
                if filename and folder:
                    local_path = f"conferences/pdfs/{folder}/{filename}"
                else:
                    local_path = None
                
                conf = {
                    "id": file_info.get("id", f"{topic.get('id', 'unknown')}-{i}"),
                    "title": file_info.get("title", filename),
                    "description": file_info.get("description", ""),
                    "topic": topic_title,
                    "order": i + 1,
                    "topic_order": topic_order,
                    "local_path": local_path,
                    "filename": filename,
                }
                conferences.append(conf)
        
        return conferences
    
    def get_by_topic(self, topic: str) -> List[Dict]:
        """Obtiene conferencias por tema."""
        all_confs = self.get_all()
        return [c for c in all_confs if c.get("topic") == topic]
    
    def get_by_id(self, conf_id: str) -> Optional[Dict]:
        """Obtiene una conferencia por ID."""
        for conf in self.get_all():
            if conf.get("id") == conf_id:
                return conf
        return None
    
    def save(self, conference: Dict) -> None:
        """Guarda o actualiza una conferencia."""
        # Nota: Esta operación requiere reestructurar de vuelta al formato topics
        # Por ahora solo actualizamos el índice completo
        pass
    
    def get_topics(self) -> List[str]:
        """Obtiene la lista de temas únicos."""
        conferences = self.get_all()
        topics = set(c.get("topic", "") for c in conferences)
        return sorted(topics)


class BibliographyRepository(JsonRepository):
    """Repositorio para bibliografía."""
    
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self.biblio_dir = self.data_dir / "bibliography"
        self.books_file = self.biblio_dir / "books.json"
        self.papers_file = self.biblio_dir / "papers.json"
        self.index_file = self.biblio_dir / "index.json"
    
    def _add_local_path(self, item: Dict) -> Dict:
        """Añade local_path a un item basándose en su filename."""
        if item.get("filename"):
            item["local_path"] = f"bibliography/pdfs/{item['filename']}"
        return item
    
    def get_all_books(self) -> List[Dict]:
        """Obtiene todos los libros."""
        # Intentar primero con index.json
        data = self._read_json(self.index_file)
        if data and "books" in data:
            books = data.get("books", [])
            return [self._add_local_path(book.copy()) for book in books]
        
        # Fallback a books.json
        data = self._read_json(self.books_file)
        if data:
            books = data.get("books", [])
            return [self._add_local_path(book.copy()) for book in books]
        
        return []
    
    def get_all_papers(self) -> List[Dict]:
        """Obtiene todos los artículos."""
        # Intentar primero con index.json
        data = self._read_json(self.index_file)
        if data and "papers" in data:
            papers = data.get("papers", [])
            return [self._add_local_path(paper.copy()) for paper in papers]
        
        # Fallback a papers.json
        data = self._read_json(self.papers_file)
        if data:
            papers = data.get("papers", [])
            return [self._add_local_path(paper.copy()) for paper in papers]
        
        return []
    
    def get_all(self) -> List[Dict]:
        """Obtiene toda la bibliografía."""
        return self.get_all_books() + self.get_all_papers()
    
    def get_by_id(self, item_id: str) -> Optional[Dict]:
        """Obtiene un item bibliográfico por ID."""
        for item in self.get_all():
            if item.get("id") == item_id:
                return item
        return None
    
    def get_by_topic(self, topic: str) -> List[Dict]:
        """Obtiene bibliografía por tema."""
        return [
            item for item in self.get_all()
            if topic in item.get("topics", [])
        ]
    
    def save_book(self, book: Dict) -> None:
        """Guarda o actualiza un libro."""
        books = self.get_all_books()
        
        found = False
        for i, b in enumerate(books):
            if b.get("id") == book.get("id"):
                books[i] = book
                found = True
                break
        
        if not found:
            books.append(book)
        
        self._write_json(self.books_file, {"books": books})
    
    def get_primary_references(self) -> List[Dict]:
        """Obtiene las referencias principales del curso."""
        return [item for item in self.get_all() if item.get("is_primary", False)]


class ProblemRepository(JsonRepository):
    """Repositorio para problemas/ejercicios."""
    
    def __init__(self, data_dir: Path):
        super().__init__(data_dir)
        self.problems_dir = self.data_dir / "problems"
        self.seminars_index = self.problems_dir / "seminars" / "_index.json"
    
    def get_all(self) -> List[Dict]:
        """Obtiene todos los problemas."""
        problems = []
        
        for category_dir in self.problems_dir.iterdir():
            if category_dir.is_dir() and not category_dir.name.startswith("_"):
                for problem_file in category_dir.glob("*.json"):
                    if not problem_file.name.startswith("_"):
                        data = self._read_json(problem_file)
                        if data:
                            problems.append(data)
        
        return problems
    
    def get_all_seminars(self) -> List[Dict]:
        """Obtiene todos los seminarios con sus rutas locales."""
        data = self._read_json(self.seminars_index)
        if not data:
            return []
        
        seminars = []
        for seminar in data.get("seminars", []):
            sem = seminar.copy()
            filename = sem.get("filename", "")
            if filename:
                sem["local_path"] = f"problems/seminars/{filename}"
            seminars.append(sem)
        
        return sorted(seminars, key=lambda x: x.get("order", 0))
    
    def get_by_category(self, category: str) -> List[Dict]:
        """Obtiene problemas por categoría."""
        category_dir = self.problems_dir / category
        problems = []
        
        if category_dir.exists():
            for problem_file in category_dir.glob("*.json"):
                if not problem_file.name.startswith("_"):
                    data = self._read_json(problem_file)
                    if data:
                        problems.append(data)
        
        return problems
    
    def get_by_id(self, problem_id: str) -> Optional[Dict]:
        """Obtiene un problema por ID."""
        for problem in self.get_all():
            if problem.get("id") == problem_id:
                return problem
        return None
    
    def get_by_difficulty(self, difficulty: int) -> List[Dict]:
        """Obtiene problemas por nivel de dificultad."""
        return [p for p in self.get_all() if p.get("difficulty") == difficulty]
    
    def save(self, problem: Dict) -> None:
        """Guarda un problema."""
        category = problem.get("category", "general")
        problem_id = problem.get("id", "unknown")
        
        category_dir = self.problems_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = category_dir / f"{problem_id}.json"
        self._write_json(filepath, problem)
    
    def get_categories(self) -> List[str]:
        """Obtiene las categorías disponibles."""
        categories = []
        
        for item in self.problems_dir.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                categories.append(item.name)
        
        return sorted(categories)
    
    def get_problems_with_solver(self, solver_name: str) -> List[Dict]:
        """Obtiene problemas relacionados con un solver específico."""
        return [
            p for p in self.get_all()
            if p.get("related_solver") == solver_name
        ]
