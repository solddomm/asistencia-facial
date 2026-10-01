from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from services.camera_service import CameraThread

class AttendancePage(QWidget):
    def __init__(self, horarios_page=None):
        super().__init__()
        self.horarios_page = horarios_page
        self.camera_thread = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Asistencia por Captura Facial")
        title.setStyleSheet("font-size: 16px; font-weight: normal; color: #212529;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Panel para visualización de la cámara
        self.camera_panel = QLabel("Cámara apagada")
        self.camera_panel.setAlignment(Qt.AlignCenter)
        self.camera_panel.setMinimumHeight(380)
        self.camera_panel.setStyleSheet("""
            QLabel {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #000000;
                color: #ffffff;
                font-size: 13px;
                font-weight: normal;
            }
        """)
        layout.addWidget(self.camera_panel)

        # Botones de control
        self.open_camera_button = QPushButton("Abrir Cámara")
        self.close_camera_button = QPushButton("Cerrar Cámara")

        self.open_camera_button.clicked.connect(self.open_camera)
        self.close_camera_button.clicked.connect(self.close_camera)

        layout.addWidget(self.open_camera_button)
        layout.addWidget(self.close_camera_button)
        layout.addStretch()

        self.close_camera()

        if self.horarios_page:
            self.horarios_page.configuracion_cambiada.connect(self.verificar_cierre_automatico)

    def open_camera(self):
        if not self.horarios_page or not self.horarios_page.is_configured():
            QMessageBox.warning(
                self,
                "Horarios sin configurar",
                "Antes de abrir la Cámara del Sistema debe configurarse los parámetros de Horarios (segunda opción del Menú Lateral)."
            )
            return

        # Iniciar el hilo de la cámara
        self.camera_thread = CameraThread(camera_index=0)
        self.camera_thread.frame_ready.connect(self.actualizar_cuadro)
        self.camera_thread.error_occurred.connect(self.mostrar_error_camara)
        self.camera_thread.start()

        self.open_camera_button.setEnabled(False)
        self.close_camera_button.setEnabled(True)

        self.open_camera_button.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                color: #adb5bd;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                font-weight: normal;
            }
        """)

        self.close_camera_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: #ffffff;
                font-weight: normal;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #bb2d3b;
            }
        """)

    def close_camera(self):
        # Detener y liberar cámara
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.stop()
            self.camera_thread = None

        self.camera_panel.clear()
        self.camera_panel.setText("Cámara apagada")

        self.open_camera_button.setEnabled(True)
        self.close_camera_button.setEnabled(False)

        self.open_camera_button.setStyleSheet("""
            QPushButton {
                background-color: #198754;
                color: #ffffff;
                font-weight: normal;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #157347;
            }
        """)

        self.close_camera_button.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                color: #adb5bd;
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                font-weight: normal;
            }
        """)

    def actualizar_cuadro(self, qt_image, _frame):
        # Proyectar el cuadro de la cámara ajustado al tamaño del panel
        pixmap = QPixmap.fromImage(qt_image)
        self.camera_panel.setPixmap(
            pixmap.scaled(self.camera_panel.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def mostrar_error_camara(self, mensaje):
        QMessageBox.critical(self, "Error de Cámara", mensaje)
        self.close_camera()

    def verificar_cierre_automatico(self):
        # Si la cámara está activa y los datos de horarios dejan de ser válidos, apagar
        if self.camera_thread and self.camera_thread.isRunning():
            if not self.horarios_page or not self.horarios_page.is_configured():
                self.close_camera()
                