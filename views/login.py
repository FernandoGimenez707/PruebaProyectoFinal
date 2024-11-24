import tkinter as tk
from tkinter import ttk, messagebox
from security.auth import AuthManager
from security.session import SessionManager
from utils.error_handler import handle_exceptions

class Login(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.auth_manager = AuthManager()
        self.session_manager = SessionManager()
        self.setup_ui()
    
    def setup_ui(self):
        self.config(bg="#C6D9E3")
        
        # Login frame
        login_frame = ttk.Frame(self)
        login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo or title
        title = ttk.Label(login_frame, text="Sistema de Gestión",
                         font=("Helvetica", 24, "bold"))
        title.pack(pady=20)
        
        # Username
        ttk.Label(login_frame, text="Usuario:").pack(pady=5)
        self.username = ttk.Entry(login_frame, width=30)
        self.username.pack(pady=5)
        
        # Password
        ttk.Label(login_frame, text="Contraseña:").pack(pady=5)
        self.password = ttk.Entry(login_frame, show="*", width=30)
        self.password.pack(pady=5)
        
        # Login button
        ttk.Button(login_frame, text="Ingresar", 
                  command=self.login).pack(pady=20)
    
    @handle_exceptions("Login")
    def login(self):
        username = self.username.get()
        password = self.password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Complete todos los campos")
            return
            
        user = self.auth_manager.authenticate(username, password)
        if user:
            session_id = self.session_manager.create_session(
                user['id'], user['token'])
            self.controller.session_id = session_id
            self.controller.show_frame("Container")
        else:
            messagebox.showerror("Error", "Credenciales inválidas")
            self.password.delete(0, tk.END)
