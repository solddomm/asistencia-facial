import os
import cv2
from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from services.camera_service import CameraThread

class CameraCaptureDialog(QDialog):
    def __init__(self, parent=None, title="Capturar Fotografía"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(520, 440)

        self.last_frame = None
        self.saved_image_path = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Panel de visualización en vivo
        self.view_panel = QLabel("Iniciando cámara...")
        self.view_panel.setAlignment(Qt.AlignCenter)
        self.view_panel.setFixedSize(480, 320)
        self.view_panel.setStyleSheet("""
            QLabel {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #000000;
                color: #ffffff;
                font-size: 13px;
                font-weight: normal;
            }
        """)
        layout.addWidget(self.view_panel, alignment=Qt.AlignCenter)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_capturar = QPushButton("Capturar Fotografía")
        self.btn_capturar.setStyleSheet("""
            QPushButton {
                background-color: #0d6efd;
                color: #ffffff;
                font-weight: normal;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0b5ed7;
            }
        """)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: #ffffff;
                font-weight: normal;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #5c636a;
            }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_capturar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)

        self.btn_capturar.clicked.connect(self.capturar_foto)
        self.btn_cancelar.clicked.connect(self.reject)

        # Hilo de cámara
        self.camera_thread = CameraThread(camera_index=0)
        self.camera_thread.frame_ready.connect(self.actualizar_cuadro)
        self.camera_thread.error_occurred.connect(self.mostrar_error)
        self.camera_thread.start()

    def actualizar_cuadro(self, qt_image, frame):
        self.last_frame = frame
        pixmap = QPixmap.fromImage(qt_image)
        self.view_panel.setPixmap(
            pixmap.scaled(self.view_panel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def capturar_foto(self):
        if self.last_frame is None:
            QMessageBox.warning(self, "Atención", "No se ha recibido cuadro de la cámara todavía.")
            return

        carpeta_capturas = os.path.join(os.getcwd(), "capturas_temp")
        os.makedirs(carpeta_capturas, exist_ok=True)

        nombre_archivo = f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.jpg"
        ruta_archivo = os.path.join(carpeta_capturas, nombre_archivo)

        cv2.imwrite(ruta_archivo, self.last_frame)
        self.saved_image_path = ruta_archivo

        self.liberar_camara()
        self.accept()

    def mostrar_error(self, msg):
        QMessageBox.critical(self, "Error de Cámara", msg)
        self.reject()

    def liberar_camara(self):
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None

    def closeEvent(self, event):
        self.liberar_camara()
        super().closeEvent(event)

    def reject(self):
        self.liberar_camara()
        super().reject()