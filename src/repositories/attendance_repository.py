from datetime import datetime, date, timedelta
from database.connection import get_connection


class AttendanceRepository:
    @staticmethod
    def obtener_asistencia(horarios_id, alumno_id):
        """
        Busca si ya existe una fila de asistencia para la combinación horarios_id + alumno_id.
        """
        conn = get_connection()
        if not conn:
            return None

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, registro_entrada, registro_salida, estado
                    FROM asistencias
                    WHERE horarios_id = %s AND alumno_id = %s;
                    """,
                    (horarios_id, alumno_id)
                )
                return cur.fetchone()
        except Exception as e:
            print(f"[AttendanceRepository] Error al consultar asistencia: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def registrar_entrada(horarios_id, alumno_id):
        """
        Inserta la entrada (primera coincidencia) con salida en NULL.
        """
        conn = get_connection()
        if not conn:
            return False

        ahora = datetime.now()
        hoy = ahora.date()
        hora_actual = ahora.time()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO asistencias (alumno_id, horarios_id, fecha, registro_entrada, registro_salida, estado)
                    VALUES (%s, %s, %s, %s, NULL, %s);
                    """,
                    (alumno_id, horarios_id, hoy, hora_actual, "PRESENTE")
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"[AttendanceRepository] Error al registrar entrada: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def registrar_salida(asistencia_id):
        """
        Actualiza la misma fila completando registro_salida.
        """
        conn = get_connection()
        if not conn:
            return False

        hora_actual = datetime.now().time()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE asistencias
                    SET registro_salida = %s
                    WHERE id = %s;
                    """,
                    (hora_actual, asistencia_id)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"[AttendanceRepository] Error al registrar salida: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def procesar_asistencia(horarios_id, alumno_id, hora_salida_str):
        """
        Aplica las reglas funcionales del Incremento 5 y devuelve (estado, mensaje).
        """
        registro = AttendanceRepository.obtener_asistencia(horarios_id, alumno_id)

        # Caso 1: No existe registro -> Registrar Entrada
        if not registro:
            ok = AttendanceRepository.registrar_entrada(horarios_id, alumno_id)
            if ok:
                return "ENTRADA_OK", "Entrada registrada"
            return "ERROR", "Error al registrar entrada en la base de datos"

        asistencia_id, entrada, salida, estado = registro

        # Caso 2: Ya tiene entrada y salida -> Asistencia completa
        if salida is not None:
            return "COMPLETA", "Entrada y salida ya registradas para esta jornada"

        # Caso 3: Tiene entrada, evaluar salida según regla horaria (5 min antes de hora_salida)
        try:
            partes = hora_salida_str.split(":")
            h_salida = int(partes[0])
            m_salida = int(partes[1])

            ahora = datetime.now()
            dt_salida_jornada = ahora.replace(hour=h_salida, minute=m_salida, second=0, microsecond=0)
            dt_habilitada_desde = dt_salida_jornada - timedelta(minutes=5)

            if ahora < dt_habilitada_desde:
                return "TEMPRANO", "Entrada ya registrada; todavía no puede registrar salida"

            ok = AttendanceRepository.registrar_salida(asistencia_id)
            if ok:
                return "SALIDA_OK", "Salida registrada"
            return "ERROR", "Error al registrar salida en la base de datos"

        except Exception as e:
            print(f"[AttendanceRepository] Error calculando horario de salida: {e}")
            return "ERROR", "Error procesando validación horaria de salida"