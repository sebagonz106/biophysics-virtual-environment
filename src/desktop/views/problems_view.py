"""
Vista de problemas propuestos.
"""

import customtkinter as ctk
from tkinter import messagebox


class ProblemsView(ctk.CTkFrame):
    """
    Vista para el módulo de Problemas Propuestos.
    """
    
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app = app
        self.current_problem = None
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self._load_problems()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        self.title = ctk.CTkLabel(
            header_frame,
            text="📝 Problemas Propuestos",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(
            header_frame,
            text="Ejercicios organizados por tema",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, sticky="w")
        
        # Filtros
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.grid(row=0, column=1, rowspan=2, sticky="e")
        
        ctk.CTkLabel(filter_frame, text="Categoría:").grid(row=0, column=0, padx=5)
        self.category_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todas"],
            width=150,
            command=self._on_filter_change
        )
        self.category_filter.grid(row=0, column=1, padx=5)
        
        ctk.CTkLabel(filter_frame, text="Dificultad:").grid(row=0, column=2, padx=(20, 5))
        self.difficulty_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todas", "1 ⭐", "2 ⭐⭐", "3 ⭐⭐⭐", "4 ⭐⭐⭐⭐", "5 ⭐⭐⭐⭐⭐"],
            width=120,
            command=self._on_filter_change
        )
        self.difficulty_filter.grid(row=0, column=3, padx=5)
        
        # Panel principal dividido
        self.main_paned = ctk.CTkFrame(self)
        self.main_paned.grid(row=1, column=0, sticky="nsew")
        self.main_paned.grid_columnconfigure(0, weight=1)
        self.main_paned.grid_columnconfigure(1, weight=2)
        self.main_paned.grid_rowconfigure(0, weight=1)
        
        # Lista de problemas
        self.list_frame = ctk.CTkFrame(self.main_paned)
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_rowconfigure(0, weight=1)
        
        self.problems_scroll = ctk.CTkScrollableFrame(self.list_frame)
        self.problems_scroll.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.problems_scroll.grid_columnconfigure(0, weight=1)
        
        # Detalle del problema
        self.detail_frame = ctk.CTkFrame(self.main_paned)
        self.detail_frame.grid(row=0, column=1, sticky="nsew")
        self.detail_frame.grid_columnconfigure(0, weight=1)
        self.detail_frame.grid_rowconfigure(1, weight=1)
        
        self.detail_title = ctk.CTkLabel(
            self.detail_frame,
            text="Selecciona un problema",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.detail_title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 10))
        
        self.detail_scroll = ctk.CTkScrollableFrame(self.detail_frame)
        self.detail_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.detail_scroll.grid_columnconfigure(0, weight=1)
        
        self.detail_content = ctk.CTkLabel(
            self.detail_scroll,
            text="Haz clic en un problema de la lista para ver su contenido.",
            font=ctk.CTkFont(size=13),
            text_color="gray",
            wraplength=400,
            justify="left"
        )
        self.detail_content.grid(row=0, column=0, pady=20)
    
    def _load_problems(self):
        """Carga los problemas desde el repositorio."""
        if not self.app:
            return
        
        # Obtener categorías
        categories = self.app.problem_repo.get_categories()
        self.category_filter.configure(values=["Todas"] + categories)
        
        # Cargar todos los problemas
        self._display_problems(self.app.problem_repo.get_all())
    
    def _display_problems(self, problems: list):
        """Muestra la lista de problemas."""
        # Limpiar lista actual
        for widget in self.problems_scroll.winfo_children():
            widget.destroy()
        
        if not problems:
            empty_label = ctk.CTkLabel(
                self.problems_scroll,
                text="No hay problemas disponibles",
                text_color="gray"
            )
            empty_label.grid(row=0, column=0, pady=20)
            return
        
        for i, problem in enumerate(problems):
            item = self._create_problem_item(problem)
            item.grid(row=i, column=0, sticky="ew", pady=2)
    
    def _create_problem_item(self, problem: dict):
        """Crea un item de problema para la lista."""
        frame = ctk.CTkFrame(
            self.problems_scroll,
            fg_color=("gray85", "gray25"),
            corner_radius=5,
            height=60,
            cursor="hand2"
        )
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_propagate(False)
        
        # Título
        title = ctk.CTkLabel(
            frame,
            text=problem.get("title", "Sin título")[:45] + ("..." if len(problem.get("title", "")) > 45 else ""),
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 0))
        
        # Info
        difficulty = problem.get("difficulty", 3)
        stars = "⭐" * difficulty
        category = problem.get("category", "general")
        
        info = ctk.CTkLabel(
            frame,
            text=f"{category} | {stars}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        info.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 8))
        
        # Hacer todo el frame clicable
        def on_click(event):
            self._show_problem_detail(problem)
        
        def on_enter(event):
            frame.configure(fg_color=("gray75", "gray35"))
        
        def on_leave(event):
            frame.configure(fg_color=("gray85", "gray25"))
        
        # Vincular eventos a todos los widgets
        for widget in [frame, title, info]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
        
        return frame
    
    def _show_problem_detail(self, problem: dict):
        """Muestra el detalle de un problema."""
        self.current_problem = problem
        
        # Limpiar contenido anterior
        for widget in self.detail_scroll.winfo_children():
            widget.destroy()
        
        # Título
        self.detail_title.configure(text=problem.get("title", "Sin título"))
        
        row = 0
        
        # Metadatos
        meta_frame = ctk.CTkFrame(self.detail_scroll, fg_color=("gray90", "gray20"))
        meta_frame.grid(row=row, column=0, sticky="ew", pady=(0, 15))
        
        difficulty = problem.get("difficulty", 3)
        meta_text = f"Dificultad: {'⭐' * difficulty} | Categoría: {problem.get('category', 'N/A')}"
        if problem.get("tags"):
            meta_text += f" | Tags: {', '.join(problem['tags'][:3])}"
        
        meta_label = ctk.CTkLabel(
            meta_frame,
            text=meta_text,
            font=ctk.CTkFont(size=11)
        )
        meta_label.grid(row=0, column=0, padx=10, pady=8)
        row += 1
        
        # Enunciado
        statement_label = ctk.CTkLabel(
            self.detail_scroll,
            text="📋 Enunciado:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        statement_label.grid(row=row, column=0, sticky="w", pady=(10, 5))
        row += 1
        
        statement = ctk.CTkLabel(
            self.detail_scroll,
            text=problem.get("statement", "No disponible"),
            font=ctk.CTkFont(size=12),
            wraplength=450,
            justify="left"
        )
        statement.grid(row=row, column=0, sticky="w", pady=(0, 15))
        row += 1
        
        # Datos dados
        if problem.get("given_data"):
            data_label = ctk.CTkLabel(
                self.detail_scroll,
                text="📊 Datos proporcionados:",
                font=ctk.CTkFont(size=14, weight="bold")
            )
            data_label.grid(row=row, column=0, sticky="w", pady=(10, 5))
            row += 1
            
            for key, value in problem["given_data"].items():
                if isinstance(value, dict):
                    text = f"• {key}: {value.get('value', '')} {value.get('unit', '')}"
                else:
                    text = f"• {key}: {value}"
                
                data_item = ctk.CTkLabel(
                    self.detail_scroll,
                    text=text,
                    font=ctk.CTkFont(size=11)
                )
                data_item.grid(row=row, column=0, sticky="w", padx=15)
                row += 1
        
        # Botón de mostrar solución
        if problem.get("solution"):
            show_solution_btn = ctk.CTkButton(
                self.detail_scroll,
                text="👁️ Mostrar Solución",
                command=lambda: self._toggle_solution(problem)
            )
            show_solution_btn.grid(row=row, column=0, pady=20)
            row += 1
        
        # Botón de resolver con solver si aplica
        if problem.get("related_solver"):
            solver_btn = ctk.CTkButton(
                self.detail_scroll,
                text="🧮 Resolver con Módulo Interactivo",
                fg_color="green",
                command=lambda: self._open_in_solver(problem)
            )
            solver_btn.grid(row=row, column=0, pady=5)
    
    def _toggle_solution(self, problem: dict):
        """Muestra/oculta la solución del problema."""
        solution = problem.get("solution", {})
        
        # Por simplicidad, mostramos en un mensaje
        if solution:
            steps_text = ""
            for step in solution.get("steps", []):
                steps_text += f"\nPaso {step['step_number']}: {step['description']}\n"
                if step.get("formula"):
                    steps_text += f"   Fórmula: {step['formula']}\n"
                if step.get("calculation"):
                    steps_text += f"   Cálculo: {step['calculation']}\n"
            
            final = solution.get("final_answer", {})
            final_text = f"\n\n✅ Respuesta: {final.get('value', '')} {final.get('unit', '')}"
            
            if solution.get("interpretation"):
                final_text += f"\n\n💡 {solution['interpretation']}"
            
            messagebox.showinfo("Solución", steps_text + final_text)
    
    def _open_in_solver(self, problem: dict):
        """Abre el problema en el solver correspondiente."""
        solver = problem.get("related_solver", "")
        
        if not self.app:
            return
        if "osmol" in solver.lower() or problem.get("category") == "osmosis":
            self.app.show_view("osmosis")
        elif "nernst" in solver.lower() or "patch" in solver.lower():
            self.app.show_view("patch_clamp")
    
    def _on_filter_change(self, *args):
        """Maneja cambios en los filtros."""
        if not self.app:
            return
        
        problems = self.app.problem_repo.get_all()
        
        # Filtrar por categoría
        category = self.category_filter.get()
        if category != "Todas":
            problems = [p for p in problems if p.get("category") == category]
        
        # Filtrar por dificultad
        difficulty = self.difficulty_filter.get()
        if difficulty != "Todas":
            diff_num = int(difficulty[0])
            problems = [p for p in problems if p.get("difficulty") == diff_num]
        
        self._display_problems(problems)
