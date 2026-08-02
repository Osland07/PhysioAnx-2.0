<p align="center">
  <a href="https://www.python.org" target="_blank">
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python Logo" width="200">
  </a>
</p>

<h1 align="center">PhysioAnx 2.0</h1>

<p align="center">
  Sistem Pemantauan Cemas berbasis Telemetri Fisiologis dengan UI Modern
</p>

<p align="center">
  <a href="https://github.com/Osland07/PhysioAnx-2.0"><img src="https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white" alt="Python"></a>
  <a href="https://flet.dev"><img src="https://img.shields.io/badge/UI-Flet-FF4B4B.svg?logo=flutter&logoColor=white" alt="Flet"></a>
  <a href="https://www.sqlite.org/index.html"><img src="https://img.shields.io/badge/Database-SQLite-003B57.svg?logo=sqlite&logoColor=white" alt="SQLite"></a>
</p>

---

## 🌟 Tentang PhysioAnx

**PhysioAnx** adalah aplikasi cerdas yang dirancang untuk membantu memantau dan mengklasifikasikan tingkat kecemasan pasien secara real-time. Dengan memanfaatkan sinyal fisiologis seperti Heart Rate (HR), Galvanic Skin Response (GSR), dan Suhu Tubuh (Temperature), sistem ini mempermudah terapis atau psikolog dalam mendiagnosis dan menyimpan data riwayat pasien.


## 🚀 Fitur Utama

- **📊 Dashboard Real-time:** Pantau statistik pengunjung dan rekaman terbaru secara langsung.
- **👥 Manajemen Klien:** Tambah, edit, dan kelola data klien dengan mudah.
- **📈 Perekaman Sesi (Telemetri):** Rekam dan visualisasikan data HR, GSR, dan Suhu pasien dalam bentuk grafik.
- **🗂️ Riwayat & Laporan PDF:** Lihat rekaman sesi yang lalu dan cetak dokumen "Surat Hasil Pemeriksaan" (PDF) secara instan.
- **☁️ Cloud Sync (PostgreSQL):** Sinkronisasi data ke cloud 
- **⚙️ Pengaturan Kustom:**

## 🛠️ Persyaratan Sistem

Pastikan sistem Anda memenuhi persyaratan berikut sebelum menjalankan aplikasi:
- Python >= 3.10
- Git

## 📦 Instalasi

Ikuti langkah-langkah di bawah ini untuk menjalankan PhysioAnx di komputer Anda (Windows / macOS).

1. **Kloning Repositori**
   ```bash
   git clone https://github.com/Osland07/PhysioAnx-2.0.git
   cd "PhysioAnx 2.0"
   ```

2. **Buat Virtual Environment (Sangat Direkomendasikan)**
   
   **Di Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   **Di macOS / Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instal Dependensi**
   ```bash
   pip install -r requirements.txt
   # (Gunakan pip3 install -r requirements.txt jika di macOS dan pip belum terhubung ke python3)
   ```

## ▶️ Menjalankan Aplikasi

Anda dapat menjalankan aplikasi langsung dengan mengeksekusi file utama:

**Di Windows:**
```bash
# Menggunakan script batch
start_app.bat

# Atau eksekusi langsung
python src/main.py
```

**Di macOS / Linux:**
```bash
# Pastikan virtual environment sudah aktif, lalu jalankan:
python3 src/main.py
```

## 📂 Struktur Direktori

```text
PhysioAnx 2.0/
├── assets/                  # File gambar, kop surat, dan resource statis
├── src/                     # Source Code Utama
│   ├── components/          # Komponen UI Flet (Sidebar, dll)
│   ├── models/              # Model data (jika ada)
│   ├── pages/               # Halaman-halaman aplikasi (Dashboard, Klien, Riwayat, dll)
│   ├── services/            # Logika bisnis dan database (SQLite, Cloud Sync)
│   ├── utils/               # Modul utilitas (seperti Generator PDF)
│   └── main.py              # Entry point aplikasi
├── flet_tabs_help.txt       # Bantuan sintaks Flet
├── requirements.txt         # Daftar dependencies
├── start_app.bat            # Script start-up
└── README.md                # Dokumentasi (Anda di sini!)
```

## 🤝 Berkontribusi

Kami sangat mengapresiasi segala bentuk kontribusi! Jika Anda menemukan bug atau memiliki saran fitur baru, silakan buka *Issue* atau kirimkan *Pull Request*.

## 📄 Lisensi

PhysioAnx adalah perangkat lunak open-source. Anda bebas untuk menggunakannya untuk kebutuhan penelitian maupun operasional klinik Anda.
