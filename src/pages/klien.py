import flet as ft
import datetime
import re
from services.klien_service import KlienService

class KlienPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.db = KlienService()

        self.search_input = ft.TextField(
            hint_text="Cari klien...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=8,
            expand=True,
            height=45,
            content_padding=0,
            on_change=self.on_search
        )

        self.datatable = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("NAMA", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("L/P", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("UMUR", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("NO HP", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("EMAIL", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("ALAMAT", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("AKSI", weight="bold"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
            ],
            rows=[],
            heading_row_color=ft.Colors.BLUE_GREY_50,
            border_radius=10,
            vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            horizontal_lines=ft.BorderSide(1, ft.Colors.GREY_200),
            expand=True
        )

        self.main_content = ft.Container(
            content=ft.Column([
                ft.Text("Manajemen Data Klien", size=28, weight=ft.FontWeight.W_800, color="#1e293b"),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                ft.Row([
                    self.search_input,
                    ft.Button(
                        "Tambah Klien",
                        icon=ft.Icons.ADD,
                        on_click=self.open_tambah_panel,
                        style=ft.ButtonStyle(bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, padding=15, shape=ft.RoundedRectangleBorder(radius=10))
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),

                ft.Container(
                    content=ft.ListView([
                        ft.Row([self.datatable], expand=True, scroll=ft.ScrollMode.ADAPTIVE)
                    ], expand=True),
                    expand=True
                )
            ], expand=True),
            padding=40,
            expand=True
        )

        self.input_id = ft.Text(visible=False)
        self.input_nama = ft.TextField(label="Nama Lengkap")
        self.input_jk = ft.Dropdown(
            label="Jenis Kelamin",
            options=[ft.dropdown.Option("Laki-laki"), ft.dropdown.Option("Perempuan")],
            width=400
        )

        self.date_picker = ft.DatePicker(
            on_change=self.on_date_picked,
            first_date=datetime.datetime(1930, 1, 1),
            last_date=datetime.datetime.now()
        )

        self.input_tgl = ft.TextField(
            label="Tanggal Lahir",
            read_only=True,
            on_click=self.open_date_picker
        )

        self.input_hp = ft.TextField(label="Nomor Telepon", keyboard_type=ft.KeyboardType.PHONE)
        self.input_email = ft.TextField(
            label="Email",
            keyboard_type=ft.KeyboardType.EMAIL,
            on_change=self.on_email_change
        )
        self.input_alamat = ft.TextField(label="Alamat", multiline=True, min_lines=3)
        self.panel_title = ft.Text("Tambah Klien", size=22, weight="bold", color="#1e293b")

        self.side_panel = ft.Container(
            content=ft.Column([
                ft.Row([
                    self.panel_title,
                    ft.IconButton(ft.Icons.CLOSE, on_click=self.close_panel)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.ListView([
                    self.input_nama, self.input_jk, self.input_tgl,
                    self.input_hp, self.input_email, self.input_alamat
                ], expand=True, spacing=15, padding=ft.Padding(0, 10, 0, 10)),
                ft.Row([
                    ft.Button("Simpan Data", on_click=self.save_data, bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE, expand=True)
                ])
            ]),
            width=400,
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=ft.BorderRadius(top_left=20, bottom_left=20, top_right=0, bottom_right=0),
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=30, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK), offset=ft.Offset(-5, 0)),
            right=-450,
            top=0,
            bottom=0,
            animate_position=ft.Animation(300, ft.AnimationCurve.DECELERATE)
        )

        self.content = ft.Stack([
            self.date_picker,
            self.main_content,
            self.side_panel
        ], expand=True)

        self.expand = True
        self.bgcolor = ft.Colors.WHITE
        self.border_radius = ft.BorderRadius(top_left=35, top_right=0, bottom_left=35, bottom_right=0)
        self.padding = 0
        self.margin = ft.Margin(left=0, top=15, right=15, bottom=15)
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=20, color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK), offset=ft.Offset(0, 4))

        self.load_data(initial_load=True)

    def handle_resize(self, e):
        width = self.main_page.window.width

        hide_indices = []
        if width < 1100:
            hide_indices.append(6)
        if width < 950:
            hide_indices.append(5)
        if width < 800:
            hide_indices.append(4)
        if width < 650:
            hide_indices.extend([0, 2])
        if width < 500:
            hide_indices.append(3)

        for i, col in enumerate(self.datatable.columns):
            col.visible = i not in hide_indices

        for row in self.datatable.rows:
            for i, cell in enumerate(row.cells):
                cell.visible = i not in hide_indices

        try:
            self.update()
        except RuntimeError:
            pass

    def show_snackbar(self, message, color):
        snackbar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.main_page.overlay.append(snackbar)
        snackbar.open = True
        self.main_page.update()

    def load_data(self, search_query="", initial_load=False):
        data_klien = self.db.get_all_klien(search_query)
        self.datatable.rows.clear()

        for klien in data_klien:
            jk_singkat = "L" if klien["jenis_kelamin"] == "Laki-laki" else ("P" if klien["jenis_kelamin"] == "Perempuan" else "-")

            umur = "-"
            if klien["tanggal_lahir"]:
                try:
                    tgl_lahir = datetime.datetime.strptime(klien["tanggal_lahir"], "%d-%m-%Y")
                    today = datetime.datetime.now()
                    umur_int = today.year - tgl_lahir.year - ((today.month, today.day) < (tgl_lahir.month, tgl_lahir.day))
                    umur = f"{umur_int} thn"
                except:
                    pass

            self.datatable.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(klien["id_klien"])),
                    ft.DataCell(ft.Text(klien["nama"])),
                    ft.DataCell(ft.Text(jk_singkat)),
                    ft.DataCell(ft.Text(umur)),
                    ft.DataCell(ft.Text(klien["no_hp"])),
                    ft.DataCell(ft.Text(klien["email"])),
                    ft.DataCell(ft.Text(klien["alamat"])),
                    ft.DataCell(ft.Row([
                        ft.Button("Edit", icon=ft.Icons.EDIT_ROUNDED, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.BLUE), on_click=lambda e, k=klien: self.open_edit_panel(k)),
                        ft.Button("Hapus", icon=ft.Icons.DELETE_ROUNDED, style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=ft.Colors.RED), on_click=lambda e, k=klien: self.open_delete_dialog(k))
                    ])),
                ])
            )

        self.handle_resize(None)

        if not initial_load:
            self.update()

    def on_search(self, e):
        self.load_data(e.control.value)

    def open_date_picker(self, e):
        self.date_picker.open = True
        self.main_page.update()

    def on_date_picked(self, e):
        if self.date_picker.value:
            self.input_tgl.value = self.date_picker.value.strftime("%d-%m-%Y")
            self.update()

    def open_tambah_panel(self, e):
        self.panel_title.value = "Tambah Klien Baru"
        self.input_id.value = ""
        self.input_nama.value = ""
        self.input_jk.value = None
        self.input_tgl.value = ""
        self.input_hp.value = ""
        self.input_email.value = ""
        self.input_alamat.value = ""

        self.side_panel.right = 0
        self.update()

    def open_edit_panel(self, klien):
        self.panel_title.value = f"Edit ({klien['id_klien']})"
        self.input_id.value = str(klien["id"])
        self.input_nama.value = klien["nama"]
        self.input_jk.value = klien["jenis_kelamin"]
        self.input_tgl.value = klien["tanggal_lahir"]
        self.input_hp.value = klien["no_hp"]
        self.input_email.value = klien["email"]
        self.input_alamat.value = klien["alamat"]

        self.side_panel.right = 0
        self.update()

    def close_panel(self, e=None):
        self.side_panel.right = -450
        self.update()

    def on_email_change(self, e):
        email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if self.input_email.value and not re.match(email_pattern, self.input_email.value):
            self.input_email.error = ft.Text("Format salah (contoh: nama@email.com)", color=ft.Colors.RED)
        else:
            self.input_email.error = None
        self.update()

    def save_data(self, e):
        if not self.input_nama.value:
            self.show_snackbar("Nama Lengkap wajib diisi!", ft.Colors.RED)
            return

        if self.input_email.error:
            self.show_snackbar("Mohon perbaiki format email terlebih dahulu!", ft.Colors.RED)
            return

        data = {
            "nama": self.input_nama.value,
            "jenis_kelamin": self.input_jk.value or "",
            "tanggal_lahir": self.input_tgl.value or "",
            "no_hp": self.input_hp.value or "",
            "email": self.input_email.value or "",
            "alamat": self.input_alamat.value or ""
        }

        if self.input_id.value == "":
            self.db.add_klien(data)
            self.show_snackbar("Sukses menambahkan klien!", ft.Colors.GREEN)
        else:
            self.db.update_klien(int(self.input_id.value), data)
            self.show_snackbar("Data berhasil diperbarui!", ft.Colors.BLUE)

        self.close_panel()
        self.load_data()

    def open_delete_dialog(self, klien):
        def close_delete(e):
            dialog.open = False
            self.main_page.update()

        def on_hapus(e):
            self.db.delete_klien(klien["id"])
            dialog.open = False
            self.main_page.update()
            self.load_data()
            self.show_snackbar("Klien telah dihapus!", ft.Colors.RED)

        dialog = ft.AlertDialog(
            title=ft.Text("Konfirmasi Hapus"),
            content=ft.Text(f"Apakah Anda yakin ingin menghapus data {klien['nama']}?"),
            actions=[
                ft.TextButton("Batal", on_click=close_delete),
                ft.Button("Ya, Hapus", on_click=on_hapus, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.main_page.overlay.append(dialog)
        dialog.open = True
        self.main_page.update()
