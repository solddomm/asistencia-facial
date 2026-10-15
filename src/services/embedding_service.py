import os
import cv2
import numpy as np
from deepface import DeepFace


class EmbeddingService:
    def __init__(self, model_name="Facenet512", threshold=0.40):
        self.model_name = model_name
        self.threshold = threshold

    def extract_embedding(self, img):
        """
        Genera el vector de 512 valores a partir de una ruta de imagen o un array de OpenCV (BGR).
        """
        try:
            if isinstance(img, str):
                if not os.path.exists(img):
                    return None
                img_input = cv2.imread(img)
                if img_input is None:
                    return None
            else:
                img_input = img

            # DeepFace espera formato RGB
            img_rgb = cv2.cvtColor(img_input, cv2.COLOR_BGR2RGB)

            # Se usa detector_backend='skip' porque el recorte ya fue realizado
            representaciones = DeepFace.represent(
                img_path=img_rgb,
                model_name=self.model_name,
                enforce_detection=False,
                detector_backend="skip"
            )

            if representaciones and len(representaciones) > 0:
                vector = np.array(representaciones[0]["embedding"], dtype=np.float32)
                return vector

            return None
        except Exception as e:
            print(f"[EmbeddingService] Error extrayendo embedding: {e}")
            return None

    @staticmethod
    def cosine_distance(vec_a, vec_b):
        """
        Calcula la distancia coseno entre dos vectores numéricos:
        distancia = 1 - (A . B) / (norm(A) * norm(B))
        """
        norm_a = np.linalg.norm(vec_a)
        norm_b = np.linalg.norm(vec_b)

        if norm_a == 0 or norm_b == 0:
            return 1.0

        dot_product = np.dot(vec_a, vec_b)
        similarity = dot_product / (norm_a * norm_b)
        # Asegurar rango de similitud [-1, 1] por precisión flotante
        similarity = np.clip(similarity, -1.0, 1.0)
        return float(1.0 - similarity)

    def find_best_match(self, current_emb, registered_faces):
        """
        Compara el vector actual contra todas las referencias de los alumnos.
        Devuelve (best_match_info, min_distance, is_recognized).
        """
        if current_emb is None or not registered_faces:
            return None, float("inf"), False

        min_dist = float("inf")
        best_match = None

        for item in registered_faces:
            ref_emb = item["embedding"]
            dist = self.cosine_distance(current_emb, ref_emb)

            if dist < min_dist:
                min_dist = dist
                best_match = item

        is_recognized = (min_dist <= self.threshold)
        return best_match, min_dist, is_recognized

    def load_registered_embeddings(self, students_with_photos):
        """
        Carga y calcula los embeddings de las 3 fotografías por cada alumno registrado.
        """
        registered = []
        for student in students_with_photos:
            student_id = student.get("id")
            nombre = f"{student.get('nombre', '')} {student.get('apellido', '')}".strip()

            for angulo in ["foto_frontal", "foto_izquierdo", "foto_derecho"]:
                path = student.get(angulo)
                if path and os.path.exists(path):
                    emb = self.extract_embedding(path)
                    if emb is not None:
                        registered.append({
                            "alumno_id": student_id,
                            "nombre": nombre,
                            "angulo": angulo,
                            "embedding": emb
                        })

        return registered