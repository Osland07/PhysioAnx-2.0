import flet as ft

from components.sidebar import AppSidebar
from pages.dashboard import DashboardPage
from pages.klien import KlienPage
from pages.sesi_baru import SesiBaruPage
from pages.riwayat import RiwayatPage

def main(page: ft.Page):
    page.title = "PhysioAnx"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.window.width = 1100
    page.window.height = 750
    page.bgcolor = "#f1f5f9"
    page.window.icon = "Logo.ico"

    # Start persistent Bluetooth BLE Service
    from services.sensor_service import SensorService
    SensorService.get_instance(page)

    content_area = ft.Container(expand=True)
    content_area.content = DashboardPage()

    def on_menu_change(e):
        from services.cloud_sync import CloudSyncService
        import os
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'physioanx.db')
        sync_service = CloudSyncService()
        sync_service.run_in_background(sync_service.pull_all_from_cloud, db_path, True)

        idx = e.control.selected_index
        if idx == 0:
            content_area.content = DashboardPage()
        elif idx == 1:
            content_area.content = KlienPage(page)
        elif idx == 2:
            content_area.content = SesiBaruPage(page)
        elif idx == 3:
            content_area.content = RiwayatPage(page)
        elif idx == 4:
            from pages.pengaturan import PengaturanPage
            content_area.content = PengaturanPage(page)
        else:
            content_area.content = ft.Container(
                content=ft.Text(f"Halaman Menu ke-{idx} Belum Dibuat", size=24, color=ft.Colors.GREY_600),
                alignment=ft.Alignment(0,0), expand=True, bgcolor=ft.Colors.WHITE,
                border_radius=ft.BorderRadius(top_left=35, top_right=0, bottom_left=35, bottom_right=0),
                margin=ft.Margin(left=0, top=15, right=15, bottom=15)
            )

        if hasattr(content_area.content, 'handle_resize'):
            content_area.content.handle_resize(None)

        page.update()

    def handle_page_resize(e):
        if hasattr(content_area.content, 'handle_resize'):
            content_area.content.handle_resize(e)

    page.on_resize = handle_page_resize

    sidebar = AppSidebar(on_menu_change)

    page.add(
        ft.Row([sidebar, content_area], expand=True, spacing=0)
    )

    if hasattr(content_area.content, 'handle_resize'):
        content_area.content.handle_resize(None)
        page.update()

if __name__ == '__main__':
    ft.run(main, assets_dir="../assets")
