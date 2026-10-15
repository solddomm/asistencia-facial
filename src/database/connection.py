import os
import psycopg2

def get_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "asistencia_facial"),
            user=os.getenv("DB_USER", "admin"),
            password=os.getenv("DB_PASSWORD", "admin123")
        )
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        return None