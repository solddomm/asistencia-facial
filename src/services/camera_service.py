import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

class CameraThread(QThread):
    # Emite el cuadro en formato QImage para la interfaz y el frame original de OpenCV
    frame_ready = Signal(QImage, object)
    error_occurred = Signal(str)

    def __init__(self, camera_index=0):
        super().__init__()
        self.camera_index = camera_index
        self._running = False
        self.cap = None

    def run(self):
        # Intentar con backend nativo de Windows (DSHOW) o por defecto
        self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            self.error_occurred.emit("No se pudo acceder a la cámara web.")
            return

        self._running = True

        while self._running:
            ret, frame = self.cap.read()
            if not ret or frame is None:
                continue

            # Convertir formato de color de BGR a RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w

            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
            self.frame_ready.emit(qt_image, frame)

        # Liberar el recurso al detener
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None

    def stop(self):
        self._running = False
        self.wait(1000)
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.cap = None