from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from repositories.schedule_repository import ScheduleRepository


class HorariosConfigPage(QWidget):
    configuracion_cambiada = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.jornada_id = None
        self.en_edicion = False

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        title = QLabel("Configuración de Horarios")
        title.setStyleSheet("font-size: 16px; font-weight: normal; color: #212529;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        self.fecha_label = QLabel(fecha_actual)
        self.fecha_label.setStyleSheet("color: #212529; font-weight: normal;")
        form.addRow("Fecha:", self.fecha_label)

        self.entrada_input = QLineEdit()
        self.entrada_input.setInputMask("99:99")
        self.entrada_input.setText("")
        self.entrada_input.setPlaceholderText("--:--")
        form.addRow("Horario de entrada:", self.entrada_input)

        self.salida_input = QLineEdit()
        self.salida_input.setInputMask("99:99")
        self.salida_input.setText("")
        self.salida_input.setPlaceholderText("--:--")
        form.addRow("Horario de salida:", self.salida_input)

        self.catedra_input = QLineEdit()
        self.catedra_input.setPlaceholderText("Ingrese la cátedra")
        form.addRow("Cátedra:", self.catedra_input)

        layout.addLayout(form)

        # Botones de gestión de Jornada (Sección 5 Requisitos)
        botones_layout = QHBoxLayout()
        botones_layout.setSpacing(10)

        self.btn_guardar = QPushButton("Guardar Jornada")
        self.btn_guardar.setEnabled(False)
        self.btn_guardar.clicked.connect(self._guardar_jornada)
        botones_layout.addWidget(self.btn_guardar)

        self.btn_editar = QPushButton("Editar Jornada")
        self.btn_editar.setVisible(False)
        self.btn_editar.clicked.connect(self._editar_jornada)
        botones_layout.addWidget(self.btn_editar)

        self.btn_terminar = QPushButton("Terminar Jornada")
        self.btn_terminar.setVisible(False)
        self.btn_terminar.clicked.connect(self._terminar_jornada)
        botones_layout.addWidget(self.btn_terminar)

        layout.addLayout(botones_layout)
        layout.addStretch()

        # Validar en cada cambio
        self.entrada_input.textChanged.connect(self._validar_formulario)
        self.salida_input.textChanged.connect(self._validar_formulario)
        self.catedra_input.textChanged.connect(self._validar_formulario)

    def _validar_formulario(self):
        valido = self._son_datos_validos()
        if not self.jornada_id or self.en_edicion:
            self.btn_guardar.setEnabled(valido)
        self.configuracion_cambiada.emit()

    def _son_datos_validos(self):
        hora_entrada = self.entrada_input.text().strip()
        hora_salida = self.salida_input.text().strip()
        catedra = self.catedra_input.text().strip()

        if not hora_entrada or ":" not in hora_entrada or len(hora_entrada) < 5 or " " in hora_entrada:
            return False
        if not hora_salida or ":" not in hora_salida or len(hora_salida) < 5 or " " in hora_salida:
            return False
        if not catedra:
            return False

        return True

    def _guardar_jornada(self):
        hora_entrada = self.entrada_input.text().strip()
        hora_salida = self.salida_input.text().strip()
        catedra = self.catedra_input.text().strip()

        if self.en_edicion and self.jornada_id:
            # UPDATE del mismo registro
            ok = ScheduleRepository.actualizar_jornada(
                self.jornada_id, catedra, hora_entrada, hora_salida
            )
            if ok:
                self.en_edicion = False
                self._aplicar_estado_guardado()
                self.configuracion_cambiada.emit()
            else:
                QMessageBox.critical(self, "Error", "No se pudo actualizar la jornada en la base de datos.")
        else:
            # INSERT nueva jornada
            nuevo_id = ScheduleRepository.crear_jornada(catedra, hora_entrada, hora_salida)
            if nuevo_id:
                self.jornada_id = nuevo_id
                self.en_edicion = False
                self._aplicar_estado_guardado()
                self.configuracion_cambiada.emit()
            else:
                QMessageBox.critical(self, "Error", "No se pudo guardar la jornada en la base de datos.")

    def _editar_jornada(self):
        self.en_edicion = True
        self.entrada_input.setEnabled(True)
        self.salida_input.setEnabled(True)
        self.catedra_input.setEnabled(True)

        self.btn_guardar.setVisible(True)
        self.btn_guardar.setEnabled(True)
        self.btn_editar.setVisible(False)
        self.btn_terminar.setVisible(True)

        self.configuracion_cambiada.emit()

    def _terminar_jornada(self):
        # Olvida la sesión activa sin borrar de la base
        self.jornada_id = None
        self.en_edicion = False

        self.entrada_input.clear()
        self.salida_input.clear()
        self.catedra_input.clear()

        self.entrada_input.setEnabled(True)
        self.salida_input.setEnabled(True)
        self.catedra_input.setEnabled(True)

        self.btn_guardar.setVisible(True)
        self.btn_guardar.setEnabled(False)
        self.btn_editar.setVisible(False)
        self.btn_terminar.setVisible(False)

        self.configuracion_cambiada.emit()

    def _aplicar_estado_guardado(self):
        self.entrada_input.setEnabled(False)
        self.salida_input.setEnabled(False)
        self.catedra_input.setEnabled(False)

        self.btn_guardar.setVisible(False)
        self.btn_editar.setVisible(True)
        self.btn_terminar.setVisible(True)

    def is_configured(self):
        """Devuelve True sólo si la jornada está guardada en la base y no está en edición."""
        return self.jornada_id is not None and not self.en_edicion

    def get_jornada_activa(self):
        return {
            "id": self.jornada_id,
            "hora_entrada": self.entrada_input.text().strip(),
            "hora_salida": self.salida_input.text().strip(),
            "catedra": self.catedra_input.text().strip()
        }