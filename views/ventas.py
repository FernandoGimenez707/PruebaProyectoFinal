
# views/ventas.py
import tkinter as tk
from tkinter import ttk, messagebox
from utils.db_manager import DatabaseManager
from utils.validators import DataValidator
from utils.error_handler import handle_exceptions
from decimal import Decimal, InvalidOperation
from datetime import datetime
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class Ventas(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = DatabaseManager()
        self.validator = DataValidator()
        self.productos_seleccionados = []
        self.precio_actual = Decimal('0.0')
        self.stock_actual = 0
        
        # Inicializar UI
        self.setup_ui()
        self.cargar_productos()
        self.cargar_numero_factura()
        
        # Configurar estilos de la factura
        self.setup_factura_styles()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        self.setup_top_frame()
        self.setup_table_frame()
        self.setup_bottom_frame()
    
    def setup_top_frame(self):
        """Configura el frame superior con los datos de venta"""
        top_frame = ttk.LabelFrame(self, text="Datos de Venta")
        top_frame.pack(fill="x", padx=10, pady=5)
        
        # Frame para cliente
        cliente_frame = ttk.Frame(top_frame)
        cliente_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(cliente_frame, text="Cliente:").pack(side="left")
        self.cliente_entry = ttk.Entry(cliente_frame, width=40)
        self.cliente_entry.pack(side="left", padx=5)
        
        # Frame para producto
        producto_frame = ttk.Frame(top_frame)
        producto_frame.pack(fill="x", padx=5, pady=5)
        
        # Producto
        ttk.Label(producto_frame, text="Producto:").pack(side="left")
        self.producto_combo = ttk.Combobox(producto_frame, width=40)
        self.producto_combo.pack(side="left", padx=5)
        self.producto_combo.bind('<<ComboboxSelected>>', self.actualizar_precio)
        
        # Precio y Stock
        precio_stock_frame = ttk.Frame(producto_frame)
        precio_stock_frame.pack(side="left", padx=20)
        
        self.precio_label = ttk.Label(precio_stock_frame, text="Precio: $0.00")
        self.precio_label.pack(side="left", padx=5)
        
        self.stock_label = ttk.Label(precio_stock_frame, text="Stock: 0")
        self.stock_label.pack(side="left", padx=5)
        
        # Cantidad y Botón Agregar
        cantidad_frame = ttk.Frame(top_frame)
        cantidad_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(cantidad_frame, text="Cantidad:").pack(side="left")
        self.cantidad_entry = ttk.Entry(cantidad_frame, width=10)
        self.cantidad_entry.pack(side="left", padx=5)
        
        ttk.Button(cantidad_frame, text="Agregar", 
                  command=self.agregar_producto).pack(side="left", padx=20)
    
    def setup_table_frame(self):
        """Configura la tabla de productos"""
        table_frame = ttk.LabelFrame(self, text="Productos Seleccionados")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Tabla
        columns = ("Producto", "Cantidad", "Precio Unit.", "Subtotal")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        
        # Configurar columnas
        self.tree.column("Producto", width=200)
        self.tree.column("Cantidad", width=100, anchor="center")
        self.tree.column("Precio Unit.", width=100, anchor="e")
        self.tree.column("Subtotal", width=100, anchor="e")
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Botón para eliminar item
        ttk.Button(table_frame, text="Eliminar Item",
                  command=self.eliminar_item).pack(side="bottom", pady=5)
    
    def setup_bottom_frame(self):
        """Configura el frame inferior con totales y botones de acción"""
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        
        # Totales
        self.total_label = ttk.Label(bottom_frame, 
                                   text="Total: $0.00",
                                   font=("Helvetica", 12, "bold"))
        self.total_label.pack(side="right", padx=10)
        
        # Botones
        ttk.Button(bottom_frame, text="Procesar Venta",
                  command=self.procesar_venta).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Cancelar",
                  command=self.limpiar_venta).pack(side="left", padx=5)

    @handle_exceptions("Cargar productos")
    def cargar_productos(self):
        """Carga los productos disponibles en el combobox"""
        data = self.db.execute_query(
            "SELECT articulo FROM articulos WHERE estado = 'Activo' AND stock > 0"
        )
        self.producto_combo['values'] = [row['articulo'] for row in data]

    @handle_exceptions("Cargar número de factura")
    def cargar_numero_factura(self):
        """Obtiene el siguiente número de factura"""
        result = self.db.execute_query("SELECT MAX(factura) as ultima FROM ventas")
        self.numero_factura = (result[0]['ultima'] or 0) + 1

    @handle_exceptions("Actualizar precio")
    def actualizar_precio(self, event=None):
        producto = self.producto_combo.get()
        if producto:
            data = self.db.execute_query(
                "SELECT precio, stock FROM articulos WHERE articulo = ?",
                (producto,)
            )
            if data:
                self.precio_actual = Decimal(str(data[0]['precio']))
                self.stock_actual = data[0]['stock']
                self.precio_label.config(text=f"Precio: ${self.precio_actual:,.2f}")
                self.stock_label.config(text=f"Stock: {self.stock_actual}")
                self.cantidad_entry.focus()
            else:
                self.precio_actual = Decimal('0.0')
                self.stock_actual = 0
                self.precio_label.config(text="Precio: $0.00")
                self.stock_label.config(text="Stock: 0")

    @handle_exceptions("Agregar producto")
    def agregar_producto(self):
        producto = self.producto_combo.get()
        cantidad = self.cantidad_entry.get()
        
        if not producto or not cantidad:
            messagebox.showerror("Error", "Complete todos los campos")
            return
            
        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError("La cantidad debe ser positiva")
            
            if cantidad > self.stock_actual:
                messagebox.showerror("Error", f"Stock insuficiente. Disponible: {self.stock_actual}")
                return
                
            subtotal = self.precio_actual * cantidad
            
            self.tree.insert("", "end", values=(
                producto,
                cantidad,
                f"${self.precio_actual:,.2f}",
                f"${subtotal:,.2f}"
            ))
            
            self.productos_seleccionados.append({
                'nombre': producto,
                'cantidad': cantidad,
                'precio': self.precio_actual,
                'subtotal': subtotal
            })
            
            self.actualizar_total()
            self.limpiar_campos()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def actualizar_total(self):
        """Actualiza el total de la venta"""
        total = sum(item['subtotal'] for item in self.productos_seleccionados)
        self.total_label.config(text=f"Total: ${total:,.2f}")

    def limpiar_campos(self):
        """Limpia los campos de entrada"""
        self.producto_combo.set('')
        self.cantidad_entry.delete(0, 'end')
        self.precio_label.config(text="Precio: $0.00")
        self.stock_label.config(text="Stock: 0")
        self.producto_combo.focus()

    def limpiar_venta(self):
        """Limpia toda la venta actual"""
        self.tree.delete(*self.tree.get_children())
        self.productos_seleccionados = []
        self.actualizar_total()
        self.limpiar_campos()
        self.cliente_entry.delete(0, 'end')
        self.cliente_entry.focus()

    @handle_exceptions("Eliminar item")
    def eliminar_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un item para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Desea eliminar el item seleccionado?"):
            index = self.tree.index(selected[0])
            self.tree.delete(selected[0])
            self.productos_seleccionados.pop(index)
            self.actualizar_total()

    @handle_exceptions("Procesar venta")
    def procesar_venta(self):
        """Inicia el proceso de venta"""
        if not self.productos_seleccionados:
            messagebox.showerror("Error", "No hay productos seleccionados")
            return
        
        if not self.cliente_entry.get():
            messagebox.showerror("Error", "Debe especificar un cliente")
            return
        
        total = sum(item['subtotal'] for item in self.productos_seleccionados)
        self.mostrar_dialogo_pago(total)

    def mostrar_dialogo_pago(self, total):
        """Muestra el diálogo de pago"""
        dialog = tk.Toplevel(self)
        dialog.title("Procesar Pago")
        dialog.geometry("400x300")
        dialog.transient(self)
        dialog.grab_set()
        
        # Centrar en la pantalla
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'+{x}+{y}')
        
        # Contenido
        ttk.Label(dialog, 
                 text=f"Total a pagar: ${total:,.2f}",
                 font=("Helvetica", 14, "bold")).pack(pady=20)
        
        frame = ttk.Frame(dialog)
        frame.pack(pady=20)
        
        ttk.Label(frame, text="Monto recibido: $").pack(side="left")
        monto_entry = ttk.Entry(frame, width=15)
        monto_entry.pack(side="left")
        monto_entry.focus()
        
        def confirmar():
            try:
                monto = Decimal(monto_entry.get())
                if monto < total:
                    messagebox.showerror("Error", "Monto insuficiente")
                    return
                
                cambio = monto - total
                if self.procesar_venta_db(monto, cambio):
                    dialog.destroy()
                    
            except (ValueError, InvalidOperation):
                messagebox.showerror("Error", "Ingrese un monto válido")
        
        ttk.Button(dialog, text="Confirmar", 
                  command=confirmar).pack(pady=10)
        ttk.Button(dialog, text="Cancelar",
                  command=dialog.destroy).pack()
        
        # Binding para Enter
        monto_entry.bind('<Return>', lambda e: confirmar())
        
        # Esperar a que se cierre el diálogo
        dialog.wait_window()

    @handle_exceptions("Procesar venta en DB")
    def procesar_venta_db(self, monto_recibido, cambio):
        """Procesa la venta en la base de datos"""
        fecha = datetime.now().date()
        hora = datetime.now().time()
        
        for producto in self.productos_seleccionados:
            # Registrar venta
            self.db.insert('ventas', {
                'factura': self.numero_factura,
                'cliente': self.cliente_entry.get(),
                'articulo': producto['nombre'],
                'cantidad': producto['cantidad'],
                'precio': producto['precio'],
                'total': producto['subtotal'],
                'fecha': fecha,
                'hora': hora
            })
            
            # Actualizar stock
            self.db.execute_query(
                """UPDATE articulos 
                   SET stock = stock - ? 
                   WHERE articulo = ?""",
                (producto['cantidad'], producto['nombre'])
            )
        
        messagebox.showinfo("Éxito", 
            f"Venta procesada correctamente\n"
            f"Monto recibido: ${monto_recibido:,.2f}\n"
            f"Cambio: ${cambio:,.2f}")
        
        self.generar_factura()
        self.limpiar_venta()
        self.cargar_numero_factura()
        self.cargar_productos()
        return True

    def setup_factura_styles(self):
        """Configura los estilos para la factura PDF"""
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(
            name='Centered',
            parent=self.styles['Normal'],
            alignment=1,
            spaceAfter=20
        ))
        
        self.styles.add(ParagraphStyle(
            name='RightAligned',
            parent=self.styles['Normal'],
            alignment=2,
            spaceAfter=20
        ))

    @handle_exceptions("Generar factura")
    def generar_factura(self):
        """Genera la factura en PDF"""
        # Crear directorio si no existe
        os.makedirs('facturas', exist_ok=True)