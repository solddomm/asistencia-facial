from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from ui.widgets.photo_selector import PhotoSelector
from repositories.student_repository import StudentRepository

class StudentRegistrationPage(QWidget):
    def __init__(self):
        super().__init__()
        self.repo = StudentRepository()

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        container = QWidget()
        layout = QVBoxLayout(container)

        form = QFormLayout()

        # Inputs con las columnas de tu tabla
        self.input_nombre = QLineEdit()
        self.input_apellido = QLineEdit()
        self.input_dni = QLineEdit()
        self.input_carrera = QLineEdit()
        self.input_celular = QLineEdit()
        self.input_email = QLineEdit()
        self.input_fecha_nac = QLineEdit()
        self.input_fecha_nac.setPlaceholderText("dd/mm/aaaa")
        self.input_periodo_ingreso = QLineEdit()
        self.input_periodo_ingreso.setPlaceholderText("Ej: 2026")
        self.input_domicilio = QLineEdit()
        self.input_libreta = QLineEdit()

        form.addRow("Nombre:", self.input_nombre)
        form.addRow("Apellido:", self.input_apellido)
        form.addRow("DNI:", self.input_dni)
        form.addRow("Carrera:", self.input_carrera)
        form.addRow("Celular:", self.input_celular)
        form.addRow("Email:", self.input_email)
        form.addRow("Fecha de Nacimiento:", self.input_fecha_nac)
        form.addRow("Año / Periodo de ingreso:", self.input_periodo_ingreso)
        form.addRow("Domicilio:", self.input_domicilio)
        form.addRow("Número de libreta:", self.input_libreta)

        layout.addLayout(form)

        # Selectores de fotos
        self.photo_frontal = PhotoSelector("Ángulo Frontal")
        self.photo_izq = PhotoSelector("Ángulo Izquierdo")
        self.photo_der = PhotoSelector("Ángulo Derecho")

        layout.addWidget(self.photo_frontal)
        layout.addWidget(self.photo_izq)
        layout.addWidget(self.photo_der)

        # Botón Registrar
        self.btn_registrar = QPushButton("Registrar")
        self.btn_registrar.setStyleSheet("padding: 8px; font-weight: bold; background-color: #0275d8; color: white;")
        self.btn_registrar.clicked.connect(self.registrar_alumno)
        layout.addWidget(self.btn_registrar)

        scroll.setWidget(container)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def registrar_alumno(self):
        campos = {
            "nombre": self.input_nombre.text().strip(),
            "apellido": self.input_apellido.text().strip(),
            "dni": self.input_dni.text().strip(),
            "carrera": self.input_carrera.text().strip(),
            "celular": self.input_celular.text().strip(),
            "email": self.input_email.text().strip(),
            "fecha_nacimiento": self.input_fecha_nac.text().strip(),
            "periodo_ingreso": self.input_periodo_ingreso.text().strip(),
            "domicilio": self.input_domicilio.text().strip(),
            "num_libreta": self.input_libreta.text().strip()
        }

        # Validar campos vacíos
        if any(v == "" for v in campos.values()):
            QMessageBox.warning(self, "Campos incompletos", "Existen campos obligatorios sin completar.")
            return

        # Validar fotos
        foto_front = self.photo_frontal.get_image_path()
        foto_izq = self.photo_izq.get_image_path()
        foto_der = self.photo_der.get_image_path()

        if not foto_front or not foto_izq or not foto_der:
            QMessageBox.warning(self, "Fotos incompletas", "Debe cargar las fotografías Frontal, Izquierda y Derecha.")
            return

        # Validar fecha
        try:
            fecha_dt = datetime.strptime(campos["fecha_nacimiento"], "%d/%m/%Y").date()
            campos["fecha_nacimiento"] = fecha_dt
        except ValueError:
            QMessageBox.warning(self, "Fecha inválida", "La fecha de nacimiento debe tener formato dd/mm/aaaa.")
            return

        # Validar periodo de ingreso (número entero)
        try:
            campos["periodo_ingreso"] = int(campos["periodo_ingreso"])
        except ValueError:
            QMessageBox.warning(self, "Año inválido", "El periodo de ingreso debe ser un número entero.")
            return

        # Guardar en BD
        try:
            fotos = {
                "frontal": foto_front,
                "izquierdo": foto_izq,
                "derecho": foto_der
            }
            self.repo.create_student(campos, fotos)
            QMessageBox.information(self, "Éxito", "El alumno fue registrado exitosamente.")
            self.limpiar_formulario()
        except Exception as e:
            QMessageBox.critical(self, "Error en registro", f"No se pudo guardar el alumno:\n{e}")

    def limpiar_formulario(self):
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_dni.clear()
        self.input_carrera.clear()
        self.input_celular.clear()
        self.input_email.clear()
        self.input_fecha_nac.clear()
        self.input_periodo_ingreso.clear()
        self.input_domicilio.clear()
        self.input_libreta.clear()
        self.photo_frontal.borrar_foto()
        self.photo_izq.borrar_foto()
        self.photo_der.borrar_foto()