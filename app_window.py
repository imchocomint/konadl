# app_window.py
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QScrollArea, QMessageBox,
                             QFileDialog, QInputDialog, QLabel, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from threading import Thread
import os

from ui_elements import ImageResultWidget
from konachan_api import KonachanAPI
from settings_manager import SettingsManager
from config_manager import ConfigManager

class ImageSearchApp(QMainWindow):
    update_status_signal = pyqtSignal(str)
    show_message_box_signal = pyqtSignal(str, bool)
    update_results_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.config_manager = ConfigManager()
        self.api = KonachanAPI()
        self.load_settings()
        self.initUI()
        self.apply_theme()

    def initUI(self):
        width = int(self.config_manager.get_setting("General", "app_width"))
        height = int(self.config_manager.get_setting("General", "app_height"))
        opacity_effect = QGraphicsOpacityEffect()
        self.setWindowTitle("konadl")
        self.setGeometry(100, 100, width, height)
        opacity_effect.setOpacity(float(self.config_manager.get_setting("General", "app_opacity")))
        self.setGraphicsEffect(opacity_effect)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tags...")
        self.search_box.setFont(QFont("Arial", 12))
        self.search_box.returnPressed.connect(self.search_images)
        
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("searchButton")
        self.search_button.clicked.connect(self.search_images)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_button)

        # Menu button to open config file
        self.settings_button = QPushButton("Open Config")
        self.settings_button.setObjectName("settingsButton")
        self.settings_button.clicked.connect(self.open_config_file)
        search_layout.addWidget(self.settings_button)
        self.main_layout.addLayout(search_layout)

        # Status Bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Scrollable area for results
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area_content = QWidget()
        self.results_layout = QVBoxLayout(self.scroll_area_content)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.results_layout.setSpacing(10)
        self.scroll_area.setWidget(self.scroll_area_content)
        self.main_layout.addWidget(self.scroll_area)

        # Connect custom signals to their slots
        self.update_status_signal.connect(self.update_status_label)
        self.show_message_box_signal.connect(self.show_message_box)
        self.update_results_signal.connect(self.display_results)

    def load_settings(self):
        self.download_dir = self.config_manager.get_download_folder()
        self.autoexclude_tags = self.config_manager.get_autoexclude_tags()
        self.background_color = self.config_manager.get_background_color()
        self.button_color = self.config_manager.get_button_color()

    def apply_theme(self):
        self.main_widget.setStyleSheet(f"background-color: {self.background_color.name()};")
        
        button_style = f"""
            #searchButton, #settingsButton {{
                background-color: {self.button_color.name()};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }}
            #searchButton:hover, #settingsButton:hover {{
                background-color: {self.button_color.darker(120).name()};
            }}
        """
        self.setStyleSheet(button_style)
        
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

    def open_config_file(self):
        if not os.path.exists(self.config_manager.config_path):
            self.config_manager.save_config()
            QMessageBox.information(self, "Config File Created",
                                    f"A new config file has been created at:\n{self.config_manager.config_path}\n\nPlease edit this file and restart the application to apply changes.")
        
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.config_manager.config_path))

    def update_result_button_colors(self, color):
        for i in range(self.results_layout.count()):
            widget = self.results_layout.itemAt(i).widget()
            if isinstance(widget, ImageResultWidget):
                widget.set_button_color(color)

    def clear_results(self):
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

    def search_images(self):
        search_query = self.search_box.text()
        self.update_status_signal.emit(f"Searching for: {search_query}")
        self.clear_results()

        thread = Thread(target=self.perform_search, args=(search_query,))
        thread.start()

    def perform_search(self, search_query):
        images, error = self.api.search_images(search_query, self.autoexclude_tags)
        
        if error:
            self.show_message_box_signal.emit("Search failed: " + error, True)
            self.update_status_signal.emit("Search failed.")
            return

        self.update_results_signal.emit(images)

    def download_image_threaded(self, url, file_extension):
        counter = self.settings_manager.increment_download_counter()
        filename = f"{counter}{file_extension}"
        save_path = os.path.join(self.download_dir, filename)
        
        self.update_status_signal.emit(f"Downloading {filename}...")
        
        thread = Thread(target=self.perform_download, args=(url, save_path, filename))
        thread.start()

    def perform_download(self, url, save_path, filename):
        success, message = self.api.download_image(url, save_path)
        
        if success:
            self.show_message_box_signal.emit(f"Successfully downloaded {filename}.", False)
            self.update_status_signal.emit(f"Successfully downloaded {filename}.")
        else:
            self.show_message_box_signal.emit(f"Failed to download {filename}: {message}", True)
            self.update_status_signal.emit(f"Failed to download {filename}.")

    # --- Slots for Signals ---
    def update_status_label(self, message):
        self.status_label.setText(message)

    def show_message_box(self, message, is_error):
        if is_error:
            QMessageBox.critical(self, "Error", message)
        else:
            QMessageBox.information(self, "Success", message)

    def display_results(self, images):
        if not images:
            self.update_status_signal.emit("No images found.")
        else:
            self.update_status_signal.emit(f"Found {len(images)} images.")
        
        self.clear_results()
        for data in images:
            widget = ImageResultWidget(image_data=data, api=self.api)
            widget.set_button_color(self.button_color.name())
            widget.download_requested.connect(self.download_image_threaded)
            self.results_layout.addWidget(widget)
        self.update_result_button_colors(self.button_color.name())