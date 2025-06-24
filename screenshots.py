import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
from PIL import ImageGrab, Image
from settings import AppConfiguration
import json

class ScreenshotManager:
    def __init__(self, root_window, app_config):
        self.root = root_window
        self.app_config = app_config
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.current_x = None
        self.current_y = None
        self.selection_canvas = None
        self.last_selection = None  # Stores last selected area (x1, y1, x2, y2)
        self.config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings_folder", "screenshot_settings.json")
        self._load_last_selection()

    def _load_last_selection(self):
        """Load last selected area from config file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.last_selection = data.get('last_selection')
        except Exception:
            self.last_selection = None

    def _save_last_selection(self):
        """Save last selected area to config file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump({'last_selection': self.last_selection}, f)
        except Exception:
            pass

    def show_screenshot_menu(self, parent_frame):
        """Show screenshot options in the provided frame"""
        for widget in parent_frame.winfo_children():
            widget.destroy()

        ttk.Button(parent_frame,
                 text="← Back to Main Menu",
                 command=lambda: self._return_to_main()).pack(anchor='nw', pady=5)

        ttk.Label(parent_frame, 
                 text="Screenshot Options",
                 style="Heading.TLabel").pack(pady=20)

        ttk.Button(parent_frame,
                 text="1. Take Manual Screenshot",
                 command=self._take_manual_screenshot,
                 style="Accent.TButton").pack(fill='x', pady=10)

        ttk.Button(parent_frame,
                 text="2. Take Automatic Screenshot",
                 command=self._take_auto_screenshot,
                 style="Accent.TButton").pack(fill='x', pady=10)

        ttk.Button(parent_frame,
                 text="3. Location Screenshot",
                 command=self._take_location_screenshot,
                 style="Accent.TButton").pack(fill='x', pady=10)

    def _return_to_main(self):
        self.root.event_generate("<<ReturnToMain>>")

    def _take_manual_screenshot(self):
        """Handle manual screenshot with hidden main window"""
        self.root.withdraw()
        self._create_selection_overlay(save_location=True)

    def _take_location_screenshot(self):
        """Take screenshot of previously selected area"""
        if not self.last_selection:
            # If no previous selection, prompt to select area first
            self.root.withdraw()
            self._create_selection_overlay(save_location=True, is_location_screenshot=True)
            return
        
        # Take screenshot of saved location
        self.root.withdraw()
        time.sleep(0.2)  # Small delay to ensure window is hidden
        
        try:
            x1, y1, x2, y2 = self.last_selection
            screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
            self._save_screenshot(screenshot, "location")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture: {str(e)}")
        finally:
            self.root.deiconify()

    def _create_selection_overlay(self, save_location=False, is_location_screenshot=False):
        selection_win = tk.Toplevel(self.root)
        selection_win.attributes('-fullscreen', True)
        selection_win.attributes('-alpha', 0.3)
        selection_win.attributes('-topmost', True)
        
        self.selection_canvas = tk.Canvas(selection_win, cursor="cross")
        self.selection_canvas.pack(fill='both', expand=True)
        
        self.selection_canvas.bind("<ButtonPress-1>", self._on_press)
        self.selection_canvas.bind("<B1-Motion>", self._on_drag)
        self.selection_canvas.bind("<ButtonRelease-1>", 
            lambda e: self._on_release(e, save_location, is_location_screenshot))
        selection_win.bind("<Escape>", lambda e: self._cancel_screenshot(selection_win))

    def _cancel_screenshot(self, window):
        """Cancel screenshot and restore main window"""
        window.destroy()
        self.root.deiconify()

    def _on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.selection_canvas.create_rectangle(
            self.start_x, self.start_y, 
            self.start_x, self.start_y,
            outline='red', width=2, fill='white')

    def _on_drag(self, event):
        self.current_x, self.current_y = event.x, event.y
        self.selection_canvas.coords(
            self.rect, self.start_x, self.start_y, 
            self.current_x, self.current_y)

    def _on_release(self, event, save_location, is_location_screenshot):
        self.selection_canvas.master.destroy()
        
        x1, y1 = min(self.start_x, self.current_x), min(self.start_y, self.current_y)
        x2, y2 = max(self.start_x, self.current_x), max(self.start_y, self.current_y)
        
        if save_location:
            self.last_selection = (x1, y1, x2, y2)
            self._save_last_selection()
        
        time.sleep(0.2)
        screenshot = pyautogui.screenshot(region=(x1, y1, x2-x1, y2-y1))
        
        if is_location_screenshot:
            self._save_screenshot(screenshot, "location")
        else:
            self._save_manual_screenshot(screenshot)
        
        self.root.deiconify()

    def _save_manual_screenshot(self, screenshot):
        """Show save dialog for manual screenshots"""
        default_dir = self.app_config.config["screenshot_dir"]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_name = f"screenshot_manual_{timestamp}.png"
        
        file_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_name,
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if file_path:
            screenshot.save(file_path)

    def _take_auto_screenshot(self):
        """Automatic screenshot with hidden main window"""
        self.root.withdraw()
        time.sleep(0.2)
        
        try:
            monitors = self.app_config.config["monitor_details"]
            selected = self.app_config.config["selected_monitors"]
            
            if selected == "all":
                for monitor in monitors:
                    self._capture_monitor(monitor)
            else:
                monitor_id = int(selected)
                monitor = next((m for m in monitors if m["id"] == monitor_id), None)
                if monitor:
                    self._capture_monitor(monitor)
        finally:
            self.root.deiconify()

    def _capture_monitor(self, monitor):
        try:
            width, height, x, y = map(int, monitor["geometry"].replace('x', '+').split('+'))
            screenshot = ImageGrab.grab(bbox=(x, y, x+width, y+height))
            self._save_screenshot(screenshot, f"monitor_{monitor['id']}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to capture monitor: {str(e)}")

    def _save_screenshot(self, screenshot, prefix=""):
        """Save screenshot without showing dialog"""
        default_dir = self.app_config.config["screenshot_dir"]
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        default_name = f"{prefix}_{timestamp}.png"
        save_path = os.path.join(default_dir, default_name)
        
        os.makedirs(default_dir, exist_ok=True)
        screenshot.save(save_path)