# settings_manager.py
from PyQt6.QtCore import QSettings
import os

class SettingsManager:
    def __init__(self, organization_name="KonachanDownloader", app_name="ImageSearchApp"):
        self.settings = QSettings(organization_name, app_name)
        self.download_counter = self.settings.value("download_counter", 0, type=int)

    def load_settings(self):
        return {
            "download_dir": self.settings.value(
                "download_dir", os.path.join(os.path.expanduser("~"), "KonachanDownloads"), type=str
            ),
            "autoexclude_tags": self.settings.value("autoexclude_tags", "", type=str),
            "background_color": self.settings.value("background_color", "#f0f0f0", type=str),
            "button_color": self.settings.value("button_color", "#007BFF", type=str),
        }

    def save_setting(self, key, value):
        self.settings.setValue(key, value)
    
    def get_download_counter(self):
        return self.settings.value("download_counter", 0, type=int)

    def increment_download_counter(self):
        self.download_counter += 1
        self.settings.setValue("download_counter", self.download_counter)
        return self.download_counter