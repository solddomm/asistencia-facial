import time
import cv2
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

from services.embedding_service import EmbeddingService
from repositories.student_repository import StudentRepository
from repositories.attendance_repository import AttendanceRepository


class AttendancePage(QWidget):
    def __init__(self, horarios_page=None):
        super().__init__()
        self.horarios_page = horarios_page
        self.is_camera_open = False

        # OpenCV y Clasificador Haar Cascade oficial
        self.cap = None
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        # Servicios y repositorios
        self.embedding_service = EmbeddingService(model_name="Facenet512", threshold=0.40)
        self.student_repository = StudentRepository()
        self.registered_embeddings = []

        # Control de intervalos de reconocimiento (~2 seg)
        self.last_recognition_time = 0
        self.recognition_interval = 2.0
        self.is_processing = False

        # Timer para renderizar frames (~30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._actualizar_frame)

        # Interfaz de usuario
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("Asistencia por Captura Facial")
        title.setStyleSheet("font-size: 16px; font-weight: normal; color: #212529;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Panel de visualización de video
        self.camera_panel = QLabel("Cámara cerrada")
        self.camera_panel.setAlignment(Qt.AlignCenter)
        self.camera_panel.setMinimumHeight(380)
        self.camera_panel.setStyleSheet("""
            QLabel {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: #1a1a1a;
                color: #ffffff;
                font-size: 13px;
                font-weight: normal;
            }
        """)
        layout.addWidget(self.camera_panel)

        # Labels de retroalimentación de estado
        self.lbl_estado_rostro = QLabel("Estado: Cámara cerrada")
        self.lbl_estado_rostro.setAlignment(Qt.AlignCenter)
        self.lbl_estado_rostro.setStyleSheet("font-size: 13px; font-weight: bold; color: #495057;")
        layout.addWidget(self.lbl_estado_rostro)

        self.lbl_estado_asistencia = QLabel("")
        self.lbl_estado_asistencia.setAlignment(Qt.AlignCenter)
        self.lbl_estado_asistencia.setStyleSheet("font-size: 13px; font-weight: bold; color: #0d6efd;")
        layout.addWidget(self.lbl_estado_asistencia)

        # Botones de control de cámara
        self.open_camera_button = QPushButton("Abrir Cámara")
        self.close_camera_button = QPushButton("Cerrar Cámara")

        self.open_camera_button.clicked.connect(self.open_camera)
        self.close_camera_button.clicked.connect(self.close_camera)

        layout.addWidget(self.open_camera_button)
        layout.addWidget(self.close_camera_button)
        layout.addStretch()

        self.close_camera()

        # Conectar señal de jornada para cierre automático si se edita/termina
        if self.horarios_page:
            self.horarios_page.configuracion_cambiada.connect(self.verificar_cierre_automatico)

    def cerrar_camara(self):
        """Método público para compatibilidad con MainWindow."""
        self.close_camera()

    def open_camera(self):
        if not self.horarios_page or not self.horarios_page.is_configured():
            QMessageBox.warning(
                self,
                "Jornada sin guardar o en edición",
                "Antes de abrir la cámara debe existir una Jornada guardada y no estar en modo edición."
            )
            return

        # Cargar referencias de alumnos registrados para la sesión
        try:
            alumnos = self.student_repository.get_all_students_with_photos()
            self.registered_embeddings = self.embedding_service.load_registered_embeddings(alumnos)
        except Exception as e:
            print(f"[AttendancePage] Error cargando alumnos registrados: {e}")
            self.registered_embeddings = []

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error de Cámara", "No se pudo acceder a la webcam.")
            return

        self.is_camera_open = True
        self.is_processing = False
        self.last_recognition_time = 0

        self.open_camera_button.setEnabled(False)
        self.close_camera_button.setEnabled(True)
        self.lbl_estado_rostro.setText("Estado: Esperando rostro")
        self.lbl_estado_asistencia.setText("")

        self._estilos_botones_activos()
        self.timer.start(30)

    def close_camera(self):
        self.is_camera_open = False
        self.timer.stop()

        if self.cap:
            self.cap.release()
            self.cap = None

        self.camera_panel.clear()
        self.camera_panel.setText("Cámara cerrada")
        self.lbl_estado_rostro.setText("Estado: Cámara cerrada")
        self.lbl_estado_asistencia.setText("")

        self.open_camera_button.setEnabled(True)
        self.close_camera_button.setEnabled(False)
        self._estilos_botones_inactivos()

    def _actualizar_frame(self):
        if not self.cap or not self.is_camera_open:
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        # Espejar imagen para visualización natural
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detección facial con Haar Cascade
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        num_faces = len(faces)

        if num_faces == 0:
            self.lbl_estado_rostro.setText("Estado: Esperando rostro")
        elif num_faces > 1:
            self.lbl_estado_rostro.setText("Estado: Más de un rostro detectado")
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        elif num_faces == 1:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Evaluar intervalo de tiempo para reconocimiento
            ahora = time.time()
            if not self.is_processing and (ahora - self.last_recognition_time >= self.recognition_interval):
                self.is_processing = True
                self.last_recognition_time = ahora
                self.lbl_estado_rostro.setText("Estado: Procesando reconocimiento...")

                # Recorte del rostro
                face_crop = frame[y:y + h, x:x + w].copy()
                self._procesar_reconocimiento_y_asistencia(face_crop)
                self.is_processing = False

        # Convertir a QImage y mostrar en la UI
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        alto, ancho, canales = rgb_frame.shape
        q_img = QImage(rgb_frame.data, ancho, alto, canales * ancho, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_img).scaled(
            self.camera_panel.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.camera_panel.setPixmap(pixmap)

    def _procesar_reconocimiento_y_asistencia(self, face_crop):
        current_emb = self.embedding_service.extract_embedding(face_crop)
        if current_emb is None:
            self.lbl_estado_rostro.setText("Estado: No se pudo procesar el rostro")
            return

        best_match, min_dist, is_recognized = self.embedding_service.find_best_match(
            current_emb, self.registered_embeddings
        )

        if not is_recognized or best_match is None:
            dist_str = f"{min_dist:.2f}" if min_dist != float("inf") else "--"
            self.lbl_estado_rostro.setText(f"Estado: Rostro no reconocido (Distancia: {dist_str})")
            return

        # Rostro reconocido
        alumno_id = best_match["alumno_id"]
        nombre = best_match["nombre"]
        self.lbl_estado_rostro.setText(f"Reconocido: {nombre} (Dist: {min_dist:.2f})")

        # Procesar asistencia con la jornada activa
        jornada_activa = self.horarios_page.get_jornada_activa() if self.horarios_page else None
        if not jornada_activa or not jornada_activa.get("id"):
            self.lbl_estado_asistencia.setText("Error: Sin Jornada activa")
            return

        horarios_id = jornada_activa["id"]
        hora_salida_str = jornada_activa["hora_salida"]

        _, mensaje = AttendanceRepository.procesar_asistencia(
            horarios_id=horarios_id,
            alumno_id=alumno_id,
            hora_salida_str=hora_salida_str
        )
        self.lbl_estado_asistencia.setText(mensaje)

    def verificar_cierre_automatico(self):
        if self.is_camera_open:
            if not self.horarios_page or not self.horarios_page.is_configured():
                self.close_camera()

    def _estilos_botones_activos(self):
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

    def _estilos_botones_inactivos(self):
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