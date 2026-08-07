import flet as ft
import flet_charts as fc
import asyncio
from services.klien_service import KlienService
from services.sesi_service import SesiService
from services.sensor_service import SensorService

class SesiBaruPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.klien_db = KlienService()
        self.sesi_db = SesiService()

        self.latest_prediction_result = None

        # Bluetooth Status Indicator Badge UI
        self.ble_status_icon = ft.Icon(ft.Icons.BLUETOOTH_SEARCHING, color=ft.Colors.AMBER_600, size=18)
        self.ble_status_text = ft.Text("Mencari Device...", size=13, weight="w500", color=ft.Colors.AMBER_800)
        self.ble_status_badge = ft.Container(
            content=ft.Row([self.ble_status_icon, self.ble_status_text], spacing=6),
            padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            bgcolor=ft.Colors.AMBER_50,
            border=ft.Border.all(1, ft.Colors.AMBER_200),
            border_radius=20
        )

        # Get persistent SensorService singleton & register callbacks
        self.sensor_service = SensorService.get_instance(page)
        self.sensor_service.register_callbacks(
            on_data=self._on_sensor_data,
            on_status=self._on_sensor_status,
            on_prediction=self._on_sensor_prediction
        )

        self.expand = True
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = ft.BorderRadius(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.padding = 40
        self.margin = ft.Margin(left=0, top=15, right=15, bottom=15)
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=20, color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK), offset=ft.Offset(0, 4))

        self.selected_klien_id = None
        self.session_active = False
        self.time_counter = 0

        self.dropdown_klien = ft.Dropdown(
            label="Pilih Klien",
            expand=True,
            options=[],
            on_select=self.on_klien_selected,
            enable_filter=True,
            enable_search=True,
            editable=True
        )

        self.btn_mulai = ft.Button(
            "Mulai Sesi",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, padding=15, shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.mulai_sesi
        )

        self.val_nama = ft.Text("-", weight="bold", size=16, color="#1e293b")
        self.val_jk = ft.Text("-", size=15, color="#334155")
        self.val_umur = ft.Text("-", size=15, color="#334155")
        self.val_hp = ft.Text("-", size=15, color="#334155")
        self.val_email = ft.Text("-", size=15, color="#334155")
        self.val_alamat = ft.Text("-", size=15, color="#334155", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)
        self.val_sesi = ft.Text("0", weight="bold", size=16, color=ft.Colors.BLUE_600)

        def form_row(label, val_control):
            return ft.Row([
                ft.Container(content=ft.Text(label, color=ft.Colors.GREY_500, size=14, weight="w500"), width=110),
                ft.Text(":", color=ft.Colors.GREY_500),
                ft.Container(content=val_control, expand=True)
            ])

        self.klien_info_card = ft.Card(
            elevation=0,
            visible=False,
            content=ft.Container(
                padding=30,
                bgcolor="#f8fafc",
                border_radius=12,
                border=ft.Border.all(1, "#e2e8f0"),
                content=ft.Column([
                    ft.Text("DATA KLIEN", size=13, weight="bold", color=ft.Colors.BLUE_600),
                    ft.Divider(height=20, color="#e2e8f0"),

                    ft.Row([
                        ft.Column([
                            form_row("Nama Lengkap", self.val_nama),
                            form_row("Jenis Kelamin", self.val_jk),
                            form_row("Umur", self.val_umur),
                        ], expand=True),

                        ft.Column([
                            form_row("Nomor Telepon", self.val_hp),
                            form_row("Email", self.val_email),
                            form_row("Alamat", self.val_alamat),
                        ], expand=True),
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),

                    ft.Divider(height=30, color="#e2e8f0"),
                    ft.Row([
                        ft.Row([
                            ft.Icon(ft.Icons.ANALYTICS_OUTLINED, color=ft.Colors.BLUE_600, size=22),
                            ft.Text("Total Sesi Sebelumnya :", size=15, weight="w500", color=ft.Colors.GREY_600),
                            self.val_sesi
                        ]),
                        self.btn_mulai
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ])
            )
        )

        self.empty_state_card = ft.Container(
            padding=50,
            alignment=ft.Alignment.CENTER,
            bgcolor="#f8fafc",
            border_radius=12,
            border=ft.Border.all(1, "#e2e8f0"),
            content=ft.Column([
                ft.Icon(ft.Icons.PERSON_SEARCH_ROUNDED, size=60, color=ft.Colors.GREY_400),
                ft.Text("Belum Ada Klien Terpilih", size=18, weight="bold", color=ft.Colors.GREY_600),
                ft.Text("Silakan pilih nama klien dari kotak pencarian di atas untuk memuat data klien.", size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        )

        self.view_presession = ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("Pre-Session", size=28, weight=ft.FontWeight.W_800, color="#1e293b"),
                    ft.Text("Silakan cari dan pilih klien dari database untuk melihat data klien dan memulai sesi konseling.", color=ft.Colors.GREY_700),
                ], expand=True),
                self.ble_status_badge
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Row([self.dropdown_klien]),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            self.empty_state_card,
            self.klien_info_card
        ], visible=True)

        self.session_name = ft.Text("-", size=24, weight="bold", color=ft.Colors.BLUE_900)
        self.session_details = ft.Text("-", size=16, color=ft.Colors.GREY_600)

        # Prediction Result Simple Text UI (No Card Container)
        self.prediction_text = ft.Text("", size=15, weight="bold", visible=False)

        self.session_header = ft.Row([
            ft.Container(
                content=ft.Icon(ft.Icons.PERSON_PIN_ROUNDED, color=ft.Colors.BLUE_600, size=40),
                padding=10,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=10
            ),
            ft.Column([
                ft.Row([
                    ft.Text("Sesi Konseling Aktif", size=12, weight="bold", color=ft.Colors.BLUE_600),
                    ft.Icon(ft.Icons.CIRCLE, color=ft.Colors.GREEN_500, size=10)
                ], spacing=5),
                self.session_name,
                self.session_details,
                self.prediction_text
            ], spacing=2)
        ], alignment=ft.MainAxisAlignment.START, spacing=15)

        self.val_hr = ft.Text("--", size=36, weight="bold", color=ft.Colors.RED_600)
        self.val_gsr = ft.Text("--", size=36, weight="bold", color=ft.Colors.BLUE_600)
        self.val_temp = ft.Text("--", size=36, weight="bold", color=ft.Colors.ORANGE_600)

        def create_sensor_card(title, val_control, unit, icon, icon_color):
            return ft.Container(
                width=240,
                height=180,
                padding=18,
                bgcolor=ft.Colors.WHITE,
                border_radius=12,
                border=ft.Border.all(1, "#e2e8f0"),
                content=ft.Column([
                    ft.Row([
                        ft.Icon(icon, color=icon_color, size=22),
                        ft.Text(title, size=14, weight="bold", color=ft.Colors.GREY_700)
                    ], spacing=8),
                    ft.Row([
                        val_control,
                        ft.Text(unit, size=15, weight="w500", color=ft.Colors.GREY_500)
                    ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.END)
                ], spacing=6, alignment=ft.MainAxisAlignment.CENTER)
            )

        self.chart_data_hr = []
        self.chart_data_gsr = []
        self.chart_data_temp = []

        self.chart_hr = self._create_chart("Heart Rate", self.chart_data_hr, ft.Colors.RED_500, 60, 150, " BPM")
        self.chart_gsr = self._create_chart("Galvanic Skin Response", self.chart_data_gsr, ft.Colors.BLUE_500, 0, 10, " µS")
        self.chart_temp = self._create_chart("Suhu Tubuh", self.chart_data_temp, ft.Colors.ORANGE_500, 35, 40, " °C")

        self.card_hr = create_sensor_card("Heart Rate", self.val_hr, "BPM", ft.Icons.FAVORITE, ft.Colors.RED_500)
        self.card_gsr = create_sensor_card("GSR", self.val_gsr, "µS", ft.Icons.WATER_DROP, ft.Colors.BLUE_500)
        self.card_temp = create_sensor_card("Suhu Tubuh", self.val_temp, "°C", ft.Icons.THERMOSTAT, ft.Colors.ORANGE_500)

        self.charts_container = ft.Column([
            ft.Row([self.chart_hr, self.card_hr], height=180, spacing=15),
            ft.Row([self.chart_gsr, self.card_gsr], height=180, spacing=15),
            ft.Row([self.chart_temp, self.card_temp], height=180, spacing=15)
        ], spacing=15)

        self.btn_batal = ft.Button(
            "Batalkan",
            icon=ft.Icons.ARROW_BACK_ROUNDED,
            style=ft.ButtonStyle(bgcolor="#64748b", color=ft.Colors.WHITE, padding=15, shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.batal_sesi
        )

        self.btn_simpan = ft.Button(
            "Simpan Sesi",
            icon=ft.Icons.SAVE_ROUNDED,
            style=ft.ButtonStyle(bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, padding=15, shape=ft.RoundedRectangleBorder(radius=10)),
            on_click=self.akhiri_sesi
        )

        self.view_session = ft.Column([
            self.session_header,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

            ft.Text("Visualisasi Grafik & Metrik Sensor Real-Time", size=16, weight="bold", color=ft.Colors.GREY_800),
            self.charts_container,

            ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
            ft.Row([self.btn_batal, self.btn_simpan], alignment=ft.MainAxisAlignment.END, spacing=15)
        ], visible=False, scroll=ft.ScrollMode.AUTO)

        self.content = ft.Column([
            self.view_presession,
            self.view_session
        ], expand=True, scroll=ft.ScrollMode.AUTO)

        self.load_klien_data()

    def _update_ble_badge(self, status: str, detail: str = ""):
        if status == "connected":
            self.ble_status_icon.name = ft.Icons.BLUETOOTH_CONNECTED
            self.ble_status_icon.color = ft.Colors.GREEN_600
            self.ble_status_text.value = "Terhubung"
            self.ble_status_text.color = ft.Colors.GREEN_800
            self.ble_status_badge.bgcolor = ft.Colors.GREEN_50
            self.ble_status_badge.border = ft.Border.all(1, ft.Colors.GREEN_300)
        else:
            self.ble_status_icon.name = ft.Icons.BLUETOOTH_SEARCHING
            self.ble_status_icon.color = ft.Colors.AMBER_600
            self.ble_status_text.value = "Mencari Device..."
            self.ble_status_text.color = ft.Colors.AMBER_800
            self.ble_status_badge.bgcolor = ft.Colors.AMBER_50
            self.ble_status_badge.border = ft.Border.all(1, ft.Colors.AMBER_200)

        try:
            self.ble_status_badge.update()
        except Exception:
            pass

    def _on_sensor_status(self, category, status_code, message):
        if category == "connection":
            self._update_ble_badge(status_code, message)
        elif category == "scan_status" and status_code == "finish":
            if self.session_active:
                self.akhiri_sesi(None)

    def _on_sensor_prediction(self, hasil_text: str):
        self.latest_prediction_result = hasil_text
        self.prediction_text.value = f"Hasil Prediksi: {hasil_text}"
        self.prediction_text.visible = True

        hasil_lower = hasil_text.lower()
        if "normal" in hasil_lower:
            self.prediction_text.color = ft.Colors.GREEN_600
        elif "sangat cemas" in hasil_lower or "severe" in hasil_lower:
            self.prediction_text.color = ft.Colors.RED_600
        else:
            self.prediction_text.color = ft.Colors.AMBER_600

        try:
            self.prediction_text.update()
        except Exception:
            pass

        try:
            self.prediction_badge.update()
        except Exception:
            pass

    def show_snackbar(self, message, color):
        snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.main_page.snack_bar = snackbar
        snackbar.open = True
        try:
            self.main_page.update()
        except Exception:
            pass

    def load_klien_data(self):
        klien_list = self.klien_db.get_all_klien()
        self.dropdown_klien.options.clear()
        for k in klien_list:
            self.dropdown_klien.options.append(
                ft.dropdown.Option(key=str(k['id']), text=f"{k['id_klien']} - {k['nama']}")
            )

    def on_klien_selected(self, e):
        if not self.dropdown_klien.value:
            self.klien_info_card.visible = False
            self.empty_state_card.visible = True
            self.update()
            return

        klien_id_db = int(self.dropdown_klien.value)
        klien_list = self.klien_db.get_all_klien()
        klien = next((k for k in klien_list if k['id'] == klien_id_db), None)

        if klien:
            umur = "-"
            if klien["tanggal_lahir"]:
                try:
                    import datetime
                    tgl_lahir = datetime.datetime.strptime(klien["tanggal_lahir"], "%d-%m-%Y")
                    today = datetime.datetime.now()
                    umur_int = today.year - tgl_lahir.year - ((today.month, today.day) < (tgl_lahir.month, tgl_lahir.day))
                    umur = f"{umur_int} Tahun"
                except Exception:
                    pass

            self.val_nama.value = klien["nama"]
            self.val_jk.value = klien["jenis_kelamin"] if klien["jenis_kelamin"] else "-"
            self.val_umur.value = umur
            self.val_hp.value = klien['no_hp'] if klien['no_hp'] else "-"
            self.val_email.value = klien['email'] if klien['email'] else "-"
            self.val_alamat.value = klien['alamat'] if klien['alamat'] else "-"

            self.val_sesi.value = "0 Sesi"

            self.klien_info_card.visible = True
            self.empty_state_card.visible = False

        if self.main_page:
            try:
                self.update()
            except Exception:
                pass

    def mulai_sesi(self, e):
        if not self.dropdown_klien.value:
            self.show_snackbar("Mohon cari dan pilih klien terlebih dahulu dari daftar!", ft.Colors.RED)
            return

        self.selected_klien_id = int(self.dropdown_klien.value)

        self.session_name.value = self.val_nama.value
        self.session_details.value = f"{self.val_jk.value}  •  {self.val_umur.value}"

        self.view_presession.visible = False
        self.view_session.visible = True

        self.session_active = True
        self.time_counter = 0
        self.latest_prediction_result = None
        self.prediction_text.visible = False
        self.prediction_text.value = ""

        self.chart_data_hr.clear()
        self.chart_data_gsr.clear()
        self.chart_data_temp.clear()

        if self.main_page:
            self.update()

    def _on_sensor_data(self, hr_val, gsr_val, temp_val):
        """Callback yang dipanggil secara asinkron oleh SensorService setiap ada data baru"""
        if not self.session_active:
            return

        self.val_hr.value = str(int(hr_val))
        self.val_gsr.value = f"{gsr_val:.1f}"
        self.val_temp.value = f"{temp_val:.1f}"

        self.chart_data_hr.append(fc.LineChartDataPoint(self.time_counter, hr_val))
        self.chart_data_gsr.append(fc.LineChartDataPoint(self.time_counter, gsr_val))
        self.chart_data_temp.append(fc.LineChartDataPoint(self.time_counter, temp_val))

        for chart_comp in [self.chart_hr, self.chart_gsr, self.chart_temp]:
            chart_obj = chart_comp.content.controls[1].content
            if self.time_counter > 20:
                chart_obj.min_x = self.time_counter - 20
                chart_obj.max_x = self.time_counter
            else:
                chart_obj.min_x = 0
                chart_obj.max_x = 20

        self.time_counter += 1

        try:
            self.update()
        except Exception:
            pass

        if self.time_counter >= 60 and self.session_active:
            self.akhiri_sesi(None)

    def batal_sesi(self, e):
        self.session_active = False
        self.view_presession.visible = True
        self.view_session.visible = False
        self.dropdown_klien.value = None
        self.klien_info_card.visible = False
        self.empty_state_card.visible = True
        self.selected_klien_id = None
        self.latest_prediction_result = None

        self.val_hr.value = "--"
        self.val_gsr.value = "--"
        self.val_temp.value = "--"

        if self.main_page:
            self.update()

    def akhiri_sesi(self, e):
        if not self.session_active:
            return

        self.session_active = False

        if not self.chart_data_hr:
            self.show_snackbar("Tidak ada data telemetri yang terekam.", ft.Colors.RED_600)
            self.batal_sesi(None)
            return

        avg_hr = sum(p.y for p in self.chart_data_hr) / max(1, len(self.chart_data_hr))
        avg_gsr = sum(p.y for p in self.chart_data_gsr) / max(1, len(self.chart_data_gsr))
        avg_temp = sum(p.y for p in self.chart_data_temp) / max(1, len(self.chart_data_temp))

        arr_hr = [{"x": p.x, "y": p.y} for p in self.chart_data_hr]
        arr_gsr = [{"x": p.x, "y": p.y} for p in self.chart_data_gsr]
        arr_temp = [{"x": p.x, "y": p.y} for p in self.chart_data_temp]

        self.sesi_db.simpan_sesi(
            self.selected_klien_id,
            self.time_counter,
            round(avg_hr, 1),
            round(avg_gsr, 1),
            round(avg_temp, 2),
            arr_hr, arr_gsr, arr_temp,
            hasil_prediksi=self.latest_prediction_result
        )

        msg_text = f"Sesi Perekaman Data (Hasil: {self.latest_prediction_result or 'Normal'}) Berhasil Disimpan!"
        self.show_snackbar(msg_text, ft.Colors.GREEN_600)

        self.batal_sesi(None)

    def _create_chart(self, title, data_points, color, min_y, max_y, unit):
        mid_y = (min_y + max_y) / 2
        chart = fc.LineChart(
            data_series=[
                fc.LineChartData(
                    points=data_points,
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
            min_x=0, max_x=20,
            expand=True,
            left_axis=fc.ChartAxis(
                labels=[
                    fc.ChartAxisLabel(value=min_y, label=ft.Text(f"{min_y}{unit}", size=10, color=ft.Colors.GREY_500)),
                    fc.ChartAxisLabel(value=mid_y, label=ft.Text(f"{mid_y:g}{unit}", size=10, color=ft.Colors.GREY_500)),
                    fc.ChartAxisLabel(value=max_y, label=ft.Text(f"{max_y}{unit}", size=10, color=ft.Colors.GREY_500))
                ],
                label_size=40
            )
        )
        return ft.Container(
            content=ft.Column([
                ft.Text(f"{title} (Rentang: {min_y} - {max_y}{unit})", size=13, weight="bold", color=ft.Colors.GREY_700),
                ft.Container(content=chart, expand=True)
            ]),
            expand=True,
            height=180,
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.Border.all(1, "#e2e8f0"),
        )
