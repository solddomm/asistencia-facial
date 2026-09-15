from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget
)
from ui.pages.attendance_page import AttendancePage
from ui.pages.horarios_config_page import HorariosConfigPage
from ui.pages.student_registration_page import StudentRegistrationPage

class MainWindow(QMainWindow):
    def __init__(self, nombre_usuario=""):
        super().__init__()
        self.setWindowTitle("Sistema de Asistencia por Reconocimiento Facial")
        self.resize(980, 700)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #f5f5f5; color: #111111;")
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Menú lateral clásico
        menu_widget = QWidget()
        menu_widget.setFixedWidth(240)
        menu_widget.setStyleSheet("""
            QWidget {
                background-color: #e9ecef;
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QLabel {
                color: #212529;
                font-size: 13px;
                border: none;
            }
            QPushButton {
                background-color: #ffffff;
                color: #212529;
                border: 1px solid #adb5bd;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
        """)

        menu_layout = QVBoxLayout(menu_widget)
        menu_layout.setContentsMargins(12, 16, 12, 16)
        menu_layout.setSpacing(10)

        self.user_label = QLabel(f"Bienvenido, {nombre_usuario}")
        self.user_label.setStyleSheet("font-weight: bold; margin-bottom: 10px;")
        menu_layout.addWidget(self.user_label)

        self.btn_asistencia = QPushButton("Asistencia por Captura Facial")
        self.btn_horarios = QPushButton("Configuración de Horarios")
        self.btn_alumno = QPushButton("Registrar Alumno")

        menu_layout.addWidget(self.btn_asistencia)
        menu_layout.addWidget(self.btn_horarios)
        menu_layout.addWidget(self.btn_alumno)
        menu_layout.addStretch()

        main_layout.addWidget(menu_widget)

        # Contenedor central de páginas
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 4px;")
        main_layout.addWidget(self.stack)

        self.horarios_page = HorariosConfigPage()
        self.attendance_page = AttendancePage(horarios_page=self.horarios_page)
        self.student_page = StudentRegistrationPage()

        self.stack.addWidget(self.attendance_page)
        self.stack.addWidget(self.horarios_page)
        self.stack.addWidget(self.student_page)

        self.btn_asistencia.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_horarios.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_alumno.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.stack.setCurrentIndex(0)