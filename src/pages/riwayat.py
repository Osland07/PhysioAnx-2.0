import flet as ft
import flet_charts as fc
import json
import os
from services.klien_service import KlienService
from services.sesi_service import SesiService
from utils.pdf_generator import buat_pdf_hasil

class RiwayatPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.klien_db = KlienService()
        self.sesi_db = SesiService()

        self.expand = True
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = ft.BorderRadius(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.margin = ft.Margin(left=0, top=15, right=15, bottom=15)
        self.padding = 30

        self.date_picker = ft.DatePicker(
            on_change=self.on_date_picked,
            on_dismiss=self.on_date_picked,
        )

        if self.main_page and self.date_picker not in self.main_page.overlay:
            self.main_page.overlay.append(self.date_picker)

        self.datatable = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("TANGGAL SESI", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("NAMA PASIEN", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("HASIL PEMERIKSAAN", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("AKSI", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
            ],
            rows=[],
            heading_row_color=ft.Colors.BLUE_GREY_50,
            border_radius=10,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            data_row_min_height=65,
            data_row_max_height=65,
        )

        self.search_input = ft.TextField(
            hint_text="Cari nama pasien...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            expand=True,
            height=45,
            content_padding=0,
            on_change=self.on_filter_changed
        )

        self.btn_date = ft.TextButton(
            "Pilih Tanggal",
            icon=ft.Icons.CALENDAR_MONTH,
            on_click=self.open_date_picker,
            style=ft.ButtonStyle(color=ft.Colors.BLUE_700)
        )

        self.btn_clear_date = ft.IconButton(
            ft.Icons.CLOSE,
            icon_color=ft.Colors.RED_400,
            tooltip="Hapus Filter Tanggal",
            visible=False,
            on_click=self.clear_date
        )

        self.filter_jk = ft.Dropdown(
            options=[
                ft.dropdown.Option("Semua"),
                ft.dropdown.Option("Laki-laki"),
                ft.dropdown.Option("Perempuan")
            ],
            value="Semua",
            width=150,
            height=45,
            border_radius=10,
            content_padding=10,
            on_select=self.on_filter_changed,
            label="Jenis Kelamin"
        )

        self.filter_hasil = ft.Dropdown(
            options=[
                ft.dropdown.Option("Semua Hasil"),
                ft.dropdown.Option("Normal to Mild"),
                ft.dropdown.Option("Mild to Moderate"),
                ft.dropdown.Option("Moderate to Severe"),
                ft.dropdown.Option("Severe")
            ],
            value="Semua Hasil",
            width=230,
            height=45,
            border_radius=10,
            content_padding=10,
            on_select=self.on_filter_changed,
            label="Hasil"
        )

        self.filter_bar = ft.Row([
            self.search_input,
            self.filter_jk,
            self.filter_hasil,
            ft.Container(
                content=ft.Row([self.btn_date, self.btn_clear_date], spacing=0),
                border=ft.Border.all(1, ft.Colors.BLUE_200),
                border_radius=10,
                padding=ft.Padding(5, 0, 5, 0)
            )
        ], spacing=15)

        self.view_pilih_riwayat = ft.Column([
            ft.Text("Riwayat Sesi", size=28, weight="bold", color="#1e293b"),
            ft.Text("Daftar seluruh rekaman sesi telemetri yang pernah dilakukan di instansi ini.", color=ft.Colors.GREY_700),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.filter_bar,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Container(
                content=ft.ListView([self.datatable], expand=True),
                expand=True
            )
        ], expand=True, visible=True)

        self.btn_kembali = ft.TextButton(
            "Kembali ke Daftar Sesi",
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            on_click=self.tutup_detail
        )
        self.detail_title = ft.Text("-", size=20, weight="bold", color=ft.Colors.BLUE_900)

        self.chart_hr_container = ft.Container(expand=True)
        self.chart_gsr_container = ft.Container(expand=True)
        self.chart_temp_container = ft.Container(expand=True)

        self.view_detail_grafik = ft.Column([
            ft.Row([self.btn_kembali, self.detail_title], alignment=ft.MainAxisAlignment.START, spacing=15),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Column([
                self.chart_hr_container,
                self.chart_gsr_container,
                self.chart_temp_container
            ], expand=True, spacing=15, scroll=ft.ScrollMode.AUTO)
        ], expand=True, visible=False)

        self.content = ft.Column([
            self.view_pilih_riwayat,
            self.view_detail_grafik
        ], expand=True)

        self.load_all_riwayat(is_init=True)

    def show_snackbar(self, message, color):
        snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.main_page.snack_bar = snackbar
        snackbar.open = True
        try:
            self.main_page.update()
        except Exception:
            pass

    def open_date_picker(self, e):
        self.date_picker.open = True
        self.main_page.update()

    def on_date_picked(self, e):
        if self.date_picker.value:
            self.btn_date.text = self.date_picker.value.strftime("%d-%m-%Y")
            self.btn_clear_date.visible = True
        else:
            self.btn_date.text = "Pilih Tanggal"
            self.btn_clear_date.visible = False
        self.update()
        self.on_filter_changed(None)

    def clear_date(self, e):
        self.date_picker.value = None
        self.btn_date.text = "Pilih Tanggal"
        self.btn_clear_date.visible = False
        self.update()
        self.on_filter_changed(None)

    def on_filter_changed(self, e):
        search_val = self.search_input.value
        tgl_val = self.date_picker.value.strftime("%d-%m-%Y") if self.date_picker.value else ""
        jk_val = self.filter_jk.value
        hasil_val = self.filter_hasil.value

        self.load_all_riwayat(
            search_query=search_val,
            filter_tanggal=tgl_val,
            filter_jk=jk_val,
            filter_hasil=hasil_val
        )

    def load_all_riwayat(self, is_init=False, search_query="", filter_tanggal="", filter_jk="", filter_hasil=""):
        riwayat_list = self.sesi_db.get_all_riwayat(search_query, filter_tanggal, filter_jk, filter_hasil)
        self.datatable.rows.clear()

        for sesi in riwayat_list:
            sesi_id = sesi['id']
            hasil_prediksi = sesi.get('hasil_prediksi')

            if not hasil_prediksi:
                hr_val = float(sesi['avg_hr'] or 0)
                if hr_val <= 80:
                    kategori = "Normal"
                elif hr_val <= 95:
                    kategori = "Cemas"
                else:
                    kategori = "Sangat Cemas"
            else:
                kategori = hasil_prediksi

            if "normal" in str(kategori).lower():
                badge_color = ft.Colors.GREEN_700
                badge_bg = ft.Colors.GREEN_50
            elif "sangat" in str(kategori).lower() or "severe" in str(kategori).lower():
                badge_color = ft.Colors.RED_700
                badge_bg = ft.Colors.RED_50
            else:
                badge_color = ft.Colors.AMBER_700
                badge_bg = ft.Colors.AMBER_50

            hasil_ui = ft.Container(
                content=ft.Text(kategori, color=badge_color, weight="bold", size=12),
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=badge_bg,
                border_radius=8
            )

            btn_lihat = ft.Button(
                "Detail",
                icon=ft.Icons.SHOW_CHART_ROUNDED,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE_600),
                on_click=lambda e, sid=sesi_id: self.buka_detail(sid)
            )

            btn_pdf = ft.Button(
                "PDF",
                icon=ft.Icons.PICTURE_AS_PDF_ROUNDED,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_600),
                on_click=lambda e, sid=sesi_id: self.buka_pdf_dialog(sid)
            )

            btn_hapus = ft.Button(
                "Hapus",
                icon=ft.Icons.DELETE_ROUNDED,
                style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED_600),
                on_click=lambda e, sid=sesi_id: self.hapus_sesi(sid)
            )

            aksi_ui = ft.Row([btn_lihat, btn_pdf, btn_hapus], spacing=5)

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f"#{sesi['id']}", color=ft.Colors.GREY_600)),
                    ft.DataCell(ft.Text(sesi['tanggal_sesi'], color=ft.Colors.GREY_800)),
                    ft.DataCell(ft.Text(sesi['nama'], weight="bold", color=ft.Colors.BLUE_GREY_900)),
                    ft.DataCell(hasil_ui),
                    ft.DataCell(aksi_ui),
                ]
            )
            self.datatable.rows.append(row)

        if not is_init:
            try:
                self.update()
            except Exception:
                pass

    def buka_pdf_dialog(self, sesi_id):
        detail_sesi = self.sesi_db.get_detail_sesi(sesi_id)
        if not detail_sesi:
            return

        klien_info = self.klien_db.get_klien_by_id(detail_sesi['klien_id'])
        if not klien_info:
            return

        export_dir = os.path.join(os.getcwd(), "pdf_exports")
        os.makedirs(export_dir, exist_ok=True)

        nama_klien = klien_info.get('nama', 'Klien').strip().replace(' ', '_')
        file_name = f"Hasil_Pemeriksaan_{nama_klien}_Sesi_{sesi_id}.pdf"
        pdf_path = os.path.join(export_dir, file_name)

        buat_pdf_hasil(klien_info, detail_sesi, pdf_path)
        self.show_snackbar(f"PDF Berhasil Dibuat!", ft.Colors.GREEN_600)
        try:
            os.startfile(pdf_path)
        except Exception:
            pass

    def hapus_sesi(self, sesi_id):
        def close_dialog(e):
            dialog.open = False
            if dialog in self.main_page.overlay:
                self.main_page.overlay.remove(dialog)
            self.main_page.update()

        def on_confirm(e):
            self.sesi_db.delete_sesi(sesi_id)
            dialog.open = False
            if dialog in self.main_page.overlay:
                self.main_page.overlay.remove(dialog)
            self.main_page.update()
            self.show_snackbar(f"Riwayat Sesi #{sesi_id} berhasil dihapus", ft.Colors.RED_600)
            self.load_all_riwayat()

        dialog = ft.AlertDialog(
            title=ft.Text("Konfirmasi Hapus"),
            content=ft.Text(f"Apakah Anda yakin ingin menghapus Riwayat Sesi #{sesi_id}? Data yang dihapus tidak dapat dikembalikan."),
            actions=[
                ft.TextButton("Batal", on_click=close_dialog),
                ft.Button("Ya, Hapus", on_click=on_confirm, bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.main_page.overlay.append(dialog)
        dialog.open = True
        self.main_page.update()

    def buka_detail(self, sesi_id):
        detail = self.sesi_db.get_detail_sesi(sesi_id)
        if not detail:
            return

        self.detail_title.value = f"Rekaman Grafik ({detail['tanggal_sesi']})"

        if detail.get('data_grafik'):
            try:
                grafik = json.loads(detail['data_grafik'])
                self.chart_hr_container.content = self._render_chart("Heart Rate", grafik['hr'], ft.Colors.RED_500, " BPM")
                self.chart_gsr_container.content = self._render_chart("GSR", grafik['gsr'], ft.Colors.BLUE_500, " µS")
                self.chart_temp_container.content = self._render_chart("Suhu Tubuh", grafik['temp'], ft.Colors.ORANGE_500, " °C")
            except Exception as ex:
                self.chart_hr_container.content = ft.Text(f"Data grafik gagal dimuat: {ex}")
        else:
            self.chart_hr_container.content = ft.Text("Data grafik kosong")

        self.view_pilih_riwayat.visible = False
        self.view_detail_grafik.visible = True
        self.update()

    def tutup_detail(self, e):
        self.view_detail_grafik.visible = False
        self.view_pilih_riwayat.visible = True
        self.update()

    def _render_chart(self, title, arr_data, color, unit):
        points = [fc.LineChartDataPoint(p['x'], p['y']) for p in arr_data]

        min_y = min((p['y'] for p in arr_data), default=0) * 0.9
        max_y = max((p['y'] for p in arr_data), default=100) * 1.1

        min_x = min((p['x'] for p in arr_data), default=0)
        max_x = max((p['x'] for p in arr_data), default=20)

        chart = fc.LineChart(
            data_series=[
                fc.LineChartData(
                    points=points,
                    stroke_width=2,
                    color=color,
                    curved=True
                )
            ],
            border=ft.Border(
                bottom=ft.BorderSide(1, ft.Colors.GREY_300),
                left=ft.BorderSide(1, ft.Colors.GREY_300)
            ),
            min_y=min_y, max_y=max_y,
            min_x=min_x, max_x=max_x,
            expand=True,
            left_axis=fc.ChartAxis(
                labels=[
                    fc.ChartAxisLabel(value=min_y, label=ft.Text(f"{min_y:.1f}", size=10, color=ft.Colors.GREY_500)),
                    fc.ChartAxisLabel(value=max_y, label=ft.Text(f"{max_y:.1f}", size=10, color=ft.Colors.GREY_500))
                ],
                label_size=40
            )
        )
        return ft.Container(
            content=ft.Column([
                ft.Text(f"{title} (Rata-rata)", size=14, weight="bold", color=ft.Colors.GREY_700),
                ft.Container(content=chart, expand=True)
            ]),
            height=200,
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.Border.all(1, "#e2e8f0"),
        )
