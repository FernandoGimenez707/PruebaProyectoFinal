# views/clientes.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.db_manager import DatabaseManager
from utils.validators import DataValidator

class Clientes(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.validator = DataValidator()
        self.setup_ui()
    
    def setup_ui(self):
        # Search frame
        search_frame = ttk.LabelFrame(self, text="Buscar Cliente")
        search_frame.pack(fill="x", padx=5, pady=5)
        
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_clients)
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Nuevo Cliente",
                  command=self.show_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Editar",
                  command=self.show_edit_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Eliminar",
                  command=self.delete_client).pack(side="left", padx=5)
        
        # Clients table
        columns = ("ID", "Nombre", "Teléfono", "Email", "Dirección")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
    
    def search_clients(self, event):
        search_term = self.search_entry.get()
        # Aquí puedes agregar la lógica para buscar clientes basado en el término de búsqueda
        # Por ejemplo, puedes consultar la base de datos o filtrar los clientes existentes
        # y actualizar la tabla de clientes con los resultados de la búsqueda
        print(f"Buscando clientes con el término: {search_term}")
    
    def show_add_dialog(self):
        # Aquí puedes agregar la lógica para mostrar el diálogo de agregar un nuevo cliente
        print("Mostrando diálogo para agregar un nuevo cliente")
    
    def show_edit_dialog(self):
        # Aquí puedes agregar la lógica para mostrar el diálogo de editar un cliente existente
        print("Mostrando diálogo para editar un cliente")
    
    def delete_client(self):
        # Aquí puedes agregar la lógica para eliminar un cliente existente
        print("Eliminando un cliente")
    
    def load_clients(self):
        # Aquí puedes agregar la lógica para cargar los clientes desde la base de datos
        # y mostrarlos en la tabla de clientes (self.tree)
        print("Cargando clientes desde la base de datos")
    
    def save_client(self, client_data):
        # Aquí puedes agregar la lógica para guardar un nuevo cliente o actualizar uno existente
        # utilizando los datos proporcionados en client_data
        print(f"Guardando cliente: {client_data}")
    
    def get_selected_client(self):
        # Aquí puedes agregar la lógica para obtener los datos del cliente seleccionado en la tabla
        # y devolverlos para su uso en otras funciones (por ejemplo, para editar o eliminar)
        print("Obteniendo cliente seleccionado")
        return None