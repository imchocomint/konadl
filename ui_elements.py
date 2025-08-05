# ui_elements.py
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
import requests
from threading import Thread
import time

class ImageResultWidget(QWidget):
    download_requested = pyqtSignal(str, str)

    def __init__(self, parent=None, image_data=None, api=None):
        super().__init__(parent)
        self.image_data = image_data or {}
        self.api = api
        self.download_url = self.image_data.get('download_url', '')
        self.file_extension = self.image_data.get('file_extension', '.jpg')
        self.initUI()
        self.load_thumbnail()

    def initUI(self):
        self.setObjectName("ImageResultWidget")
        self.setMinimumHeight(200)
        self.setMaximumHeight(200)

        self.setStyleSheet("""
            #ImageResultWidget {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #ffffff;
            }
            QLabel {
                font-family: sans-serif;
            }
        """)

        main_layout = QHBoxLayout(self)

        # Image Placeholder
        self.image_label = QLabel("Loading...")
        self.image_label.setFixedSize(180, 180)
        self.image_label.setStyleSheet("border: 1px solid black; background-color: #f0f0f0; text-align: center;")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.image_label)

        # Details Layout
        details_layout = QVBoxLayout()
        details_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.name_label = QLabel(f"name: {self.image_data.get('name', 'N/A')}")
        self.tags_label = QLabel(f"tags: {', '.join(self.image_data.get('tags', []))}")
        self.tags_label.setWordWrap(True)
        self.author_label = QLabel(f"author: {self.image_data.get('author', 'N/A')}")
        
        details_layout.addWidget(self.name_label)
        details_layout.addWidget(self.tags_label)
        details_layout.addWidget(self.author_label)

        main_layout.addLayout(details_layout)
        main_layout.addStretch(1)

        # Download Button
        self.download_button = QPushButton("Download")
        self.download_button.setFixedWidth(80)
        self.download_button.setObjectName("downloadButton")
        self.download_button.clicked.connect(self.download_image_clicked)
        main_layout.addWidget(self.download_button, alignment=Qt.AlignmentFlag.AlignBottom)

    def set_button_color(self, color):
        self.download_button.setStyleSheet(f"""
            #downloadButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
            }}
            #downloadButton:hover {{
                background-color: #0056b3;
            }}
        """)

    def load_thumbnail(self):
        thumbnail_url = self.image_data.get('preview_url')
        if not thumbnail_url:
            self.image_label.setText("No Preview")
            return
        
        def fetch_image_with_retry():
            max_retries = 3
            for i in range(max_retries):
                try:
                    response = self.api.session.get(thumbnail_url, timeout=5)
                    response.raise_for_status()
                    image_data = response.content
                    self.load_pixmap(image_data)
                    return
                except requests.exceptions.RequestException as e:
                    print(f"Attempt {i+1} failed to load thumbnail: {e}")
                    time.sleep(1)
                except Exception as e:
                    print(f"An unexpected error occurred during thumbnail load: {e}")
                    break

            self.load_pixmap(None)
            self.image_label.setText("Failed")

        thread = Thread(target=fetch_image_with_retry)
        thread.start()

    def load_pixmap(self, image_data):
        pixmap = QPixmap()
        if image_data:
            pixmap.loadFromData(QByteArray(image_data))
        
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Failed")

    def download_image_clicked(self):
        self.download_requested.emit(self.download_url, self.file_extension)