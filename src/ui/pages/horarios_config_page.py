from datetime import datetime
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit
from PySide6.QtCore import Qt, Signal

class HorariosConfigPage(QWidget):
    configuracion_cambiada = Signal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

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
        layout.addStretch()

        # Emitir al instante en cualquier cambio
        self.entrada_input.textChanged.connect(self._notificar_cambio)
        self.salida_input.textChanged.connect(self._notificar_cambio)
        self.catedra_input.textChanged.connect(self._notificar_cambio)

    def _notificar_cambio(self):
        self.configuracion_cambiada.emit()

    def is_configured(self):
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