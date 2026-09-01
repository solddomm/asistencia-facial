from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class WelcomeWindow(QWidget):
    def __init__(self, nombre_completo: str):
        super().__init__()
        self.setWindowTitle("Bienvenido - Sistema de Asistencia")
        self.resize(400, 200)

        label = QLabel(f"¡Bienvenido, {nombre_completo}!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)