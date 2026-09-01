from config.database import get_connection

class UserRepository:
    def find_by_credentials(self, identificador: str, contrasenia: str):
        query = """
            SELECT id, usuario, email, dni, cuil, nombre, apellido
            FROM usuario
            WHERE contrasena = %s
              AND (
                    usuario = %s
                 OR email = %s
                 OR dni = %s
                 OR cuil = %s
              )
            LIMIT 1;
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    query,
                    (contrasenia, identificador, identificador, identificador, identificador)
                )
                return cur.fetchone()