from PySide6.QtWidgets import (
    QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox
)
from repositories.user_repository import UserRepository
from ui.welcome_window import WelcomeWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = UserRepository()
        self.welcome_window = None
        self.setWindowTitle("Inicio de sesión")
        self.resize(420, 260)

        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Usuario / Email / DNI / CUIL")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.clicked.connect(self.iniciar_sesion)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Inicio de sesión"))
        layout.addWidget(self.identifier_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        self.setLayout(layout)

    def iniciar_sesion(self):
        identificador = self.identifier_input.text().strip()
        contrasenia = self.password_input.text().strip()

        if identificador == "" or contrasenia == "":
            QMessageBox.warning(self, "Datos incompletos", "Ingrese usuario y contraseña.")
            return

        try:
            user_data = self.repo.find_by_credentials(identificador, contrasenia)
        except Exception as e:
            QMessageBox.critical(self, "Error de Conexión", f"Error con la base de datos:\n{str(e)}")
            return

        if user_data is None:
            QMessageBox.critical(self, "Error", "Credenciales incorrectas.")
            return

        nombre_mostrar = f"{user_data[5]} {user_data[6]}".strip() or user_data[1]

        self.welcome_window = WelcomeWindow(nombre_mostrar)
        self.welcome_window.show()
        self.close()