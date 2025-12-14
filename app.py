import flet as ft
import os

def main(page: ft.Page):
    page.title = "My Flet App"
    page.add(ft.Text("Hello, world!"))

# Lấy port do Render cung cấp
port = int(os.environ.get("PORT", 8550))

ft.app(target=main, view=ft.WEB_BROWSER, port=port, host="0.0.0.0")
