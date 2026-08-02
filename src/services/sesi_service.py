import sqlite3
import os
import json
from datetime import datetime
from services.cloud_sync import CloudSyncService
from services.klien_service import KlienService

class SesiService:
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'physioanx.db')
        self.cloud_sync = CloudSyncService()
        self.klien_db = KlienService()
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS sesi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            klien_id INTEGER NOT NULL,
            tanggal_sesi TEXT NOT NULL,
            durasi_detik INTEGER,
            avg_hr REAL,
            avg_gsr REAL,
            avg_temp REAL,
            data_grafik TEXT,
            FOREIGN KEY (klien_id) REFERENCES klien (id)
        )
        """
        with self._get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def simpan_sesi(self, klien_id, durasi_detik, avg_hr, avg_gsr, avg_temp, arr_hr, arr_gsr, arr_temp):
        data_grafik = json.dumps({
            "hr": arr_hr,
            "gsr": arr_gsr,
            "temp": arr_temp
        })

        tanggal_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = """
        INSERT INTO sesi (klien_id, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                klien_id, tanggal_sekarang, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik
            ))

            cursor.execute("UPDATE klien SET kunjungan_terakhir = ? WHERE id = ?",
                           (tanggal_sekarang.split()[0], klien_id))
            conn.commit()

        klien = self.klien_db.get_klien_by_id(klien_id)
        if klien:
            self.cloud_sync.sync_simpan_sesi(
                klien['id_klien'], tanggal_sekarang, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik
            )

        return True

    def get_all_riwayat(self, search_query="", filter_tanggal="", filter_jk="", filter_hasil=""):
        query = """
        SELECT s.id, s.tanggal_sesi, s.durasi_detik, s.avg_hr, s.avg_gsr, s.avg_temp, k.nama, k.jenis_kelamin
        FROM sesi s
        JOIN klien k ON s.klien_id = k.id
        WHERE 1=1
        """
        params = []

        if search_query:
            query += " AND (k.nama LIKE ? OR s.tanggal_sesi LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        if filter_tanggal:
            query += " AND s.tanggal_sesi LIKE ?"
            params.append(f"{filter_tanggal}%")

        if filter_jk and filter_jk != "Semua":
            query += " AND k.jenis_kelamin = ?"
            params.append(filter_jk)

        if filter_hasil and filter_hasil != "Semua Hasil":
            if filter_hasil == "Normal to Mild":
                query += " AND CAST(s.avg_hr AS FLOAT) <= 80"
            elif filter_hasil == "Mild to Moderate":
                query += " AND CAST(s.avg_hr AS FLOAT) > 80 AND CAST(s.avg_hr AS FLOAT) <= 95"
            elif filter_hasil == "Moderate to Severe":
                query += " AND CAST(s.avg_hr AS FLOAT) > 95 AND CAST(s.avg_hr AS FLOAT) <= 110"
            elif filter_hasil == "Severe":
                query += " AND CAST(s.avg_hr AS FLOAT) > 110"

        query += " ORDER BY s.id DESC"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_riwayat_by_klien(self, klien_id):
        query = """
        SELECT id, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp
        FROM sesi WHERE klien_id = ? ORDER BY id DESC
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (klien_id,))
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_detail_sesi(self, sesi_id):
        query = "SELECT * FROM sesi WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (sesi_id,))
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None

    def delete_sesi(self, sesi_id):
        detail = self.get_detail_sesi(sesi_id)
        if not detail:
            return False

        query = "DELETE FROM sesi WHERE id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (sesi_id,))
            conn.commit()

        self.cloud_sync.sync_delete_sesi(sesi_id, detail['tanggal_sesi'])
        return True
