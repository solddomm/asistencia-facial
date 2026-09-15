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