# utils/db_manager.py
from typing import List, Dict, Any, Optional
import db_utils
from utils.error_handler import handle_exceptions

class DatabaseManager:
    # ...

    @handle_exceptions("Database query")
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        with db_utils.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if cursor.description:  # Para SELECT queries
                columns = [column[0] for column in cursor.description]
                results = cursor.fetchall()
                return [dict(zip(columns, row)) for row in results]
            conn.commit()  # Para INSERT, UPDATE, DELETE queries
            return []

    # ...

    @handle_exceptions("Get daily sales")
    def get_daily_sales(self) -> float:
        query = "SELECT COALESCE(SUM(total), 0) AS daily_sales FROM ventas WHERE CONVERT(date, fecha) = CONVERT(date, GETDATE())"
        result = self.execute_query(query)
        return result[0]["daily_sales"]

    @handle_exceptions("Get monthly sales")
    def get_monthly_sales(self) -> float:
        query = "SELECT COALESCE(SUM(total), 0) AS monthly_sales FROM ventas WHERE YEAR(fecha) = YEAR(GETDATE()) AND MONTH(fecha) = MONTH(GETDATE())"
        result = self.execute_query(query)
        return result[0]["monthly_sales"]

    @handle_exceptions("Get top selling products")
    def get_top_selling_products(self, limit: int = 5) -> List[Dict]:
        query = """
            SELECT TOP (?) a.articulo, SUM(v.cantidad) as total_vendido
            FROM ventas v
            JOIN articulos a ON v.articulo = a.articulo
            GROUP BY a.articulo
            ORDER BY total_vendido DESC
        """
        return self.execute_query(query, (limit,))

    @handle_exceptions("Get sales by category")
    def get_sales_by_category(self) -> List[Dict]:
        query = """
            SELECT a.categoria, COALESCE(SUM(v.total), 0) as total_ventas
            FROM articulos a
            LEFT JOIN ventas v ON a.articulo = v.articulo
            GROUP BY a.categoria
        """
        return self.execute_query(query)

    @handle_exceptions("Get sales by month")
    def get_sales_by_month(self) -> List[Dict]:
        query = """
            SELECT 
                CONVERT(varchar(7), fecha, 126) as mes,
                COALESCE(SUM(total), 0) as total_ventas
            FROM ventas
            GROUP BY CONVERT(varchar(7), fecha, 126)
            ORDER BY mes
        """
        return self.execute_query(query)

    # ...