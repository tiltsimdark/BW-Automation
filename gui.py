import tkinter as tk
from tkinter import ttk

class GUIManager:
    """Handles all GUI styling and window configurations"""
    
    def __init__(self):
        # Window defaults
        self.main_window_size = "800x600"
        self.min_window_size = (600, 400)
        self.bg_color = "#f0f0f0"
        self.padding = 20
        
        # Font settings
        self.font_primary = ("Segoe UI", 12)
        self.font_heading = ("Segoe UI", 16, "bold")
        
        # Initialize styles
        self.style = ttk.Style()
        self._setup_styles()
    
    def _setup_styles(self):
        """Configure all widget styles"""
        # Configure the style of ttk widgets
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TButton', 
                           font=self.font_primary,
                           padding=10)
        self.style.configure('Heading.TLabel', 
                           font=self.font_heading,
                           background=self.bg_color)
        self.style.configure('TEntry',
                           font=self.font_primary,
                           padding=5)

def configure_window(window, title=None):
    """Apply standard window configuration"""
    gui = GUIManager()
    if title:
        window.title(title)
    window.geometry(gui.main_window_size)
    window.minsize(*gui.min_window_size)
    window.configure(bg=gui.bg_color)
    return gui