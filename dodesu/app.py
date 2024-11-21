import flet as ft
from .doudesu_flet import DoujindesuApp


class DoujindesuAppWrapper:
    def __init__(self):
        self.app = DoujindesuApp()
        self.theme_mode = ft.ThemeMode.DARK

    def toggle_theme(self, e):
        self.theme_mode = (
            ft.ThemeMode.LIGHT
            if self.theme_mode == ft.ThemeMode.DARK
            else ft.ThemeMode.DARK
        )
        e.page.theme_mode = self.theme_mode
        e.page.update()

    def build(self):
        toggle_theme_button = ft.IconButton(
            icon=ft.icons.LIGHT_MODE
            if self.theme_mode == ft.ThemeMode.DARK
            else ft.icons.DARK_MODE,
            on_click=self.toggle_theme,
        )
        app_content = self.app.build()
        return ft.Column([toggle_theme_button, app_content], expand=True)
