import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import screeninfo
from pathlib import Path

class AppConfiguration:
    def __init__(self):
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(script_dir, "settings_folder", "app_config.json")
        self.default_config = {
            "screenshot_dir": str(Path.home() / "AutomationScreenshots"),
            "selected_monitors": "all",
            "monitor_details": []
        }
        self.config = self._load_config()
        self._ensure_monitor_details()
    
    def _ensure_monitor_details(self):
        """Ensure monitor details are up-to-date"""
        if not self.config.get("monitor_details"):
            self.config["monitor_details"] = self.detect_displays()
            self.save_config()
    
    def _load_config(self):
        """Load existing config or create new"""
        try:
            # Create settings_folder if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load config: {e}")
        
        return self.default_config
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
            return False
    
    def detect_displays(self):
        """Get all connected monitors"""
        try:
            return [
                {
                    "id": idx,
                    "name": getattr(mon, "name", f"Display {idx+1}"),
                    "primary": mon.is_primary,
                    "resolution": f"{mon.width}x{mon.height}",
                    "geometry": f"{mon.width}x{mon.height}+{mon.x}+{mon.y}"
                }
                for idx, mon in enumerate(screeninfo.get_monitors())
            ]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect displays: {e}")
            return []

class SettingsPanel:
    def __init__(self, parent_frame, app_config, back_callback):
        self.parent_frame = parent_frame
        self.app_config = app_config
        self.back_callback = back_callback
        self.frame = ttk.Frame(parent_frame)
        
    def show(self):
        """Show the settings panel"""
        # Clear parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Back button
        ttk.Button(self.parent_frame,
                 text="← Back to Main Menu",
                 command=self.back_callback).pack(anchor='nw', pady=5)
        
        # Settings title
        ttk.Label(self.parent_frame, 
                 text="Settings",
                 style="Heading.TLabel").pack(pady=20)
        
        # Path selection
        self._create_path_selector()
        
        # Monitor selection
        self._create_monitor_selector()
        
        # Save button
        ttk.Button(self.parent_frame,
                 text="Save Settings",
                 command=self._save_settings).pack(pady=20)
    
    def _create_path_selector(self):
        path_frame = ttk.Frame(self.parent_frame)
        path_frame.pack(fill='x', pady=10)
        
        ttk.Label(path_frame, text="Screenshot Path:").pack(side='left')
        self.path_var = tk.StringVar(value=self.app_config.config["screenshot_dir"])
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.pack(side='left', expand=True, fill='x', padx=5)
        
        ttk.Button(path_frame, 
                 text="Browse",
                 command=lambda: self._browse_path(path_entry)).pack(side='left')
    
    def _create_monitor_selector(self):
        monitor_frame = ttk.LabelFrame(self.parent_frame, text="Monitor Selection", padding=10)
        monitor_frame.pack(fill='x', pady=10)
        
        if not self.app_config.config["monitor_details"]:
            ttk.Label(monitor_frame, text="No monitors detected").pack()
        else:
            self.monitor_var = tk.StringVar(value=self.app_config.config["selected_monitors"])
            
            ttk.Radiobutton(
                monitor_frame,
                text="All Monitors",
                variable=self.monitor_var,
                value="all"
            ).pack(anchor='w')
            
            for monitor in self.app_config.config["monitor_details"]:
                display_name = f"{monitor['name']} ({monitor['resolution']})"
                if monitor["primary"]:
                    display_name += " (Primary)"
                
                ttk.Radiobutton(
                    monitor_frame,
                    text=display_name,
                    variable=self.monitor_var,
                    value=str(monitor["id"])
                ).pack(anchor='w')
    
    def _browse_path(self, entry_widget):
        path = filedialog.askdirectory(
            initialdir=self.app_config.config["screenshot_dir"],
            title="Select Screenshot Directory"
        )
        if path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, path)
            self.app_config.config["screenshot_dir"] = path
    
    def _save_settings(self):
        self.app_config.config["screenshot_dir"] = self.path_var.get()
        self.app_config.config["selected_monitors"] = self.monitor_var.get()
        if self.app_config.save_config():
            messagebox.showinfo("Success", "Settings saved successfully")