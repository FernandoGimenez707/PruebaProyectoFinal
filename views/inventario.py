# views/inventario.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from utils.db_manager import DatabaseManager
from utils.validators import DataValidator
from utils.error_handler import handle_exceptions
import os
import secrets

class Inventario(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = DatabaseManager()
        self.validator = DataValidator()
        self.image_folder = "fotos"
        os.makedirs(self.image_folder, exist_ok=True)
        
        # Definir variables de clase
        self.search_var = tk.StringVar()
        self.image_path = None
        self.image_preview = None
        
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Configurar la interfaz de usuario"""
        # Panel principal dividido en dos
        self.panel_izquierdo = ttk.Frame(self)
        self.panel_izquierdo.pack(side="left", fill="y", padx=5, pady=5)
        
        self.panel_derecho = ttk.Frame(self)
        self.panel_derecho.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Panel izquierdo - Búsqueda y acciones
        self.setup_search_panel()
        self.setup_actions_panel()
        
        # Panel derecho - Tabla de productos
        self.setup_products_table()
    def setup_search_panel(self):
        """Configurar panel de búsqueda"""
        search_frame = ttk.LabelFrame(self.panel_izquierdo, text="Búsqueda")
        search_frame.pack(fill="x", pady=5)
        
        # Combobox para búsqueda
        self.search_combo = ttk.Combobox(search_frame, textvariable=self.search_var)
        self.search_combo.pack(fill="x", padx=5, pady=5)
        self.search_combo.bind('<KeyRelease>', self.filter_products)
    
    def setup_actions_panel(self):
        """Configurar panel de acciones"""
        actions_frame = ttk.LabelFrame(self.panel_izquierdo, text="Acciones")
        actions_frame.pack(fill="x", pady=5)
        
        # Botones de acción
        ttk.Button(actions_frame, text="Agregar Artículo",
                  command=self.show_add_dialog).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(actions_frame, text="Editar Artículo",
                  command=self.show_edit_dialog).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(actions_frame, text="Eliminar Artículo",
                  command=self.delete_product).pack(fill="x", padx=5, pady=2)
        
        ttk.Button(actions_frame, text="Actualizar Stock",
                  command=self.show_stock_dialog).pack(fill="x", padx=5, pady=2)

    def setup_products_table(self):
        # Frame para la tabla
        table_frame = ttk.Frame(self.panel_derecho)
        table_frame.pack(fill="both", expand=True)
        
        # Definir columnas
        columns = ("ID", "Artículo", "Descripción", "Precio", "Costo", "Stock", "Estado")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        # Configurar columnas
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(c))
            # Ajustar anchos según el tipo de dato
            if col in ["ID", "Stock"]:
                self.tree.column(col, width=70, anchor="center")
            elif col in ["Precio", "Costo"]:
                self.tree.column(col, width=100, anchor="e")
            else:
                self.tree.column(col, width=150)
        
        # Scrollbars
        yscroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        xscroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        
        # Pack elementos
        self.tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        xscroll.pack(side="bottom", fill="x")
        
        # Binding para doble click
        self.tree.bind("<Double-1>", lambda e: self.show_edit_dialog())
    def filter_products(self, event=None):
        """Filtrar productos en la tabla según búsqueda"""
        search_term = self.search_var.get().lower()
        
        try:
            # Obtener productos que coincidan con la búsqueda
            query = """
                SELECT id, articulo, descripcion, precio, costo, stock, estado
                FROM articulos 
                WHERE articulo LIKE ? OR descripcion LIKE ?
                ORDER BY articulo
            """
            search_pattern = f"%{search_term}%"
            data = self.db.execute_query(query, (search_pattern, search_pattern))
            
            # Limpiar tabla
            self.tree.delete(*self.tree.get_children())
            
            # Mostrar resultados filtrados
            if data:
                for row in data:
                    self.tree.insert("", "end", values=(
                        row['id'],
                        row['articulo'],
                        row['descripcion'] or '',
                        f"${float(row['precio']):,.2f}",
                        f"${float(row['costo']):,.2f}",
                        row['stock'],
                        row['estado']
                    ))
            
            # Actualizar valores del combobox
            if search_term:
                matching_products = [row['articulo'] for row in data]
                self.search_combo['values'] = matching_products or ['No se encontraron resultados']
            else:
                # Si no hay término de búsqueda, mostrar todos los productos
                all_products = self.db.execute_query("SELECT articulo FROM articulos ORDER BY articulo")
                self.search_combo['values'] = [row['articulo'] for row in all_products]
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al filtrar productos: {str(e)}")

    @handle_exceptions("Cargar inventario")
    def load_data(self):
        """Cargar datos del inventario desde la base de datos"""
        query = """
            SELECT id, articulo, descripcion, precio, costo, stock, estado
            FROM articulos
            ORDER BY articulo
        """
        try:
            data = self.db.execute_query(query)
            
            # Limpiar tabla
            self.tree.delete(*self.tree.get_children())
            
            if data:
                # Actualizar combobox de búsqueda
                self.search_combo['values'] = [row['articulo'] for row in data]
                
                # Llenar tabla
                for row in data:
                    self.tree.insert("", "end", values=(
                        row['id'],
                        row['articulo'],
                        row['descripcion'] or '',
                        f"${float(row['precio']):,.2f}",
                        f"${float(row['costo']):,.2f}",
                        row['stock'],
                        row['estado']
                    ))
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    def show_add_dialog(self):
        """Mostrar diálogo para agregar nuevo artículo"""
        dialog = tk.Toplevel(self)
        dialog.title("Agregar Artículo")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Formulario
        form_frame = ttk.LabelFrame(dialog, text="Datos del Artículo")
        form_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Campos
        fields = {}
        row = 0
        for field in ["Artículo", "Descripción", "Precio", "Costo", "Stock", "Estado"]:
            ttk.Label(form_frame, text=field + ":").grid(row=row, column=0, padx=5, pady=5)
            if field == "Descripción":
                fields[field] = tk.Text(form_frame, height=3)
            elif field == "Estado":
                fields[field] = ttk.Combobox(form_frame, values=["Activo", "Inactivo"])
                fields[field].set("Activo")
            else:
                fields[field] = ttk.Entry(form_frame)
            fields[field].grid(row=row, column=1, padx=5, pady=5, sticky="ew")
            row += 1
        
        # Frame para imagen
        image_frame = ttk.LabelFrame(dialog, text="Imagen del Artículo")
        image_frame.pack(fill="x", padx=5, pady=5)
        
        self.image_path = None
        self.image_preview = ttk.Label(image_frame, text="Sin imagen")
        self.image_preview.pack(pady=5)
        
        ttk.Button(image_frame, text="Seleccionar Imagen",
                  command=lambda: self.select_image(self.image_preview)
                  ).pack(pady=5)
        
        # Botones
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Guardar",
                  command=lambda: self.save_product(fields, dialog)
                  ).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Cancelar",
                  command=dialog.destroy).pack(side="right", padx=5)

    @handle_exceptions("Guardar producto")
    def save_product(self, fields, dialog):
        """Guardar nuevo producto en la base de datos"""
        try:
            # Validar campos
            data = {
                'articulo': fields['Artículo'].get(),
                'descripcion': fields['Descripción'].get("1.0", "end-1c"),
                'precio': float(fields['Precio'].get()),
                'costo': float(fields['Costo'].get()),
                'stock': int(fields['Stock'].get()),
                'estado': fields['Estado'].get(),
                'image_path': self.image_path or ''
            }
            
            # Validaciones básicas
            if not data['articulo']:
                messagebox.showerror("Error", "El nombre del artículo es requerido")
                return
            
            if data['precio'] < 0 or data['costo'] < 0:
                messagebox.showerror("Error", "El precio y costo deben ser positivos")
                return
            
            if data['stock'] < 0:
                messagebox.showerror("Error", "El stock debe ser positivo")
                return
            
            # Insertar en base de datos
            self.db.insert('articulos', data)
            messagebox.showinfo("Éxito", "Artículo guardado correctamente")
            dialog.destroy()
            self.load_data()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor verifique los valores numéricos")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    def show_edit_dialog(self):
        """Mostrar diálogo para editar artículo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para editar")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Editar Artículo")
        dialog.geometry("600x500")
        dialog.transient(self)
        dialog.grab_set()
        
        # Obtener datos del artículo seleccionado
        item = self.tree.item(selected[0])
        id_articulo = item['values'][0]
        
        # Obtener datos completos de la base de datos
        try:
            data = self.db.execute_query(
                "SELECT * FROM articulos WHERE id = ?", 
                (id_articulo,)
            )[0]
            
            # Formulario
            form_frame = ttk.LabelFrame(dialog, text="Datos del Artículo")
            form_frame.pack(fill="both", expand=True, padx=5, pady=5)
            
            # Campos
            fields = {}
            row = 0
            field_data = {
                'Artículo': data['articulo'],
                'Descripción': data['descripcion'] or '',
                'Precio': str(data['precio']),
                'Costo': str(data['costo']),
                'Stock': str(data['stock']),
                'Estado': data['estado']
            }
            
            for field, value in field_data.items():
                ttk.Label(form_frame, text=field + ":").grid(row=row, column=0, padx=5, pady=5)
                if field == "Descripción":
                    fields[field] = tk.Text(form_frame, height=3)
                    fields[field].insert("1.0", value)
                elif field == "Estado":
                    fields[field] = ttk.Combobox(form_frame, values=["Activo", "Inactivo"])
                    fields[field].set(value)
                else:
                    fields[field] = ttk.Entry(form_frame)
                    fields[field].insert(0, value)
                fields[field].grid(row=row, column=1, padx=5, pady=5, sticky="ew")
                row += 1
            
            # Frame para imagen
            image_frame = ttk.LabelFrame(dialog, text="Imagen del Artículo")
            image_frame.pack(fill="x", padx=5, pady=5)
            
            self.image_path = data['image_path']
            self.image_preview = ttk.Label(image_frame)
            
            if self.image_path and os.path.exists(self.image_path):
                image = Image.open(self.image_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_preview.configure(image=photo)
                self.image_preview.image = photo
            else:
                self.image_preview.configure(text="Sin imagen")
            self.image_preview.pack(pady=5)
            
            ttk.Button(image_frame, text="Cambiar Imagen",
                    command=lambda: self.select_image(self.image_preview)).pack(pady=5)
            
            # Botones
            btn_frame = ttk.Frame(dialog)
            btn_frame.pack(fill="x", padx=5, pady=5)
            
            def update():
                try:
                    new_data = {
                        'articulo': fields['Artículo'].get(),
                        'descripcion': fields['Descripción'].get("1.0", "end-1c"),
                        'precio': float(fields['Precio'].get()),
                        'costo': float(fields['Costo'].get()),
                        'stock': int(fields['Stock'].get()),
                        'estado': fields['Estado'].get(),
                        'image_path': self.image_path or ''
                    }
                    
                    # Validaciones básicas
                    if not new_data['articulo']:
                        messagebox.showerror("Error", "El nombre del artículo es requerido")
                        return
                    
                    if new_data['precio'] < 0 or new_data['costo'] < 0:
                        messagebox.showerror("Error", "El precio y costo deben ser positivos")
                        return
                    
                    if new_data['stock'] < 0:
                        messagebox.showerror("Error", "El stock debe ser positivo")
                        return
                    
                    # Actualizar en base de datos
                    self.db.execute_query("""
                        UPDATE articulos 
                        SET articulo=?, descripcion=?, precio=?, costo=?, 
                            stock=?, estado=?, image_path=?
                        WHERE id=?
                    """, (
                        new_data['articulo'], new_data['descripcion'], 
                        new_data['precio'], new_data['costo'],
                        new_data['stock'], new_data['estado'], 
                        new_data['image_path'], id_articulo
                    ))
                    
                    messagebox.showinfo("Éxito", "Artículo actualizado correctamente")
                    dialog.destroy()
                    self.load_data()
                    
                except ValueError:
                    messagebox.showerror("Error", "Por favor verifique los valores numéricos")
                except Exception as e:
                    messagebox.showerror("Error", f"Error al actualizar: {str(e)}")
            
            ttk.Button(btn_frame, text="Guardar", command=update).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Cancelar", command=dialog.destroy).pack(side="right", padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos del artículo: {str(e)}")
            dialog.destroy()
    def delete_product(self):
        """Eliminar artículo seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para eliminar")
            return
        
        if messagebox.askyesno("Confirmar", "¿Está seguro de eliminar este artículo?"):
            try:
                item = self.tree.item(selected[0])
                id_articulo = item['values'][0]
                self.db.execute_query("DELETE FROM articulos WHERE id = ?", (id_articulo,))
                messagebox.showinfo("Éxito", "Artículo eliminado correctamente")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar: {str(e)}")

    def show_stock_dialog(self):
        """Mostrar diálogo para actualizar stock"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un artículo para actualizar stock")
            return
        
        dialog = tk.Toplevel(self)
        dialog.title("Actualizar Stock")
        dialog.geometry("300x200")
        dialog.transient(self)
        dialog.grab_set()
        
        # Get current stock
        item = self.tree.item(selected[0])
        current_stock = item['values'][5]
        
        ttk.Label(dialog, text=f"Stock actual: {current_stock}").pack(pady=5)
        ttk.Label(dialog, text="Cantidad:").pack(pady=5)
        cantidad = ttk.Entry(dialog)
        cantidad.pack(pady=5)
        
        ttk.Label(dialog, text="Tipo:").pack(pady=5)
        tipo = ttk.Combobox(dialog, values=["Entrada", "Salida"], state="readonly")
        tipo.set("Entrada")
        tipo.pack(pady=5)
        
        def actualizar():
            try:
                cant = int(cantidad.get())
                if cant <= 0:
                    messagebox.showerror("Error", "La cantidad debe ser positiva")
                    return
                    
                id_articulo = item['values'][0]
                
                if tipo.get() == "Salida":
                    if cant > current_stock:
                        messagebox.showerror("Error", "No hay suficiente stock")
                        return
                    cant = -cant
                
                self.db.execute_query("""
                    UPDATE articulos 
                    SET stock = stock + ? 
                    WHERE id = ?
                """, (cant, id_articulo))
                
                messagebox.showinfo("Éxito", "Stock actualizado correctamente")
                dialog.destroy()
                self.load_data()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese una cantidad válida")
        
        ttk.Button(dialog, text="Actualizar", command=actualizar).pack(pady=20)

    def select_image(self, preview_label):
        """Seleccionar y previsualizar imagen"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp")]
        )
        
        if file_path:
            try:
                # Copiar imagen a carpeta del proyecto
                image = Image.open(file_path)
                image = image.resize((200, 200), Image.Resampling.LANCZOS)
                
                # Generar nombre único
                new_filename = f"{secrets.token_hex(8)}{os.path.splitext(file_path)[1]}"
                new_path = os.path.join(self.image_folder, new_filename)
                
                image.save(new_path)
                self.image_path = new_path
                
                # Mostrar preview
                preview = ImageTk.PhotoImage(image)
                preview_label.configure(image=preview)
                preview_label.image = preview
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al procesar la imagen: {str(e)}")

    def sort_treeview(self, col):
        """Ordenar la tabla por columna"""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        items.sort()
        for index, (val, item) in enumerate(items):
            self.tree.move(item, '', index)