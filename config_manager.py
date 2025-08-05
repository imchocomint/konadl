# config_manager.py
import configparser
import os
from PyQt6.QtGui import QColor

class ConfigManager:
    def __init__(self, app_name="konadl"):
        config_dir = os.path.join(os.path.expanduser("~"), ".config", app_name)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.config_path = os.path.join(config_dir, "config.ini")
        
        self.config = configparser.ConfigParser()
        self.load_config()

    def load_config(self):
        self.config.read(self.config_path)
        
        # Set default values if not present
        if "General" not in self.config:
            self.config["General"] = {
                # Corrected: Use os.path.expanduser('~') for a valid home directory path
                "download_folder": os.path.join(os.path.expanduser("~"), "KcdlDownloads"),
                "autoexclude_tags": "loli,shota,young",
                "app_width": "800",
                "app_height": "900",
                "app_opacity": "1.0"
            }
        
        if "Colors" not in self.config:
            self.config["Colors"] = {
                "background": "#f0f0f0",
                "button": "#007BFF"
            }
            
        self.save_config()

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)

    def get_setting(self, section, key):
        try:
            return self.config.get(section, key)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return None

    def set_setting(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config.set(section, key, str(value))
        self.save_config()
        
    def get_download_folder(self):
        # A small fix to ensure the value is always a valid path
        folder = self.get_setting("General", "download_folder")
        if folder.startswith("~"):
            return os.path.expanduser(folder)
        return folder
        
    def get_autoexclude_tags(self):
        return self.get_setting("General", "autoexclude_tags")
        
    def get_background_color(self):
        color_hex = self.get_setting("Colors", "background")
        return QColor(color_hex) if QColor(color_hex).isValid() else QColor("#f0f0f0")
    
    def get_button_color(self):
        color_hex = self.get_setting("Colors", "button")
        return QColor(color_hex) if QColor(color_hex).isValid() else QColor("#007BFF")
        
    def get_app_size(self):
        width = int(self.get_setting("General", "app_width"))
        height = int(self.get_setting("General", "app_height"))
        return width, height
        
    def get_app_opacity(self):
        return float(self.get_setting("General", "app_opacity"))