# views/pedidos.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.db_manager import DatabaseManager
from utils.validators import DataValidator
from utils.error_handler import handle_exceptions

class Pedidos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.validator = DataValidator()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        # Top frame for new order
        top_frame = ttk.LabelFrame(self, text="Nuevo Pedido")
        top_frame.pack(fill="x", padx=5, pady=5)
        
        # Cliente selector
        ttk.Label(top_frame, text="Cliente:").grid(row=0, column=0, padx=5, pady=5)
        self.cliente_combo = ttk.Combobox(top_frame)
        self.cliente_combo.grid(row=0, column=1, padx=5, pady=5)
        
        # Fecha entrega
        ttk.Label(top_frame, text="Fecha Entrega:").grid(row=0, column=2, padx=5, pady=5)
        self.fecha_entry = ttk.Entry(top_frame)
        self.fecha_entry.grid(row=0, column=3, padx=5, pady=5)
        
        # Orders table
        columns = ("ID", "Cliente", "Fecha Pedido", "Fecha Entrega", "Estado", "Total")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)

    @handle_exceptions("Load orders")
    def load_data(self):
        data = self.db.execute_query("""
            SELECT p.id, c.nombre, p.fecha_pedido, p.fecha_entrega, 
                   p.estado, p.total
            FROM pedidos p
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY p.fecha_pedido DESC
        """)
        self.tree.delete(*self.tree.get_children())
        for row in data:
            self.tree.insert("", "end", values=row)