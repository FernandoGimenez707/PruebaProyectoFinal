import tkinter as tk
from tkinter import ttk
from .inventario import Inventario
from .ventas import Ventas
from .clientes import Clientes
from .pedidos import Pedidos
from .proveedor import Proveedor
from .informacion import Informacion

class Container(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()
        self.setup_frames()
    
    def setup_ui(self):
        # Navigation bar
        nav_frame = ttk.Frame(self)
        nav_frame.pack(fill="x", padx=5, pady=5)
        
        buttons = [
            ("Ventas", Ventas),
            ("Inventario", Inventario),
            ("Clientes", Clientes),
            ("Pedidos", Pedidos),
            ("Proveedor", Proveedor),
            ("Información", Informacion)
        ]
        
        for text, frame_class in buttons:
            ttk.Button(nav_frame, text=text,
                      command=lambda f=frame_class: self.show_frame(f)
                      ).pack(side="left", padx=5)
        
        # Logout button
        ttk.Button(nav_frame, text="Cerrar Sesión",
                  command=self.logout).pack(side="right", padx=5)
        
        # Content frame
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill="both", expand=True)
    
    def setup_frames(self):
        self.frames = {}
        for F in (Ventas, Inventario, Clientes, Pedidos, 
                 Proveedor, Informacion):
            frame = F(self.content_frame)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(Ventas)
    
    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()
    
    def logout(self):
        if hasattr(self.controller, 'session_id'):
            self.controller.session_manager.end_session(
                self.controller.session_id)
        self.controller.show_frame("Login")