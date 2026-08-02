import flet as ft
import shutil
import os
import json

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "settings.json")

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
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

        self.file_picker = ft.FilePicker()

        self.input_nama = ft.TextField(
            label="Nama Penanda Tangan",
            value=self.nama_penanda_tangan,
            width=400,
            hint_text="Contoh: Dr. Andi Setiawan, M.Kes",
            on_change=self.save_nama
        )

        self.img_preview = ft.Image(
            src=self.kop_surat_path if self.kop_surat_path else None,
            width=300,
            height=150,
            fit=ft.BoxFit.CONTAIN,
            visible=bool(self.kop_surat_path)
        )

        self.btn_hapus_kop = ft.Button(
            "Hapus Kop",
            icon=ft.Icons.DELETE,
            bgcolor=ft.Colors.RED_500,
            color=ft.Colors.WHITE,
            on_click=self.hapus_kop,
            visible=bool(self.kop_surat_path)
        )

        tab_surat_content = ft.Container(
            padding=30,
            content=ft.Column([
                ft.Text("Pengaturan Surat & Dokumen", size=22, weight="bold", color="#1e293b"),
                ft.Divider(height=20, color=ft.Colors.GREY_200),

                ft.Text("Kop Surat", weight="bold", size=16),
                ft.Text("Upload gambar kop surat (format: jpg, png) yang akan digunakan saat mencetak dokumen.", color=ft.Colors.GREY_600),
                ft.Row([
                    ft.Button(
                        "Pilih Gambar",
                        icon=ft.Icons.UPLOAD_FILE,
                        bgcolor=ft.Colors.BLUE_600,
                        color=ft.Colors.WHITE,
                        on_click=self.pilih_kop_surat
                    ),
                    self.btn_hapus_kop
                ]),
                self.img_preview,

                ft.Divider(height=30, color=ft.Colors.TRANSPARENT),

                ft.Text("Penanda Tangan", weight="bold", size=16),
                ft.Text("Nama yang akan tertera di bagian bawah (tanda tangan) pada dokumen yang dicetak.", color=ft.Colors.GREY_600),
                self.input_nama,

                ft.Row([
                    ft.Button(
                        "Simpan Nama",
                        icon=ft.Icons.SAVE,
                        on_click=self.simpan_manual,
                        bgcolor=ft.Colors.GREEN_600,
                        color=ft.Colors.WHITE,
                        style=ft.ButtonStyle(padding=15)
                    )
                ])
            ], scroll=ft.ScrollMode.AUTO, spacing=10)
        )

        tab_umum_content = ft.Container(
            padding=30,
            content=ft.Column([
                ft.Text("Pengaturan Umum", size=22, weight="bold", color="#1e293b"),
                ft.Divider(height=20, color=ft.Colors.GREY_200),
                ft.Text("Pengaturan umum aplikasi (Tema, Bahasa, dsb) akan ditambahkan di sini pada pengembangan berikutnya.", color=ft.Colors.GREY_600)
            ])
        )

        self.tabs = ft.Tabs(
            length=2,
            selected_index=0,
            animation_duration=300,
            expand=True,
            content=ft.Column([
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Surat-menyurat", icon=ft.Icons.MAIL_OUTLINE),
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
                self.file_picker,
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

    async def pilih_kop_surat(self, e):
        files = await self.file_picker.pick_files(allow_multiple=False, allowed_extensions=["png", "jpg", "jpeg"])
        if files:
            file_info = files[0]
            src_path = file_info.path

            assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "assets")
            if not os.path.exists(assets_dir):
                os.makedirs(assets_dir)

            filename = f"kop_surat_{file_info.name}"
            dest_path = os.path.join(assets_dir, filename)

            shutil.copy2(src_path, dest_path)

            self.kop_surat_path = filename
            self.settings["kop_surat_path"] = self.kop_surat_path
            save_settings(self.settings)

            self.img_preview.src = self.kop_surat_path
            self.img_preview.visible = True

            self.btn_hapus_kop.visible = True

            self.show_snackbar("Kop Surat berhasil diunggah!", ft.Colors.GREEN)

            try:
                self.update()
            except RuntimeError:
                pass

    def hapus_kop(self, e):
        self.kop_surat_path = ""
        self.settings["kop_surat_path"] = ""
        save_settings(self.settings)

        self.img_preview.visible = False

        self.btn_hapus_kop.visible = False

        self.show_snackbar("Kop Surat telah dihapus!", ft.Colors.ORANGE)
        try:
            self.update()
        except RuntimeError:
            pass

    def save_nama(self, e):
        self.settings["nama_penanda_tangan"] = self.input_nama.value
        save_settings(self.settings)

    def simpan_manual(self, e):
        self.save_nama(e)
        self.show_snackbar("Nama penanda tangan berhasil disimpan!", ft.Colors.BLUE)

    def show_snackbar(self, message, color):
        snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.main_page.overlay.append(snackbar)
        snackbar.open = True

        try:
            self.main_page.update()
        except RuntimeError:
            pass

    def handle_resize(self, e):
        pass
