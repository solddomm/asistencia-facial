from config.database import get_connection

class StudentRepository:
    def create_student(self, student_data, fotos):
        """
        Inserta el alumno en tu tabla 'alumno' y las tres rutas en 'captura_facial'.
        """
        insert_alumno_sql = """
            INSERT INTO alumno (
                nombre, apellido, dni, carrera, celular,
                email, fecha_nacimiento, periodo_ingreso,
                domicilio, num_libreta
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """

        insert_captura_sql = """
            INSERT INTO captura_facial (
                alumno_id, foto_frontal, foto_izquierdo, foto_derecho
            )
            VALUES (%s, %s, %s, %s);
        """

        with get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Guardar datos en tabla alumno
                cur.execute(insert_alumno_sql, (
                    student_data["nombre"],
                    student_data["apellido"],
                    student_data["dni"],
                    student_data["carrera"],
                    student_data["celular"],
                    student_data["email"],
                    student_data["fecha_nacimiento"],
                    student_data["periodo_ingreso"],
                    student_data["domicilio"],
                    student_data["num_libreta"]
                ))
                alumno_id = cur.fetchone()[0]

                # 2. Guardar rutas de imágenes en tabla captura_facial
                cur.execute(insert_captura_sql, (
                    alumno_id,
                    fotos["frontal"],
                    fotos["izquierdo"],
                    fotos["derecho"]
                ))

            conn.commit()
            return alumno_id

    def get_all_students_with_photos(self):
        """
        Devuelve la lista de alumnos con sus rutas de captura facial para generar embeddings.
        """
        query = """
            SELECT a.id, a.nombre, a.apellido, cf.foto_frontal, cf.foto_izquierdo, cf.foto_derecho
            FROM alumno a
            INNER JOIN captura_facial cf ON a.id = cf.alumno_id;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

        alumnos = []
        for r in rows:
            alumnos.append({
                "id": r[0],
                "nombre": r[1],
                "apellido": r[2],
                "foto_frontal": r[3],
                "foto_izquierdo": r[4],
                "foto_derecho": r[5]
            })
        return alumnos