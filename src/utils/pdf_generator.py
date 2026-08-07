import os
import json
import warnings
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

warnings.filterwarnings("ignore", category=DeprecationWarning)

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"kop_surat_path": "", "nama_penanda_tangan": ""}

BULAN_INDONESIA = {
    1: "Januari", 2: "Februari", 3: "Maret", 4: "April",
    5: "Mei", 6: "Juni", 7: "Juli", 8: "Agustus",
    9: "September", 10: "Oktober", 11: "November", 12: "Desember"
}

def format_tanggal_indonesia(dt=None):
    if dt is None:
        dt = datetime.now()
    return f"{dt.day:02d} {BULAN_INDONESIA.get(dt.month, '')} {dt.year}"

class PhysioAnxPDF(FPDF):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.kop_surat_path = settings.get("kop_surat_path", "")

    def header(self):
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        
        # Check custom uploaded Kop Surat image
        if self.kop_surat_path:
            full_kop_path = os.path.join(assets_dir, self.kop_surat_path)
            if os.path.exists(full_kop_path):
                self.image(full_kop_path, 20, 8, 170)
                self.ln(35)
                return

        # Default Clean & Official Kop Header
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Logo.jpeg")
        if os.path.exists(logo_path):
            self.image(logo_path, 20, 10, 24)

        self.set_font('helvetica', 'B', 16)
        self.set_text_color(30, 41, 59)
        self.cell(28, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 8, 'PHYSIOANX DIAGNOSTICS', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

        self.set_font('helvetica', '', 10)
        self.set_text_color(71, 85, 105)
        self.cell(28, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 5, 'Sistem Informasi Pemantauan & Deteksi Kecemasan Fisiologis', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
        self.cell(28, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.cell(0, 5, 'Layanan Pemeriksaan Telemetri & Analisis Saraf Otonom', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

        self.ln(6)
        # Double decorative line
        self.set_draw_color(37, 99, 235)
        self.set_line_width(0.8)
        self.line(20, 34, 190, 34)
        self.set_draw_color(148, 163, 184)
        self.set_line_width(0.2)
        self.line(20, 35.5, 190, 35.5)
        self.ln(6)

    def footer(self):
        pass

def buat_pdf_hasil(klien, sesi, output_path):
    settings = load_settings()
    pdf = PhysioAnxPDF(settings)
    pdf.set_margins(20, 15, 20)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 1. Judul Surat & Referensi
    pdf.set_font("helvetica", 'B', 14)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "SURAT HASIL PEMERIKSAAN KECEMASAN", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    sesi_id = sesi.get('id', 0)
    pdf.set_font("helvetica", '', 9)
    pdf.set_text_color(100, 116, 139)
    ref_no = f"No. Ref: PAX-SESSION-{sesi_id:04d}/{datetime.now().strftime('%Y')}"
    pdf.cell(0, 5, ref_no, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.ln(6)

    # 2. Section: Data Pasien / Klien
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "I. IDENTITAS KLIEN", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(2)

    pdf.set_font("helvetica", size=10)
    pdf.set_text_color(51, 65, 85)

    def print_row(label1, val1, label2="", val2=""):
        pdf.set_font("helvetica", size=9.5)
        pdf.cell(30, 6, label1, new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(5, 6, ":", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.cell(50, 6, str(val1 or '-'), new_x=XPos.RIGHT, new_y=YPos.TOP)
        
        if label2:
            pdf.cell(28, 6, label2, new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(5, 6, ":", new_x=XPos.RIGHT, new_y=YPos.TOP)
            pdf.cell(52, 6, str(val2 or '-'), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.cell(0, 6, "", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    print_row("Nama Lengkap", klien.get('nama', '-'), "No. Telepon", klien.get('no_hp', '-'))
    print_row("Tanggal Lahir", klien.get('tanggal_lahir', '-'), "Email", klien.get('email', '-'))
    print_row("Jenis Kelamin", klien.get('jenis_kelamin', '-'), "Alamat", klien.get('alamat', '-'))

    pdf.ln(4)

    # 3. Section: Hasil Pengukuran Sensor & Telemetri
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "II. HASIL TELEMETRI SENSOR FISIOLOGIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(3)

    tgl_sesi = sesi.get('tanggal_sesi', '-')
    hr_val = float(sesi.get('avg_hr', 0) or 0)
    gsr_val = float(sesi.get('avg_gsr', 0) or 0)
    temp_val = float(sesi.get('avg_temp', 0) or 0)

    # Telemetry Table Header
    pdf.set_font("helvetica", 'B', 9)
    pdf.cell(55, 7, " Parameter Sensor", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
    pdf.cell(40, 7, " Nilai Rata-rata", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(35, 7, " Satuan", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(40, 7, " Rentang Acuan", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # Telemetry Table Rows
    pdf.set_font("helvetica", '', 9.5)

    pdf.cell(55, 7, " Heart Rate (Denyut Jantung)", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
    pdf.cell(40, 7, f"{hr_val:.1f}", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(35, 7, "BPM", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(40, 7, "60 - 100 BPM", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    micro_sym = chr(181) + "S"
    pdf.cell(55, 7, " Galvanic Skin Response (GSR)", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
    pdf.cell(40, 7, f"{gsr_val:.2f}", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(35, 7, f"{micro_sym} (microSiemens)", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(40, 7, f"5.0 - 40.0 {micro_sym}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    deg_sym = chr(176) + "C"
    pdf.cell(55, 7, " Suhu Tubuh (Skin Temp)", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
    pdf.cell(40, 7, f"{temp_val:.1f}", border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(35, 7, deg_sym, border=1, new_x=XPos.RIGHT, new_y=YPos.TOP, align='C')
    pdf.cell(40, 7, f"36.0 - 37.5 {deg_sym}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    pdf.ln(3)
    pdf.set_font("helvetica", '', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, f"* Sesi perekaman berlangsung pada {tgl_sesi}.", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')

    pdf.ln(4)

    # 4. Section: Hasil Analisa
    pdf.set_font("helvetica", 'B', 10)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 6, "III. HASIL ANALISA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L')
    pdf.ln(3)

    # Determine classification text
    hasil_prediksi = sesi.get('hasil_prediksi')
    if not hasil_prediksi:
        if hr_val <= 80:
            hasil_prediksi = "Normal"
        elif hr_val <= 95:
            hasil_prediksi = "Cemas"
        else:
            hasil_prediksi = "Sangat Cemas"

    pdf.set_font("helvetica", '', 10)
    pdf.set_text_color(51, 65, 85)
    pdf.cell(45, 6, "Tingkat Kecemasan", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(5, 6, ":", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(0, 6, str(hasil_prediksi).upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(2)
    pdf.set_font("helvetica", '', 9)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(0, 5, "Catatan: Hasil analisis diperoleh berdasarkan pengolahan data telemetri fisiologis (Heart Rate, Galvanic Skin Response, dan Suhu Tubuh) selama sesi berlangsung.")

    pdf.ln(8)

    # 5. Section: Pengesahan & Tanda Tangan
    pdf.set_font("helvetica", size=9.5)
    pdf.set_text_color(30, 41, 59)
    
    pdf.cell(90, new_x=XPos.RIGHT, new_y=YPos.TOP)
    tgl_sekarang = format_tanggal_indonesia()
    pdf.cell(0, 5, f"Jakarta, {tgl_sekarang}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.cell(90, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 5, "Terapis / Petugas Pemeriksa,", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    
    pdf.ln(22)

    nama_penanda = settings.get("nama_penanda_tangan", "").strip()
    if not nama_penanda:
        nama_penanda = "( ____________________ )"
    else:
        nama_penanda = f"( {nama_penanda} )"

    pdf.set_font("helvetica", 'B', 10)
    pdf.cell(90, new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.cell(0, 5, nama_penanda, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

    # Export PDF file
    pdf.output(output_path)
