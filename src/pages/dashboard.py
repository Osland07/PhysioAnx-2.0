import flet as ft

def DashboardPage():
    return ft.Container(
        content=ft.Column([
            ft.Text("Dashboard Utama", size=32, weight=ft.FontWeight.W_800, color="#1e293b"),
            ft.Text("Selamat datang di Sistem Informasi Manajemen PhysioAnx.", size=16, color="#64748b")
        ]),
        alignment=ft.Alignment(-1.0, -1.0),
        expand=True,
        bgcolor=ft.Colors.WHITE,
        border_radius=ft.BorderRadius(top_left=35, top_right=0, bottom_left=35, bottom_right=0),
        padding=50,
        margin=ft.Margin(left=0, top=15, right=15, bottom=15),
        shadow=ft.BoxShadow(
            spread_radius=0,
            blur_radius=20,
            color=ft.Colors.with_opacity(0.04, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        )
    )
