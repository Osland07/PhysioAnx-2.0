import flet as ft

class AppSidebar(ft.Container):
    def __init__(self, on_menu_change):
        super().__init__()
        self.selected_index = 0
        self.on_menu_change_callback = on_menu_change
        self.width = 260
        self.padding = ft.Padding(left=15, top=25, right=15, bottom=25)
        self.bgcolor = ft.Colors.TRANSPARENT

        self.menus = [
            {"icon": ft.Icons.DASHBOARD_OUTLINED, "sel_icon": ft.Icons.DASHBOARD_ROUNDED, "label": "Dashboard"},
            {"icon": ft.Icons.PEOPLE_OUTLINE_ROUNDED, "sel_icon": ft.Icons.PEOPLE_ROUNDED, "label": "Klien"},
            {"icon": ft.Icons.ADD_COMMENT_OUTLINED, "sel_icon": ft.Icons.ADD_COMMENT_ROUNDED, "label": "Sesi Baru"},
            {"icon": ft.Icons.HISTORY_OUTLINED, "sel_icon": ft.Icons.HISTORY_ROUNDED, "label": "Riwayat"},
            {"icon": ft.Icons.SETTINGS_OUTLINED, "sel_icon": ft.Icons.SETTINGS_ROUNDED, "label": "Pengaturan"},
        ]

        self.menu_col = ft.Column(spacing=8)

        self.content = ft.Column([
            ft.Container(
                content=ft.Image(src="Logo_Sidebar.png", width=230, height=110, fit="contain"),
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding(0, 0, 0, 30)
            ),
            self.menu_col
        ])

        self.render_menus()

    def render_menus(self):
        self.menu_col.controls.clear()
        for i, m in enumerate(self.menus):
            is_sel = (i == self.selected_index)
            icon_to_use = m["sel_icon"] if is_sel else m["icon"]
            color_to_use = ft.Colors.BLUE_800 if is_sel else ft.Colors.BLUE_GREY_700

            btn = ft.Container(
                content=ft.Row([
                    ft.Icon(icon_to_use, color=color_to_use, size=22),
                    ft.Text(m["label"], weight="bold" if is_sel else "w500", color=color_to_use, size=14)
                ], spacing=15),
                bgcolor="#e0e7ff" if is_sel else ft.Colors.TRANSPARENT,
                padding=ft.Padding(left=15, top=12, right=15, bottom=12),
                border_radius=8,
                ink=True,
                on_click=self.create_click_handler(i)
            )
            self.menu_col.controls.append(btn)

    def create_click_handler(self, index):
        def on_click(e):
            if self.selected_index == index:
                return
            self.selected_index = index
            self.render_menus()
            self.update()

            class DummyEvent:
                pass
            ev = DummyEvent()
            ev.control = self
            self.on_menu_change_callback(ev)

        return on_click
