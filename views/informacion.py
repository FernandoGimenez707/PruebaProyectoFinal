# views/informacion.py
import tkinter as tk
from tkinter import ttk
from utils.db_manager import DatabaseManager
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Informacion(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.setup_ui()
    
    def setup_ui(self):
        # Statistics frame
        stats_frame = ttk.LabelFrame(self, text="Estadísticas Generales")
        stats_frame.pack(fill="x", padx=5, pady=5)
        
        self.stats_labels = {}
        stats = ["Ventas del día", "Ventas del mes", "Productos más vendidos"]
        for stat in stats:
            self.stats_labels[stat] = ttk.Label(stats_frame, text=f"{stat}: Cargando...")
            self.stats_labels[stat].pack(padx=5, pady=2)
        
        # Charts frame
        charts_frame = ttk.LabelFrame(self, text="Gráficos")
        charts_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create figure for matplotlib
        self.figure = Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=charts_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Load initial data
        self.load_data()
    
    def load_data(self):
        # Load and update statistics
        stats_data = self.get_stats_data()
        for stat, value in stats_data.items():
            self.stats_labels[stat].config(text=f"{stat}: {value}")
        
        # Load and update charts
        charts_data = self.get_charts_data()
        self.update_charts(charts_data)
    
    def get_stats_data(self):
        # Retrieve statistics data from the database
        stats_data = {
            "Ventas del día": self.db.get_daily_sales(),
            "Ventas del mes": self.db.get_monthly_sales(),
            "Productos más vendidos": self.db.get_top_selling_products()
        }
        return stats_data
    
    def get_charts_data(self):
        # Retrieve charts data from the database
        charts_data = {
            "sales_by_category": self.db.get_sales_by_category(),
            "sales_by_month": self.db.get_sales_by_month()
        }
        return charts_data
    
    def update_charts(self, charts_data):
        # Clear existing charts
        self.figure.clear()
        
        # Create sales by category chart
        ax1 = self.figure.add_subplot(2, 1, 1)
        categories = [data[0] for data in charts_data["sales_by_category"]]
        sales = [data[1] for data in charts_data["sales_by_category"]]
        ax1.bar(categories, sales)
        ax1.set_title("Ventas por Categoría")
        ax1.set_xlabel("Categoría")
        ax1.set_ylabel("Ventas")
        
        # Create sales by month chart
        ax2 = self.figure.add_subplot(2, 1, 2)
        months = [data[0] for data in charts_data["sales_by_month"]]
        sales = [data[1] for data in charts_data["sales_by_month"]]
        ax2.plot(months, sales)
        ax2.set_title("Ventas por Mes")
        ax2.set_xlabel("Mes")
        ax2.set_ylabel("Ventas")
        
        # Refresh canvas
        self.canvas.draw()