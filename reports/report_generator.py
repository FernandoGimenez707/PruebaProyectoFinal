#report_generator.py
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from db_utils import db_operation
import os

class ReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        os.makedirs('reportes', exist_ok=True)

    def create_report(self, filename, elements):
        doc = SimpleDocTemplate(f"reportes/{filename}", pagesize=letter)
        doc.build(elements)

class SalesReport(ReportGenerator):
    @db_operation
    def get_sales_data(cursor, self, start_date, end_date):
        query = """
            SELECT fecha, factura, cliente, articulo, cantidad, precio, total
            FROM ventas 
            WHERE fecha BETWEEN ? AND ?
        """
        cursor.execute(query, (start_date, end_date))
        return pd.DataFrame(cursor.fetchall(), 
                          columns=['fecha', 'factura', 'cliente', 'articulo', 
                                 'cantidad', 'precio', 'total'])

    def generate(self, start_date, end_date):
        df = self.get_sales_data(start_date, end_date)
        elements = []
        
        # Title
        elements.append(Paragraph(f"Reporte de Ventas: {start_date} - {end_date}", 
                                self.styles['Title']))
        
        # Summary Statistics
        stats = pd.DataFrame({
            'Total Ventas': [df['total'].sum()],
            'Número de Ventas': [len(df)],
            'Venta Promedio': [df['total'].mean()],
            'Mayor Venta': [df['total'].max()]
        })
        
        # Add charts
        self.add_sales_chart(df, elements)
        self.add_products_chart(df, elements)
        
        # Add detailed table
        table_data = [df.columns.tolist()] + df.values.tolist()
        elements.append(Table(table_data, style=self.get_table_style()))
        
        self.create_report(f"ventas_{datetime.now().strftime('%Y%m%d')}.pdf", 
                          elements)

class InventoryReport(ReportGenerator):
    @db_operation
    def get_inventory_data(cursor, self):
        query = """
            SELECT articulo, precio, costo, stock, estado
            FROM articulos
        """
        cursor.execute(query)
        return pd.DataFrame(cursor.fetchall(), 
                          columns=['articulo', 'precio', 'costo', 'stock', 'estado'])

    def generate(self):
        df = self.get_inventory_data()
        elements = []
        
        elements.append(Paragraph("Reporte de Inventario", self.styles['Title']))
        
        # Stock Statistics
        low_stock = df[df['stock'] < 10]
        elements.append(Paragraph(
            f"Productos con bajo stock ({len(low_stock)})", 
            self.styles['Heading2']
        ))
        
        # Value Statistics
        total_value = (df['precio'] * df['stock']).sum()
        elements.append(Paragraph(
            f"Valor total del inventario: ${total_value:,.2f}", 
            self.styles['Normal']
        ))
        
        # Add charts
        self.add_stock_chart(df, elements)
        
        # Add detailed table
        table_data = [df.columns.tolist()] + df.values.tolist()
        elements.append(Table(table_data, style=self.get_table_style()))
        
        self.create_report(f"inventario_{datetime.now().strftime('%Y%m%d')}.pdf", 
                          elements)

    def get_table_style(self):
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])