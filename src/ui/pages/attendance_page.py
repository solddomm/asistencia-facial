from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

class AttendancePage(QWidget):
    def __init__(self, horarios_page=None):
        super().__init__()
        self.horarios_page = horarios_page
        self.is_camera_open = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Asistencia por Captura Facial")
        title.setStyleSheet("font-size: 16px; font-weight: normal; color: #212529;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.camera_panel = QLabel("La captura de video se implementará en el próximo incremento.")
        self.camera_panel.setAlignment(Qt.AlignCenter)
        self.camera_panel.setMinimumHeight(280)
        self.camera_panel.setStyleSheet("""
            QLabel {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #fafafa;
                color: #6c757d;
                font-size: 13px;
                font-weight: normal;
            }
        """)
        layout.addWidget(self.camera_panel)

        self.open_camera_button = QPushButton("Abrir Cámara")
        self.close_camera_button = QPushButton("Cerrar Cámara")

        self.open_camera_button.clicked.connect(self.open_camera)
        self.close_camera_button.clicked.connect(self.close_camera)

        layout.addWidget(self.open_camera_button)
        layout.addWidget(self.close_camera_button)
        layout.addStretch()

        self.close_camera()

        # Conectar señal de horarios directamente al verificador
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

        self.is_camera_open = True
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
        self.is_camera_open = False
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

    def verificar_cierre_automatico(self):
        # Apenas deje de estar completo cualquier campo, si la cámara está abierta se cierra sola
        if self.is_camera_open:
            if not self.horarios_page or not self.horarios_page.is_configured():
                self.close_camera()
                