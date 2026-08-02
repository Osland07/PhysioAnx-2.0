import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class DatabaseService:
    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL belum diatur di .env")

    def get_connection(self):
        """Membuat dan mengembalikan koneksi PostgreSQL baru"""
        return psycopg2.connect(self.db_url, cursor_factory=DictCursor)

    def execute_query(self, query, params=None, commit=False, fetchone=False, fetchall=False):
        """Helper untuk menjalankan query dengan aman dan menutup koneksi"""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                if commit:
                    conn.commit()

                if fetchone:
                    return dict(cursor.fetchone()) if cursor.rowcount > 0 else None
                elif fetchall:
                    return [dict(row) for row in cursor.fetchall()]

            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Database Error: {e}")
            raise e
        finally:
            if conn:
                conn.close()
