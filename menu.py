import tkinter as tk
from tkinter import ttk
from settings_folder.gui import GUIManager
from settings import AppConfiguration, SettingsPanel
from screenshots import ScreenshotManager

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.gui = GUIManager()
        self.app_config = AppConfiguration()
        
        # Configure main window
        self.root.title("Automation Tool")
        self.root.geometry(self.gui.main_window_size)
        self.root.minsize(*self.gui.min_window_size)
        self.root.configure(bg=self.gui.bg_color)
        
        # Create container frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Initialize components
        self.screenshot_manager = ScreenshotManager(self.root, self.app_config)
        self.settings_panel = SettingsPanel(self.main_frame, self.app_config, self.show_main_menu)
        
        # Bind return to main event
        self.root.bind("<<ReturnToMain>>", lambda e: self.show_main_menu())
        
        # Show main menu initially
        self.show_main_menu()
    
    def show_main_menu(self):
        """Display the main menu screen"""
        # Clear current frame
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
        # Main menu widgets
        ttk.Label(self.main_frame, 
                 text="Main Menu",
                 style="Heading.TLabel").pack(pady=20)
        
        buttons = [
            ("BWID", self._on_bwid),
            ("Screenshots", self._on_screenshots),
            ("Settings", self._on_settings)
        ]
        
        for text, command in buttons:
            ttk.Button(self.main_frame, 
                      text=text,
                      command=command).pack(fill='x', pady=5)
    
    def _on_bwid(self):
        print("BWID functionality triggered")
    
    def _on_screenshots(self):
        self.screenshot_manager.show_screenshot_menu(self.main_frame)
    
    def _on_settings(self):
        self.settings_panel.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()