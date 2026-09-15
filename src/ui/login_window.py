from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)
from repositories.user_repository import UserRepository
from ui.main_window import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = UserRepository()
        self.main_window = None

        self.setWindowTitle("Inicio de sesión")
        self.resize(360, 260)

        layout = QVBoxLayout(self)

        title = QLabel("Inicio de sesión")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.input_identificador = QLineEdit()
        self.input_identificador.setPlaceholderText("Usuario / Email / DNI / CUIL")
        layout.addWidget(self.input_identificador)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        self.btn_login = QPushButton("Iniciar sesión")
        self.btn_login.clicked.connect(self.iniciar_sesion)
        layout.addWidget(self.btn_login)

    def iniciar_sesion(self):
        identificador = self.input_identificador.text().strip()
        contrasenia = self.input_password.text().strip()

        if not identificador or not contrasenia:
            QMessageBox.warning(self, "Datos incompletos", "Ingrese usuario y contraseña.")
            return

        usuario = self.repo.find_by_credentials(identificador, contrasenia)

        if usuario is None:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")
            return

        # Abre la nueva ventana principal y cierra el login
        self.main_window = MainWindow(nombre_usuario=usuario[1])
        self.main_window.show()
        self.close()