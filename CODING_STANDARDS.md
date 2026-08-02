# Standar Pengkodingan & Arsitektur PhysioAnx (Ala Laravel MVC)

Dokumen ini berisi aturan main (guideline) untuk pengembangan sistem PhysioAnx. Aplikasi ini menggunakan antarmuka desktop (PySide6), namun diarsiteki dengan konsep **MVC (Model-View-Controller)** yang sangat terinspirasi oleh framework web modern seperti Laravel.

Tujuan utama aturan ini adalah untuk mencegah *God Object* (satu file yang berisi ribuan baris kode) dan memastikan *Separation of Concerns* (Pemisahan Tugas).

---

## 1. Aturan Penempatan Kode (Strict Folder Rules)

Patuhi penempatan file di folder `app/` berikut secara ketat:

### 📁 `models/` (Data & Database)
- **Fungsi:** Mengurus skema database dan interaksi ORM (SQLAlchemy). Setara dengan folder `app/Models` di Laravel.
- **Aturan:** DILARANG KERAS mengimpor komponen UI (PySide6/PyQt) di dalam folder ini. Model murni hanya berurusan dengan struktur data.
- **Contoh File:** `patient.py`, `user.py`, `database.py`.

### 📁 `views/` (User Interface / Blade Templates)
- **Fungsi:** Murni hanya untuk mendefinisikan layout, warna, penempatan tombol (`QPushButton`), tabel (`QTableWidget`), dsb.
- **Aturan:** DILARANG KERAS memanggil fungsi database (`SessionLocal()`) atau menulis logika bisnis di sini. Biarkan file ini hanya tahu cara merender tampilan.
- **Contoh File:** `patient_view.py`, `dashboard_view.py`.

### 📁 `controllers/` (The Brain)
- **Fungsi:** Menjadi jembatan antara **View** dan **Model**.
- **Aturan:** Menerima *event/click* dari `View`, memproses/mengambil data dari `Model`, dan melemparkan kembali data tersebut untuk di-update di `View`. Semua interaksi ke database (`SessionLocal`) harus terjadi di sini atau di Services.
- **Contoh File:** `patient_controller.py`.

### 📁 `components/` (Reusable UI)
- **Fungsi:** Tempat untuk membuat elemen-elemen UI kecil yang sering dipanggil berulang kali.
- **Aturan:** Misalnya kotak dialog (*popup*), kustomisasi tombol, atau kartu info ringkas.
- **Contoh File:** `patient_dialog.py`.

### 📁 `services/` (Heavy Logic)
- **Fungsi:** Tempat untuk meletakkan logika yang kompleks atau berjalan di latar belakang (background processing).
- **Aturan:** Menganut prinsip *Thin Controller, Fat Service*. Jika algoritma parsing terlalu panjang (seperti komunikasi Bluetooth atau manipulasi Data Array yang rumit), pisahkan logic-nya ke dalam class Service.
- **Contoh File:** `bluetooth_worker.py`, `data_parser.py`.

---

## 2. Aturan Penamaan (Naming Conventions)

Gunakan standar penamaan PEP-8 Python:

- **Nama File & Folder:** Selalu gunakan huruf kecil dengan garis bawah (*snake_case*).
  ✅ *Benar:* `patient_view.py`, `main_window.py`
  ❌ *Salah:* `PatientView.py`, `mainWindow.py`

- **Nama Class:** Selalu gunakan huruf besar di setiap kata awal (*PascalCase*). Nama file dan class harus saling merepresentasikan.
  ✅ *Benar:* `class PatientView(QWidget):`, `class PatientController:`

- **Nama Variabel & Method/Fungsi:** Gunakan huruf kecil dengan garis bawah (*snake_case*).
  ✅ *Benar:* `btn_tambah`, `load_patients()`, `patient_data`
  ❌ *Salah:* `btnTambah`, `LoadPatients()`

---

## 3. Workflow Menambah Fitur/Halaman Baru

Saat Anda diminta untuk menambah menu/halaman baru (misal: "Menu Laporan"), selalu ikuti **4 Langkah Wajib** ini:

1. **Buat View-nya:** Buat `app/views/laporan_view.py` (Isinya murni desain layout dan deklarasi variabel UI).
2. **Buat Controller-nya:** Buat `app/controllers/laporan_controller.py` (Isinya fungsi `load_data()`, fungsi saat tombol simpan diklik, dan koneksi ke database).
3. **Impor ke Main Window:** Buka `app/main_window.py` lalu impor file View dan Controller tersebut.
4. **Registrasi Halaman:** Inisialisasi View & Controller, lalu daftarkan ke dalam `self.stacked_widget` di fungsi `__init__`.

---

## 4. Aturan Suci `main_window.py` (The Layout Master)

- `main_window.py` **HANYA** bertugas sebagai "Layout Induk" (Master Layout). 
- Tugasnya terbatas pada mengurus kerangka aplikasi: Sidebar (Menu Kiri), Topbar (Header), dan tempat penampung perpindahan halaman (`QStackedWidget`).
- **DILARANG KERAS** menambah *widget* spesifik (seperti input teks pencarian pasien, tabel riwayat, dsb) secara langsung ke dalam fungsi di file ini. Semuanya harus dipisah ke dalam `views/`. 

Dengan mematuhi struktur ini, aplikasi PhysioAnx akan selalu bersih, file tetap berukuran kecil (mudah dibaca), terhindar dari *Spaghetti Code*, dan siap dikerjakan secara kolaboratif bersama tim.
