import os
import psycopg2
import threading
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

class CloudSyncService:
    """Service berjalan di background (Local-First) untuk melakukan backup ke Neon DB"""
    _has_pulled_on_startup = False

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")

    def _get_connection(self):
        return psycopg2.connect(self.db_url, sslmode='require', connect_timeout=15)

    def run_in_background(self, task_func, *args):
        """Menjalankan fungsi dalam thread terpisah agar tidak mengganggu UI Flet"""
        thread = threading.Thread(target=task_func, args=args, daemon=True)
        thread.start()

    def start_auto_polling(self, local_db_path, interval_seconds=5):
        """Service daemon 5-detik dengan teknik hemat kuota (hanya pull jika tabel berubah)"""
        def polling_task():
            import time
            last_stats = None
            while True:
                time.sleep(interval_seconds)
                try:
                    with self._get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT sum(n_tup_ins + n_tup_upd + n_tup_del) FROM pg_stat_user_tables WHERE relname IN ('klien', 'sesi');")
                        current_stats = cursor.fetchone()[0]

                        if last_stats is None:
                            last_stats = current_stats
                        elif current_stats != last_stats:
                            print(f"[Auto-Polling] Perubahan terdeteksi di Cloud! Mengunduh data terbaru...")
                            self.pull_all_from_cloud(local_db_path, force=True)
                            last_stats = current_stats
                except Exception as e:
                    print(f"[Auto-Polling Error] {e}")

        self.run_in_background(polling_task)

    def _sync_add_klien_task(self, id_klien, nama, jenis_kelamin, tanggal_lahir, alamat, no_hp, email, kunjungan_terakhir):
        try:
            query = """
            INSERT INTO klien (id_klien, nama, jenis_kelamin, tanggal_lahir, alamat, no_hp, email, kunjungan_terakhir)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id_klien) DO UPDATE SET
            nama=EXCLUDED.nama, jenis_kelamin=EXCLUDED.jenis_kelamin,
            kunjungan_terakhir=EXCLUDED.kunjungan_terakhir;
            """
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (id_klien, nama, jenis_kelamin, tanggal_lahir, alamat, no_hp, email, kunjungan_terakhir))
                conn.commit()
        except Exception as e:
            print(f"[CloudSync] Gagal sync Klien: {e}")

    def sync_add_klien(self, data, id_klien, kunjungan_terakhir):
        self.run_in_background(
            self._sync_add_klien_task,
            id_klien, data['nama'], data['jenis_kelamin'], data['tanggal_lahir'],
            data['alamat'], data['no_hp'], data['email'], kunjungan_terakhir
        )

    def _sync_sesi_task(self, id_klien, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik):
        try:
            query_get_klien = "SELECT id FROM klien WHERE id_klien = %s"

            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_get_klien, (id_klien,))
                    row = cursor.fetchone()
                    if row:
                        klien_pg_id = row[0]
                        query_insert = """
                        INSERT INTO sesi (klien_id, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(query_insert, (klien_pg_id, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik))

                        cursor.execute("UPDATE klien SET kunjungan_terakhir = %s WHERE id = %s", (tanggal_sesi.split()[0], klien_pg_id))
                conn.commit()
        except Exception as e:
            print(f"[CloudSync] Gagal sync Sesi: {e}")

    def sync_simpan_sesi(self, id_klien, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik):
        self.run_in_background(
            self._sync_sesi_task,
            id_klien, tanggal_sesi, durasi_detik, avg_hr, avg_gsr, avg_temp, data_grafik
        )

    def _sync_delete_klien_task(self, id_klien):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM klien WHERE id_klien = %s", (id_klien,))
                conn.commit()
        except Exception as e:
            print(f"[CloudSync] Gagal delete Klien: {e}")

    def sync_delete_klien(self, id_klien):
        self.run_in_background(self._sync_delete_klien_task, id_klien)

    def _sync_delete_sesi_task(self, sesi_id):
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    pass
                conn.commit()
        except Exception as e:
            pass

    def sync_delete_sesi(self, sesi_id, tanggal_sesi):
        def task():
            try:
                with self._get_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("DELETE FROM sesi WHERE tanggal_sesi = %s", (tanggal_sesi,))
                    conn.commit()
            except:
                pass
        self.run_in_background(task)

    def pull_all_from_cloud(self, local_db_path, force=False):
        """Menarik seluruh data terbaru dari Neon DB dan menimpanya ke SQLite lokal agar tersinkronisasi antar laptop"""
        if CloudSyncService._has_pulled_on_startup and not force:
            return

        import time
        import sqlite3

        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"[CloudSync] Mengunduh data terbaru dari Cloud (Neon)... (Percobaan {attempt+1})")
                CloudSyncService._has_pulled_on_startup = True

                with self._get_connection() as pg_conn:
                    with pg_conn.cursor() as pg_cursor:
                        pg_cursor.execute("SELECT id_klien, nama, jenis_kelamin, tanggal_lahir, alamat, no_hp, email, kunjungan_terakhir FROM klien")
                        cloud_klien = pg_cursor.fetchall()

                if cloud_klien:
                    with sqlite3.connect(local_db_path) as sl_conn:
                        sl_cursor = sl_conn.cursor()
                        for k in cloud_klien:
                            query = """
                            INSERT INTO klien (id_klien, nama, jenis_kelamin, tanggal_lahir, alamat, no_hp, email, kunjungan_terakhir)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ON CONFLICT(id_klien) DO UPDATE SET
                            nama=excluded.nama, jenis_kelamin=excluded.jenis_kelamin,
                            tanggal_lahir=excluded.tanggal_lahir, alamat=excluded.alamat,
                            no_hp=excluded.no_hp, email=excluded.email, kunjungan_terakhir=excluded.kunjungan_terakhir
                            """
                            sl_cursor.execute(query, k)
                        sl_conn.commit()
                print("[CloudSync] Sinkronisasi Cloud ke Lokal berhasil!")
                break
            except Exception as e:
                print(f"[CloudSync] Gagal pull dari Cloud: {e}")
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    print("[CloudSync] Sinkronisasi dibatalkan setelah beberapa kali gagal.")

