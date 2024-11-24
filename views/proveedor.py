# views/proveedor.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.db_manager import DatabaseManager
from utils.validators import DataValidator
from utils.error_handler import handle_exceptions

class Proveedor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.validator = DataValidator()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        # Search and filter frame
        filter_frame = ttk.LabelFrame(self, text="Buscar Proveedor")
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_entry = ttk.Entry(filter_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Nuevo Proveedor",
                  command=self.show_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Nueva Compra",
                  command=self.show_purchase_dialog).pack(side="left", padx=5)
        
        # Suppliers table
        columns = ("ID", "Nombre", "Contacto", "Teléfono", "Email", "Dirección")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    @handle_exceptions("Load suppliers")
    def load_data(self):
        data = self.db.execute_query("""
            SELECT id, nombre, contacto, telefono, email, direccion
            FROM proveedores
            ORDER BY nombre
        """)
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row)

    def show_add_dialog(self):
        pass  # Implementar diálogo para agregar proveedor

    def show_purchase_dialog(self):
        pass  # Implementar diálogo para nueva compra