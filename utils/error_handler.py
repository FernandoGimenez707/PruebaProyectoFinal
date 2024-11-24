# utils/error_handler.py
import logging
import traceback
from functools import wraps
from tkinter import messagebox
from datetime import datetime
import os

class ErrorHandler:
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            filename=f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

def handle_exceptions(context):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logging.error(f"Error in {context}: {str(e)}")
                logging.error(traceback.format_exc())
                messagebox.showerror("Error", f"Error in {context}: {str(e)}")
                raise
        return wrapper
    return decorator