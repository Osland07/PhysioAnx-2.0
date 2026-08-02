import sqlite3
import os
from datetime import datetime
from services.cloud_sync import CloudSyncService

class KlienService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'physioanx.db')
        self.cloud_sync = CloudSyncService()

        self.cloud_sync.run_in_background(self.cloud_sync.pull_all_from_cloud, self.db_path)
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS klien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_klien TEXT UNIQUE,
            nama TEXT NOT NULL,
            jenis_kelamin TEXT,
            tanggal_lahir TEXT,
            alamat TEXT,
            no_hp TEXT,
            email TEXT,
            kunjungan_terakhir TEXT
        )
        """
        with self._get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def get_all_klien(self, search_query=""):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search_query:
                query = "SELECT * FROM klien WHERE nama LIKE ? OR id_klien LIKE ?"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute("SELECT * FROM klien ORDER BY id DESC")

            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_klien(self, data):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(id) FROM klien")
            count = cursor.fetchone()[0] + 1
            id_klien = f"KLN-{str(count).zfill(3)}"

            tanggal_sekarang = datetime.now().strftime("%d-%B-%Y")

            cursor.execute(
                """INSERT INTO klien (id_klien, nama, jenis_kelamin, tanggal_lahir, alamat, no_hp, email, kunjungan_terakhir)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (id_klien, data['nama'], data['jenis_kelamin'], data['tanggal_lahir'],
                 data['alamat'], data['no_hp'], data['email'], tanggal_sekarang)
            )
            conn.commit()

            self.cloud_sync.sync_add_klien(data, id_klien, tanggal_sekarang)

            return True

    def get_klien_by_id(self, id_db):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM klien WHERE id=?", (id_db,))
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

    def update_klien(self, id_db, data):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """UPDATE klien SET nama=?, jenis_kelamin=?, tanggal_lahir=?,
                   alamat=?, no_hp=?, email=? WHERE id=?""",
                (data['nama'], data['jenis_kelamin'], data['tanggal_lahir'],
                 data['alamat'], data['no_hp'], data['email'], id_db)
            )
            conn.commit()

            klien = self.get_klien_by_id(id_db)
            if klien:
                self.cloud_sync.sync_add_klien(data, klien['id_klien'], klien['kunjungan_terakhir'])

            return True

    def delete_klien(self, id_db):
        klien = self.get_klien_by_id(id_db)
        if not klien:
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM klien WHERE id=?", (id_db,))
            conn.commit()

            self.cloud_sync.sync_delete_klien(klien['id_klien'])

            return True
