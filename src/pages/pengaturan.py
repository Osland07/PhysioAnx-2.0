import flet as ft
import shutil
import os
import json
from services.sensor_service import SensorService

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"kop_surat_path": "", "nama_penanda_tangan": ""}

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

class PengaturanPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page

        self.settings = load_settings()
        self.kop_surat_path = self.settings.get("kop_surat_path", "")
        self.nama_penanda_tangan = self.settings.get("nama_penanda_tangan", "")

        # Sensor Service & Connection Status
        self.sensor_service = SensorService.get_instance(page)

        # Tab Dokumen Controls
        self.input_nama = ft.TextField(
            label="Nama Penanda Tangan",
            value=self.nama_penanda_tangan,
            width=400,
            hint_text="Contoh: Dr. Andi Setiawan, M.Kes",
            on_change=self.save_nama
        )

        full_preview_path = self._get_full_kop_path()
        self.img_preview = ft.Image(
            src=full_preview_path if (full_preview_path and os.path.exists(full_preview_path)) else None,
            width=420,
            height=130,
            fit=ft.BoxFit.CONTAIN,
            visible=bool(self.kop_surat_path and os.path.exists(full_preview_path))
        )

        self.btn_hapus_kop = ft.Button(
            "Gunakan Kop Default",
            icon=ft.Icons.RESTORE,
            bgcolor=ft.Colors.RED_500,
            color=ft.Colors.WHITE,
            on_click=self.hapus_kop,
            visible=bool(self.kop_surat_path)
        )

        tab_surat_content = ft.Container(
            padding=30,
            content=ft.Column([
                ft.Text("Kop Surat Custom", weight="bold", size=16),
                ft.Text("Upload gambar Kop Surat (PNG / JPG). Jika tidak diupload, dokumen PDF otomatis menggunakan Kop Default Resmi PhysioAnx.", color=ft.Colors.GREY_600),
                ft.Row([
                    ft.Button(
                        "Upload Kop Surat",
                        icon=ft.Icons.UPLOAD_FILE_ROUNDED,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        on_click=self.pilih_kop_surat
                    ),
                    self.btn_hapus_kop
                ]),
                self.img_preview,

                ft.Divider(height=25, color=ft.Colors.TRANSPARENT),

                ft.Text("Penanda Tangan", weight="bold", size=16),
                ft.Text("Nama yang akan tertera di bagian bawah (tanda tangan) pada dokumen yang dicetak.", color=ft.Colors.GREY_600),
                self.input_nama,

                ft.Row([
                    ft.Button(
                        "Simpan Pengaturan",
                        icon=ft.Icons.SAVE,
                        on_click=self.simpan_manual,
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(padding=15)
                    )
                ])
            ], scroll=ft.ScrollMode.AUTO, spacing=12)
        )

        # Tab Umum Connection & System Info Controls
        self.ble_status_icon = ft.Icon(ft.Icons.BLUETOOTH_SEARCHING, color=ft.Colors.AMBER_600, size=20)
        self.ble_status_text = ft.Text("Mencari Device...", size=14, weight="bold", color=ft.Colors.AMBER_800)
        self.ble_status_badge = ft.Container(
            content=ft.Row([self.ble_status_icon, self.ble_status_text], spacing=6),
            padding=ft.Padding(left=12, right=12, top=6, bottom=6),
            bgcolor=ft.Colors.AMBER_50,
            border=ft.Border.all(1, ft.Colors.AMBER_200),
            border_radius=20
        )
        self.ble_status_detail = ft.Text(self.sensor_service.last_status_detail, size=13, color=ft.Colors.GREY_600)

        # Register Sensor Status Callback
        self.sensor_service.register_callbacks(on_status=self._on_sensor_status)

        def create_info_row(label: str, value: str, icon=None):
            return ft.Row([
                ft.Row([
                    ft.Icon(icon, size=18, color=ft.Colors.BLUE_600) if icon else ft.Container(),
                    ft.Text(label, size=14, color=ft.Colors.GREY_700, weight="w500")
                ], spacing=8),
                ft.Text(value, size=14, weight="bold", color=ft.Colors.GREY_900)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        card_ble = ft.Container(
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.GREY_200),
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.BLUETOOTH, color=ft.Colors.BLUE_600, size=22),
                        ft.Text("Koneksi", size=16, weight="bold", color="#1e293b")
                    ], spacing=10),
                    self.ble_status_badge
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=15, color=ft.Colors.GREY_200),
                create_info_row("Target Device", "PhysioAnx", ft.Icons.DEVICES),
                create_info_row("Device ID", "PAX-BLE-8F42A1", ft.Icons.FINGERPRINT),
                create_info_row("Status", self.sensor_service.last_status_detail, ft.Icons.CELL_TOWER),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    ft.Button(
                        "Hubungkan Ulang",
                        icon=ft.Icons.REFRESH,
                        on_click=self.reconnect_ble,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE
                    )
                ], alignment=ft.MainAxisAlignment.END)
            ], spacing=10)
        )

        card_sync = ft.Container(
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.GREY_200),
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.CLOUD_SYNC, color=ft.Colors.GREEN_600, size=22),
                    ft.Text("Sinkronisasi Cloud", size=16, weight="bold", color="#1e293b")
                ], spacing=10),
                ft.Divider(height=15, color=ft.Colors.GREY_200),
                create_info_row("Penyimpanan Lokal", "PhysioAnx.db", ft.Icons.STORAGE),
                create_info_row("Status Sinkronisasi", "Aktif", ft.Icons.CLOUD_DONE)
            ], spacing=10)
        )

        card_system = ft.Container(
            padding=20,
            bgcolor=ft.Colors.GREY_50,
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.GREY_200),
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.INDIGO_600, size=22),
                    ft.Text("Informasi Sistem", size=16, weight="bold", color="#1e293b")
                ], spacing=10),
                ft.Divider(height=15, color=ft.Colors.GREY_200),
                create_info_row("Versi Aplikasi", "PhysioAnx System v2.0", ft.Icons.VERIFIED_USER_OUTLINED)
            ], spacing=10)
        )

        tab_umum_content = ft.Container(
            padding=30,
            content=ft.Column([
                card_ble,
                card_sync,
                card_system
            ], scroll=ft.ScrollMode.AUTO, spacing=20)
        )

        self.tabs = ft.Tabs(
            length=2,
            selected_index=0,
            animation_duration=300,
            expand=True,
            content=ft.Column([
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Dokumen", icon=ft.Icons.ARTICLE_OUTLINED),
                        ft.Tab(label="Umum", icon=ft.Icons.SETTINGS)
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        tab_surat_content,
                        tab_umum_content
                    ]
                )
            ], expand=True)
        )

        self.content = ft.Container(
            content=ft.Column([
                ft.Text("Pengaturan Aplikasi", size=28, weight=ft.FontWeight.W_800, color="#1e293b"),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                self.tabs
            ], expand=True),
            padding=40,
            expand=True
        )

        self.expand = True
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = ft.BorderRadius(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.margin = ft.Margin(left=0, top=15, right=15, bottom=15)
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=20, color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK), offset=ft.Offset(0, 4))

        # Initial trigger connection status UI update
        self._update_ble_status_ui(self.sensor_service.connection_state, self.sensor_service.last_status_detail)

    def _get_full_kop_path(self):
        if not self.kop_surat_path:
            return ""
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
        return os.path.join(assets_dir, self.kop_surat_path)

    def _on_sensor_status(self, category, status_code, message):
        if category == "connection":
            self._update_ble_status_ui(status_code, message)

    def _update_ble_status_ui(self, status_code: str, message: str):
        if status_code == "connected":
            self.ble_status_icon.name = ft.Icons.BLUETOOTH_CONNECTED
            self.ble_status_icon.color = ft.Colors.GREEN_600
            self.ble_status_text.value = "Terhubung"
            self.ble_status_text.color = ft.Colors.GREEN_800
            self.ble_status_badge.bgcolor = ft.Colors.GREEN_50
            self.ble_status_badge.border = ft.Border.all(1, ft.Colors.GREEN_300)
        elif status_code == "searching":
            self.ble_status_icon.name = ft.Icons.BLUETOOTH_SEARCHING
            self.ble_status_icon.color = ft.Colors.AMBER_600
            self.ble_status_text.value = "Mencari Device..."
            self.ble_status_text.color = ft.Colors.AMBER_800
            self.ble_status_badge.bgcolor = ft.Colors.AMBER_50
            self.ble_status_badge.border = ft.Border.all(1, ft.Colors.AMBER_200)
        else:
            self.ble_status_icon.name = ft.Icons.BLUETOOTH_DISABLED
            self.ble_status_icon.color = ft.Colors.RED_600
            self.ble_status_text.value = "Terputus"
            self.ble_status_text.color = ft.Colors.RED_800
            self.ble_status_badge.bgcolor = ft.Colors.RED_50
            self.ble_status_badge.border = ft.Border.all(1, ft.Colors.RED_200)

        self.ble_status_detail.value = message
        try:
            self.update()
        except Exception:
            pass

    def reconnect_ble(self, e):
        self.sensor_service.start()
        self.show_snackbar("Memulai ulang pencarian koneksi Bluetooth BLE...", ft.Colors.BLUE_600)

    def pilih_kop_surat(self, e):
        try:
            from tkinter import filedialog, Tk
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            selected_file = filedialog.askopenfilename(
                title="Pilih Gambar Kop Surat Custom",
                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.PNG;*.JPG;*.JPEG")]
            )
            root.destroy()

            if selected_file:
                assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
                os.makedirs(assets_dir, exist_ok=True)
                filename = f"kop_surat_{os.path.basename(selected_file)}"
                dest_path = os.path.join(assets_dir, filename)
                shutil.copy(selected_file, dest_path)

                self.kop_surat_path = filename
                self.settings["kop_surat_path"] = filename
                save_settings(self.settings)

                self.img_preview.src = dest_path
                self.img_preview.visible = True
                self.btn_hapus_kop.visible = True
                self.show_snackbar("Kop Surat Custom berhasil diupload!", ft.Colors.GREEN_600)
                try:
                    self.update()
                except Exception:
                    pass
        except Exception as ex:
            self.show_snackbar(f"Gagal memilih file: {ex}", ft.Colors.RED_600)

    def hapus_kop(self, e):
        self.kop_surat_path = ""
        self.settings["kop_surat_path"] = ""
        save_settings(self.settings)

        self.img_preview.visible = False
        self.btn_hapus_kop.visible = False
        self.show_snackbar("Kop Surat diubah kembali ke Kop Default Resmi PhysioAnx!", ft.Colors.BLUE_600)
        try:
            self.update()
        except Exception:
            pass

    def save_nama(self, e):
        self.settings["nama_penanda_tangan"] = self.input_nama.value
        save_settings(self.settings)

    def simpan_manual(self, e):
        self.save_nama(e)
        self.show_snackbar("Pengaturan berhasil disimpan!", ft.Colors.GREEN_600)

    def show_snackbar(self, message, color):
        snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.main_page.snack_bar = snackbar
        snackbar.open = True

        try:
            self.main_page.update()
        except Exception:
            pass

    def handle_resize(self, e):
        pass
