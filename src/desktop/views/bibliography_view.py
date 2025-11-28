"""
Vista de bibliografía recomendada.
"""

import customtkinter as ctk
from tkinter import messagebox


class BibliographyView(ctk.CTkFrame):
    """
    Vista para el módulo de Bibliografía Recomendada.
    """
    
    def __init__(self, master, app=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.app = app
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._create_widgets()
        self._load_bibliography()
    
    def _create_widgets(self):
        """Crea los widgets de la vista."""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        
        self.title = ctk.CTkLabel(
            header_frame,
            text="📚 Bibliografía Recomendada",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title.grid(row=0, column=0, sticky="w")
        
        self.subtitle = ctk.CTkLabel(
            header_frame,
            text="Referencias bibliográficas del curso",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.subtitle.grid(row=1, column=0, sticky="w")
        
        # Tabs para tipo de recurso
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew")
        
        self.tab_books = self.tabview.add("📕 Libros")
        self.tab_papers = self.tabview.add("📄 Artículos")
        
        # Configurar tabs
        for tab in [self.tab_books, self.tab_papers]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)
        
        # ScrollFrames para cada tab
        self.books_scroll = ctk.CTkScrollableFrame(self.tab_books)
        self.books_scroll.grid(row=0, column=0, sticky="nsew")
        self.books_scroll.grid_columnconfigure(0, weight=1)
        
        self.papers_scroll = ctk.CTkScrollableFrame(self.tab_papers)
        self.papers_scroll.grid(row=0, column=0, sticky="nsew")
        self.papers_scroll.grid_columnconfigure(0, weight=1)
    
    def _load_bibliography(self):
        """Carga la bibliografía desde el repositorio."""
        if not self.app:
            self._show_empty_message(self.books_scroll, "libros")
            self._show_empty_message(self.papers_scroll, "artículos")
            return
        
        # Cargar libros
        books = self.app.bibliography_repo.get_all_books()
        if books:
            for i, book in enumerate(books):
                card = self._create_book_card(book)
                card.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
        else:
            self._show_empty_message(self.books_scroll, "libros")
        
        # Cargar artículos
        papers = self.app.bibliography_repo.get_all_papers()
        if papers:
            for i, paper in enumerate(papers):
                card = self._create_paper_card(paper)
                card.grid(row=i, column=0, sticky="ew", pady=5, padx=5)
        else:
            self._show_empty_message(self.papers_scroll, "artículos")
    
    def _show_empty_message(self, parent, item_type: str):
        """Muestra mensaje cuando no hay items."""
        label = ctk.CTkLabel(
            parent,
            text=f"📂 No hay {item_type} disponibles\n\nEdite data/bibliography/ para agregar {item_type}",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            justify="center"
        )
        label.grid(row=0, column=0, pady=50)
    
    def _create_book_card(self, book: dict) -> ctk.CTkFrame:
        """Crea una tarjeta para un libro."""
        card = ctk.CTkFrame(self.books_scroll)
        card.grid_columnconfigure(0, weight=1)
        
        # Header con indicador de primario
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header.grid_columnconfigure(0, weight=1)
        
        title_text = book.get("title", "Sin título")
        if book.get("is_primary"):
            title_text = "⭐ " + title_text
        
        title = ctk.CTkLabel(
            header,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            wraplength=500
        )
        title.grid(row=0, column=0, sticky="w")
        
        # Autores
        authors = ", ".join(book.get("authors", []))
        authors_label = ctk.CTkLabel(
            card,
            text=authors,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        authors_label.grid(row=1, column=0, sticky="w", padx=15)
        
        # Info adicional
        info_parts = []
        if book.get("edition"):
            info_parts.append(f"Ed. {book['edition']}")
        if book.get("year"):
            info_parts.append(str(book["year"]))
        if book.get("publisher"):
            info_parts.append(book["publisher"])
        
        if info_parts:
            info_label = ctk.CTkLabel(
                card,
                text=" | ".join(info_parts),
                font=ctk.CTkFont(size=11),
                text_color="gray"
            )
            info_label.grid(row=2, column=0, sticky="w", padx=15, pady=(2, 0))
        
        # Botón de abrir PDF si existe
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="w", padx=15, pady=(10, 15))
        
        if book.get("local_path"):
            open_btn = ctk.CTkButton(
                btn_frame,
                text="📄 Abrir PDF",
                width=100,
                height=28,
                command=lambda: self._open_pdf(book)
            )
            open_btn.grid(row=0, column=0)
        
        return card
    
    def _create_paper_card(self, paper: dict) -> ctk.CTkFrame:
        """Crea una tarjeta para un artículo."""
        card = ctk.CTkFrame(self.papers_scroll)
        card.grid_columnconfigure(0, weight=1)
        
        # Título
        title = ctk.CTkLabel(
            card,
            text=paper.get("title", "Sin título"),
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            wraplength=500
        )
        title.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        # Autores
        authors = ", ".join(paper.get("authors", []))
        authors_label = ctk.CTkLabel(
            card,
            text=authors,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        authors_label.grid(row=1, column=0, sticky="w", padx=15)
        
        # Journal info
        journal_parts = []
        if paper.get("journal"):
            journal_parts.append(paper["journal"])
        if paper.get("volume"):
            journal_parts.append(f"Vol. {paper['volume']}")
        if paper.get("year"):
            journal_parts.append(f"({paper['year']})")
        
        if journal_parts:
            journal_label = ctk.CTkLabel(
                card,
                text=" ".join(journal_parts),
                font=ctk.CTkFont(size=11, slant="italic"),
                text_color="gray"
            )
            journal_label.grid(row=2, column=0, sticky="w", padx=15, pady=(2, 15))
        
        return card
    
    def _open_pdf(self, item: dict):
        """Abre un archivo PDF."""
        if self.app and item.get("local_path"):
            success = self.app.file_manager.open_pdf(item["local_path"])
            if not success:
                messagebox.showerror(
                    "Error",
                    f"No se pudo abrir el archivo:\n{item['local_path']}"
                )
