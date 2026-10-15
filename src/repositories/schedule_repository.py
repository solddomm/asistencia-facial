import psycopg2
from database.connection import get_connection


class ScheduleRepository:
    @staticmethod
    def crear_jornada(descripcion, hora_entrada, hora_salida, usuario_id=None):
        """
        Inserta una nueva jornada en la tabla horarios y devuelve su id generado.
        """
        conn = get_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO horarios (descripcion, hora_entrada, hora_salida, usuario_id)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (descripcion, hora_entrada, hora_salida, usuario_id)
                )
                jornada_id = cur.fetchone()[0]
                conn.commit()
                return jornada_id
        except Exception as e:
            conn.rollback()
            print(f"[ScheduleRepository] Error al crear jornada: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def actualizar_jornada(jornada_id, descripcion, hora_entrada, hora_salida):
        """
        Actualiza los datos de la jornada existente (mismo id).
        """
        conn = get_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE horarios
                    SET descripcion = %s, hora_entrada = %s, hora_salida = %s
                    WHERE id = %s;
                    """,
                    (descripcion, hora_entrada, hora_salida, jornada_id)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"[ScheduleRepository] Error al actualizar jornada: {e}")
            return False
        finally:
            conn.close()