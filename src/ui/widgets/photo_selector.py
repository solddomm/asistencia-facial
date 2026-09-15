from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class PhotoSelector(QWidget):
    def __init__(self, title):
        super().__init__()
        self.image_path = None

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 6, 0, 6)
        main_layout.setSpacing(6)

        # Título sin negrita
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #212529; font-size: 13px; font-weight: normal;")
        main_layout.addWidget(self.title_label)

        # Contenedor con borde completo y limpio
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #ffffff;
            }
        """)

        card_layout = QVBoxLayout(container)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_cargar = QPushButton("Cargar Foto")
        self.btn_tomar = QPushButton("Tomar Foto")
        self.btn_borrar = QPushButton("🗑")
        self.btn_borrar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: normal;
                padding: 5px 10px;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #bb2d3b;
            }
        """)
        self.btn_borrar.setVisible(False)

        for btn in [self.btn_cargar, self.btn_tomar]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f8f9fa;
                    color: #212529;
                    border: 1px solid #ced4da;
                    border-radius: 3px;
                    padding: 5px 12px;
                    font-size: 12px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #e2e6ea;
                }
            """)

        btn_layout.addWidget(self.btn_cargar)
        btn_layout.addWidget(self.btn_tomar)
        btn_layout.addWidget(self.btn_borrar)
        btn_layout.addStretch()
        card_layout.addLayout(btn_layout)

        # Previsualización
        self.preview = QLabel("Sin imagen todavía")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setFixedSize(220, 140)
        self.preview.setStyleSheet("""
            QLabel {
                border: 1px dashed #6c757d;
                background-color: #fafafa;
                color: #495057;
                font-size: 12px;
                font-weight: normal;
            }
        """)
        card_layout.addWidget(self.preview, alignment=Qt.AlignCenter)

        main_layout.addWidget(container)

        self.btn_cargar.clicked.connect(self.cargar_foto)
        self.btn_borrar.clicked.connect(self.borrar_foto)

    def cargar_foto(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen", "", "Imágenes (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                QMessageBox.critical(self, "Error", "El archivo seleccionado no es una imagen válida.")
                return
            self.image_path = file_path
            self.preview.setPixmap(pixmap.scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.btn_borrar.setVisible(True)

    def borrar_foto(self):
        self.image_path = None
        self.preview.clear()
        self.preview.setText("Sin imagen todavía")
        self.btn_borrar.setVisible(False)

    def get_image_path(self):
        return self.image_path