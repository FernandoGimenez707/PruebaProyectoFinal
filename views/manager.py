from tkinter import Tk
from tkinter import ttk
from .login import Login
from .container import Container
import pathlib

class Manager(Tk):
    def __init__(self):
        super().__init__()
        self.setup_directories()
        self.setup_gui()
        self.setup_frames()
        
    def setup_directories(self):
        for dir_name in ['logs', 'fotos', 'facturas', 'reportes']:
            pathlib.Path(dir_name).mkdir(exist_ok=True)
            
    def setup_gui(self):
        self.title("Sistema de Gestión v2.0")
        self.geometry("1100x650+120+10")
        self.resizable(False, False)
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
    def setup_frames(self):
        self.frames = {}
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        for F in (Login, Container):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(Login)
        
    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()