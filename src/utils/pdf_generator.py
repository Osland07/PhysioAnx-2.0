import os
from datetime import datetime
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Logo.jpeg")
        if os.path.exists(logo_path):
            self.image(logo_path, 10, 8, 25)

        self.set_font('helvetica', 'B', 15)
        self.cell(80)
        self.cell(30, 10, 'SURAT HASIL PEMERIKSAAN', 0, 1, 'C')
        self.set_font('helvetica', '', 10)
        self.cell(80)
        self.cell(30, 10, 'PhysioAnx - Sistem Pemantauan Cemas', 0, 1, 'C')
        self.ln(15)
        self.line(10, 35, 200, 35)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Halaman {self.page_no()}', 0, 0, 'C')

def buat_pdf_hasil(klien, sesi, output_path):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("helvetica", size=12)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Data Pasien", 0, 1)
    pdf.set_font("helvetica", size=12)

    pdf.cell(40, 10, "ID Klien", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, str(klien.get('id_klien', '-')), 0, 1)

    pdf.cell(40, 10, "Nama", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, str(klien.get('nama', '-')), 0, 1)

    pdf.cell(40, 10, "Jenis Kelamin", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, str(klien.get('jenis_kelamin', '-')), 0, 1)

    pdf.cell(40, 10, "Tanggal Lahir", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, str(klien.get('tanggal_lahir', '-')), 0, 1)

    pdf.ln(10)

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(0, 10, "Hasil Pemeriksaan", 0, 1)
    pdf.set_font("helvetica", size=12)

    pdf.cell(40, 10, "Tanggal Sesi", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, str(sesi.get('tanggal_sesi', '-')), 0, 1)

    pdf.cell(40, 10, "Durasi (Detik)", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, str(sesi.get('durasi_detik', '-')), 0, 1)

    hr_val = float(sesi.get('avg_hr', 0) or 0)
    gsr_val = float(sesi.get('avg_gsr', 0) or 0)
    temp_val = float(sesi.get('avg_temp', 0) or 0)

    pdf.cell(40, 10, "Rata-rata HR", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, f"{hr_val:.2f} BPM", 0, 1)

    pdf.cell(40, 10, "Rata-rata GSR", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, f"{gsr_val:.2f} microSiemens", 0, 1)

    pdf.cell(40, 10, "Rata-rata Suhu", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, f"{temp_val:.2f} \u00b0C", 0, 1)

    pdf.ln(5)

    if hr_val <= 80:
        kategori = "Normal to Mild"
    elif hr_val <= 95:
        kategori = "Mild to Moderate"
    elif hr_val <= 110:
        kategori = "Moderate to Severe"
    else:
        kategori = "Severe"

    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(40, 10, "Klasifikasi Cemas", 0, 0)
    pdf.cell(10, 10, ":", 0, 0)
    pdf.cell(0, 10, kategori, 0, 1)

    pdf.ln(20)

    pdf.set_font("helvetica", size=12)
    pdf.cell(120)
    tanggal_cetak = datetime.now().strftime("%d %B %Y")
    pdf.cell(0, 10, f"Dicetak pada: {tanggal_cetak}", 0, 1, "C")
    pdf.cell(120)
    pdf.cell(0, 10, "Petugas / Terapis", 0, 1, "C")
    pdf.ln(20)
    pdf.cell(120)
    pdf.cell(0, 10, "(____________________)", 0, 1, "C")

    pdf.output(output_path)
