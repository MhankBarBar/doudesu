"""
GUI interface for the Doudesu.
This module requires the 'gui' extra dependencies.
"""

import json
import os
import sys
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path

from rich.console import Console

from ..core.doudesu import Doujindesu, Result
from ..utils.constants import DEFAULT_SETTINGS
from ..utils.converter import ImageToPDFConverter

console = Console()

if find_spec("flet"):
    import flet as ft

    from .components.loading import LoadingAnimation


@dataclass
class AppSettings:
    result_path: str = DEFAULT_SETTINGS["result_path"]
    default_theme: str = DEFAULT_SETTINGS["default_theme"]
    blur_thumbnails: bool = DEFAULT_SETTINGS["blur_thumbnails"]
    proxy: str = ""
    proxy_enabled: bool = False


class SettingsDialog(ft.AlertDialog):
    def __init__(self, page: ft.Page, app_instance, settings: AppSettings):
        super().__init__()
        self.page = page
        self.app = app_instance
        self.settings = settings
        self.modal = True

        self.setup_controls()
        self.content = self.build_content()
        self.title = ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD)
        self.actions = [
            ft.TextButton(
                "Cancel",
                on_click=self.cancel,
                style=ft.ButtonStyle(
                    color=ft.colors.ON_SURFACE_VARIANT,
                ),
            ),
            ft.TextButton(
                "Save",
                on_click=self.save,
                style=ft.ButtonStyle(
                    color=ft.colors.PRIMARY,
                ),
            ),
        ]
        self.shape = ft.RoundedRectangleBorder(radius=16)

    def setup_controls(self):
        label_style = ft.TextStyle(
            size=14,
            weight=ft.FontWeight.W_600,
            color=ft.colors.ON_SURFACE_VARIANT,
        )

        self.result_path = ft.TextField(
            label="Download Path",
            value=self.settings.result_path,
            border=ft.InputBorder.OUTLINE,
            expand=True,
            label_style=label_style,
            focused_border_color=ft.colors.PRIMARY,
            focused_color=ft.colors.PRIMARY,
        )

        self.proxy_enabled = ft.Switch(
            label="Enable Proxy",
            value=self.settings.proxy_enabled,
            active_color=ft.colors.PRIMARY,
            label_style=label_style,
        )

        self.proxy_url = ft.TextField(
            label="Proxy URL",
            value=self.settings.proxy,
            hint_text="e.g., http://proxy.example.com:8080",
            border=ft.InputBorder.OUTLINE,
            expand=True,
            disabled=not self.settings.proxy_enabled,
            label_style=label_style,
            focused_border_color=ft.colors.PRIMARY,
            focused_color=ft.colors.PRIMARY,
        )

        self.default_theme = ft.Dropdown(
            label="Default Theme",
            value=self.settings.default_theme,
            options=[
                ft.dropdown.Option("light", "Light Theme"),
                ft.dropdown.Option("dark", "Dark Theme"),
            ],
            border=ft.InputBorder.OUTLINE,
            expand=True,
            label_style=label_style,
            focused_border_color=ft.colors.PRIMARY,
            focused_color=ft.colors.PRIMARY,
        )

        self.blur_thumbnails = ft.Switch(
            label="Blur Thumbnails",
            value=self.settings.blur_thumbnails,
            active_color=ft.colors.PRIMARY,
            label_style=label_style,
        )

        def on_proxy_switch(e):
            self.proxy_url.disabled = not e.control.value
            self.proxy_url.update()

        self.proxy_enabled.on_change = on_proxy_switch

    def build_content(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.icons.FOLDER_ROUNDED,
                                            color=ft.colors.PRIMARY,
                                        ),
                                        ft.Text(
                                            "Download Settings",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.ON_SURFACE,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                ft.Container(
                                    content=ft.Row(
                                        [
                                            self.result_path,
                                            ft.IconButton(
                                                icon=ft.icons.FOLDER_OPEN_ROUNDED,
                                                icon_color=ft.colors.PRIMARY,
                                                tooltip="Browse",
                                                on_click=self.browse_folder,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    padding=ft.padding.only(left=34),
                                ),
                            ]
                        ),
                        padding=10,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=12,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.icons.SECURITY_ROUNDED,
                                            color=ft.colors.PRIMARY,
                                        ),
                                        ft.Text(
                                            "Proxy Settings",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.ON_SURFACE,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            self.proxy_enabled,
                                            self.proxy_url,
                                        ]
                                    ),
                                    padding=ft.padding.only(left=34),
                                ),
                            ]
                        ),
                        padding=10,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=12,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.icons.PALETTE_ROUNDED,
                                            color=ft.colors.PRIMARY,
                                        ),
                                        ft.Text(
                                            "Appearance",
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            color=ft.colors.ON_SURFACE,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            self.default_theme,
                                            self.blur_thumbnails,
                                        ]
                                    ),
                                    padding=ft.padding.only(left=34),
                                ),
                            ]
                        ),
                        padding=10,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        border_radius=12,
                    ),
                ],
                spacing=16,
            ),
            width=min(500, self.page.width * 0.8),
            padding=20,
            bgcolor=ft.colors.SURFACE,
        )

    def browse_folder(self, e):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e.path:
                self.result_path.value = e.path
                self.result_path.update()

        picker = ft.FilePicker(on_result=on_dialog_result)
        self.page.overlay.append(picker)
        self.page.update()
        picker.get_directory_path()

    def save(self, e):
        self.settings.result_path = self.result_path.value
        self.settings.default_theme = self.default_theme.value
        self.settings.blur_thumbnails = self.blur_thumbnails.value
        self.settings.proxy_enabled = self.proxy_enabled.value
        self.settings.proxy = self.proxy_url.value if self.proxy_enabled.value else ""

        settings_file = Path.home() / ".doudesu" / "settings.json"
        settings_file.parent.mkdir(exist_ok=True)
        settings_dict = {
            "result_path": self.settings.result_path,
            "default_theme": self.settings.default_theme,
            "blur_thumbnails": self.settings.blur_thumbnails,
            "proxy": self.settings.proxy,
            "proxy_enabled": self.settings.proxy_enabled,
        }
        with open(settings_file, "w") as f:
            json.dump(settings_dict, f, indent=4)

        self.app.result_folder = self.settings.result_path
        self.app.is_dark = self.settings.default_theme == "dark"
        self.app.blur_thumbnails = self.settings.blur_thumbnails

        if self.settings.proxy_enabled and self.settings.proxy:
            os.environ["HTTP_PROXY"] = self.settings.proxy
            os.environ["HTTPS_PROXY"] = self.settings.proxy
        else:
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)

        self.open = False
        self.page.update()

    def cancel(self, e):
        self.open = False
        self.page.update()


def run_gui(browser_mode: bool = False):
    """Run the GUI version of the application."""
    try:

        def main(page: ft.Page):
            page.title = "Doujindesu Downloader"
            page.window.width = 1100
            page.window.height = 900
            page.window.resizable = True

            app = DoujindesuApp()
            app.set_page(page)

        assets_dir = Path(__file__).parent.parent / "assets"

        if browser_mode:
            ft.app(
                target=main,
                view=ft.AppView.WEB_BROWSER,
                port=6969,
                assets_dir=assets_dir,
            )
        else:
            ft.app(target=main, assets_dir=assets_dir)
    except ImportError:
        console.print(
            "[red]GUI dependencies not installed. Please install with:[/red]"
            "\n[yellow]pip install doudesu\[gui][/yellow]"  # noqa: W605
        )
        sys.exit(1)


class DoujindesuApp:
    def __init__(self):
        self.page = None
        self.doujindesu = None
        self.results = []
        self.selected_result = None
        self.next_page_url = None
        self.previous_page_url = None
        self.result_folder = DEFAULT_SETTINGS["result_path"]
        self.browser_mode = True

        self.is_dark = DEFAULT_SETTINGS["default_theme"] == "dark"
        self.blur_thumbnails = DEFAULT_SETTINGS["blur_thumbnails"]
        self.theme_mode = ft.ThemeMode.DARK if self.is_dark else ft.ThemeMode.LIGHT

        self.selected_nav_index = 0

        os.makedirs(self.result_folder, exist_ok=True)

        self.main_status_text = ft.Text(
            value="",
            size=16,
            color=ft.colors.PINK,
            visible=False,
        )

        self.search_status_text = ft.Text(
            value="",
            size=16,
            color=ft.colors.PINK,
            visible=False,
        )

        self.settings = self.load_settings()

        self.result_folder = self.settings.result_path
        self.is_dark = self.settings.default_theme == "dark"
        self.blur_thumbnails = self.settings.blur_thumbnails

        if self.settings.proxy_enabled and self.settings.proxy:
            os.environ["HTTP_PROXY"] = self.settings.proxy
            os.environ["HTTPS_PROXY"] = self.settings.proxy

        self.initialize_controls()

        # Get proxy settings
        self.proxy = None
        if self.settings.proxy_enabled and self.settings.proxy:
            self.proxy = {"http": self.settings.proxy, "https": self.settings.proxy}

    def load_settings(self) -> AppSettings:
        settings_file = Path.home() / ".doudesu" / "settings.json"
        if settings_file.exists():
            with open(settings_file) as f:
                data = json.load(f)
                return AppSettings(**data)
        return AppSettings()

    def show_settings(self, e):
        dialog = SettingsDialog(self.page, self, self.settings)
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def initialize_controls(self):
        """Initialize all controls but don't create views yet."""
        self.logo = ft.Image(
            src="/images/logo.png",
            width=None,
            height=None,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(12),
            expand=True,
        )

        input_style = {
            "width": None,
            "expand": True,
            "border_radius": 12,
            "border_color": ft.colors.OUTLINE,
            "focused_border_color": ft.colors.PINK,
            "cursor_color": ft.colors.PINK,
            "text_size": 16,
            "content_padding": ft.padding.symmetric(horizontal=20, vertical=16),
            "filled": True,
            "bgcolor": ft.colors.SURFACE,
        }

        self.search_query = ft.TextField(
            label="Search manga",
            hint_text="Enter manga name...",
            prefix_icon=ft.icons.SEARCH_ROUNDED,
            border=ft.InputBorder.OUTLINE,
            visible=True,
            on_submit=self.handle_search,
            **input_style,
        )

        self.url_input = ft.TextField(
            label="Manga URL",
            hint_text="Enter manga URL here...",
            prefix_icon=ft.icons.LINK_ROUNDED,
            border=ft.InputBorder.OUTLINE,
            visible=False,
            on_submit=self.handle_download_by_url,
            **input_style,
        )

        button_style = {
            "style": ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.colors.PINK,
                    ft.ControlState.HOVERED: ft.colors.PINK_300,
                },
                shape={
                    ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=12),
                },
                padding=ft.padding.symmetric(horizontal=32, vertical=20),
                animation_duration=200,
                shadow_color=ft.colors.with_opacity(0.2, ft.colors.SHADOW),
                elevation={"pressed": 0, "": 2},
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.ON_PRIMARY),
            ),
            "color": ft.colors.ON_PRIMARY,
        }

        self.search_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.SEARCH_ROUNDED, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Text("Search", size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE),
                ],
                tight=True,
                spacing=8,
            ),
            on_click=self.handle_search,
            **button_style,
        )

        self.download_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.DOWNLOAD_ROUNDED, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Text("Download", size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT),
                ],
                tight=True,
                spacing=8,
            ),
            on_click=self.handle_download_by_url,
            visible=False,
            **button_style,
        )

        self.previous_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.ARROW_BACK, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Text("Previous", size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT),
                ],
                tight=True,
                spacing=8,
            ),
            on_click=self.handle_previous,
            visible=False,
            **button_style,
        )

        self.next_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.ARROW_FORWARD, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Text("Next", size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT),
                ],
                tight=True,
                spacing=8,
            ),
            on_click=self.handle_next,
            visible=False,
            **button_style,
        )

        self.nav_rail = ft.Container(
            content=ft.Column(
                [
                    ft.IconButton(
                        icon=ft.icons.DARK_MODE_ROUNDED,
                        selected_icon=ft.icons.LIGHT_MODE_ROUNDED,
                        icon_color=ft.colors.PINK,
                        selected=self.is_dark,
                        on_click=self.toggle_theme,
                        tooltip="Toggle theme",
                        style=ft.ButtonStyle(
                            shape={
                                ft.ControlState.DEFAULT: ft.CircleBorder(),
                            },
                            overlay_color=ft.colors.with_opacity(0.1, ft.colors.PINK),
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.icons.BLUR_ON_ROUNDED,
                        selected_icon=ft.icons.BLUR_OFF_ROUNDED,
                        icon_color=ft.colors.PINK,
                        selected=self.blur_thumbnails,
                        on_click=self.toggle_blur,
                        tooltip="Toggle blur",
                        style=ft.ButtonStyle(
                            shape={
                                ft.ControlState.DEFAULT: ft.CircleBorder(),
                            },
                            overlay_color=ft.colors.with_opacity(0.1, ft.colors.PINK),
                        ),
                    ),
                    ft.Divider(height=20, thickness=1),
                    ft.IconButton(
                        icon=ft.icons.SEARCH_ROUNDED,
                        icon_color=ft.colors.PINK if self.selected_nav_index == 0 else ft.colors.ON_SURFACE_VARIANT,
                        selected=self.selected_nav_index == 0,
                        on_click=lambda e: self.handle_option_change(0),
                        tooltip="Search",
                        style=ft.ButtonStyle(
                            shape={
                                ft.ControlState.DEFAULT: ft.CircleBorder(),
                            },
                            overlay_color=ft.colors.with_opacity(0.1, ft.colors.PINK),
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.icons.LINK_ROUNDED,
                        icon_color=ft.colors.PINK if self.selected_nav_index == 1 else ft.colors.ON_SURFACE_VARIANT,
                        selected=self.selected_nav_index == 1,
                        on_click=lambda e: self.handle_option_change(1),
                        tooltip="Download by URL",
                        style=ft.ButtonStyle(
                            shape={
                                ft.ControlState.DEFAULT: ft.CircleBorder(),
                            },
                            overlay_color=ft.colors.with_opacity(0.1, ft.colors.PINK),
                        ),
                    ),
                    ft.Divider(height=20, thickness=1),
                    ft.IconButton(
                        icon=ft.icons.SETTINGS,
                        icon_color=ft.colors.ON_SURFACE_VARIANT,
                        selected=False,
                        on_click=self.show_settings,
                        tooltip="Settings",
                        style=ft.ButtonStyle(
                            shape={
                                ft.ControlState.DEFAULT: ft.CircleBorder(),
                            },
                            overlay_color=ft.colors.with_opacity(0.1, ft.colors.PINK),
                        ),
                    ),
                ],
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.START,
            ),
            width=80,
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=ft.padding.only(top=20),
            border=ft.border.only(right=ft.BorderSide(1, ft.colors.OUTLINE)),
        )

        self.is_downloading = False

        self.search_results = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            animate_size=300,
        )

        self.loading_animation = LoadingAnimation()
        self.download_progress = ft.ProgressBar(visible=False)
        self.download_status = ft.Text(visible=False)

        self.snackbar = ft.SnackBar(
            content=ft.Text(""),
            bgcolor=ft.colors.INVERSE_SURFACE,
            action_color=ft.colors.RED,
            action="Dismiss",
        )

        self.download_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.DOWNLOAD_ROUNDED, color=ft.colors.ON_SURFACE),
                            ft.Text(
                                "Downloading...",
                                size=14,
                                weight=ft.FontWeight.W_300,
                                color=ft.colors.ON_SURFACE,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        "",
                        size=12,
                        color=ft.colors.ON_SURFACE_VARIANT,
                    ),
                    ft.ProgressBar(
                        width=None,
                        expand=True,
                        height=4,
                        color=ft.colors.PINK,
                        bgcolor=ft.colors.SURFACE_VARIANT,
                    ),
                    ft.Text(
                        "",
                        size=12,
                        color=ft.colors.ON_SURFACE_VARIANT,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.colors.SURFACE,
            padding=20,
            border_radius=16,
            width=min(280, self.page.width * 0.8) if self.page else 280,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=8,
                color=ft.colors.with_opacity(0.2, ft.colors.SHADOW),
                offset=ft.Offset(0, 2),
            ),
            visible=False,
            right=24,
            bottom=24,
        )

    def handle_previous(self, e):
        if self.previous_page_url:
            self.loading_animation.value = "Loading previous page..."
            self.loading_animation.visible = True
            self.loading_animation.update()

            try:
                dodes = Doujindesu(url=None, proxy=self.proxy).get_search_by_url(self.previous_page_url)
                self.results = dodes.results
                self.next_page_url = dodes.next_page_url
                self.previous_page_url = dodes.previous_page_url
                self.update_search_results()
            finally:
                self.loading_animation.visible = False
                self.loading_animation.update()

    def handle_next(self, e):
        if self.next_page_url:
            self.loading_animation.value = "Loading next page..."
            self.loading_animation.visible = True
            self.loading_animation.update()

            try:
                dodes = Doujindesu(url=None, proxy=self.proxy).get_search_by_url(self.next_page_url)
                self.results = dodes.results
                self.next_page_url = dodes.next_page_url
                self.previous_page_url = dodes.previous_page_url
                self.update_search_results()
            finally:
                self.loading_animation.visible = False
                self.loading_animation.update()

    def update_search_results(self):
        if self.results:
            self.search_results.controls = [self.create_result_control(result) for result in self.results]
            self.search_status_text.value = f"Found {len(self.results)} result(s):"
        else:
            self.search_status_text.value = "No results found."
            self.search_results.controls = []

        self.previous_button.visible = bool(self.previous_page_url)
        self.next_button.visible = bool(self.next_page_url)

        self.search_results_view.content = ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            content=ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.ARROW_BACK,
                                        icon_color=ft.colors.PRIMARY,
                                        tooltip="Back to Search",
                                        on_click=self.show_main_view,
                                    ),
                                    ft.Text("Search Results", size=20, weight=ft.FontWeight.BOLD),
                                ],
                                alignment=ft.MainAxisAlignment.START,
                            ),
                            col={"sm": 12},
                            padding=10,
                        ),
                    ]
                ),
                ft.Container(
                    content=ft.Row(
                        [self.previous_button, self.next_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=ft.padding.only(bottom=20),
                ),
                ft.Container(
                    content=self.search_status_text,
                    padding=10,
                ),
                ft.Container(
                    content=self.search_results,
                    expand=True,
                    padding=ft.padding.symmetric(
                        horizontal=max(10, min(20, self.page.width * 0.03)) if self.page else 20,
                    ),
                ),
                ft.Container(
                    content=ft.Row(
                        [self.previous_button, self.next_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=ft.padding.symmetric(vertical=20),
                ),
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        self.main_view.visible = False
        self.details_view.visible = False
        self.search_results_view.visible = True
        self.page.update()

    def handle_option_change(self, index: int):
        """Handle navigation rail option changes."""
        self.selected_nav_index = index

        search_icon = self.nav_rail.content.controls[3]
        download_icon = self.nav_rail.content.controls[4]

        search_icon.icon_color = ft.colors.PINK if self.selected_nav_index == 0 else ft.colors.ON_SURFACE_VARIANT
        download_icon.icon_color = ft.colors.PINK if self.selected_nav_index == 1 else ft.colors.ON_SURFACE_VARIANT
        search_icon.selected = self.selected_nav_index == 0
        download_icon.selected = self.selected_nav_index == 1

        if self.selected_nav_index == 0:
            self.details_view.visible = False
            self.search_results_view.visible = False
            self.main_view.visible = True
            self.search_results.visible = True

            self.search_query.visible = True
            self.url_input.visible = False
            self.search_button.visible = True
            self.download_button.visible = False

            self.search_results.controls = []
            self.results = []
            self.next_page_url = None
            self.previous_page_url = None
            self.selected_result = None

            self.main_status_text.value = ""

        else:
            self.details_view.visible = False
            self.search_results_view.visible = False
            self.main_view.visible = True

            self.search_query.visible = False
            self.url_input.visible = True
            self.search_button.visible = False
            self.download_button.visible = True

        self.main_view.content = self.build_main_view()
        self.page.update()

    def create_result_control(self, result: Result):
        type_color = ft.colors.PINK_700 if result.type.lower() == "doujinshi" else ft.colors.GREEN_700
        title_color = ft.colors.WHITE if self.theme_mode == ft.ThemeMode.DARK else ft.colors.GREY_800

        image_stack = ft.Stack(
            [
                ft.Image(
                    result.thumbnail,
                    width=120,
                    height=180,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(8),
                ),
                ft.Container(
                    width=120,
                    height=180,
                    blur=10 if self.blur_thumbnails else 0,
                    bgcolor=ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK),
                    border_radius=ft.border_radius.all(8),
                    animate=ft.animation.Animation(300, "easeOut"),
                    visible=self.blur_thumbnails,
                ),
            ]
        )

        image_container = ft.Container(
            content=image_stack,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border_radius=ft.border_radius.all(8),
            on_hover=lambda e: self.handle_image_hover(e),
            on_click=lambda e: self.handle_image_click(e),
        )

        def copy_url(e):
            self.page.set_clipboard(result.url)
            self.snackbar.bgcolor = ft.colors.GREEN_700
            self.snackbar.content = ft.Text("URL copied to clipboard!", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)

        card = ft.Container(
            content=ft.Row(
                [
                    image_container,
                    ft.Column(
                        [
                            ft.Text(
                                result.name,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=title_color,
                            ),
                            ft.Text(
                                ", ".join(result.genre),
                                size=14,
                                color=ft.colors.GREY_400,
                            ),
                            ft.Row(
                                [
                                    ft.Container(
                                        content=ft.Text(
                                            result.type,
                                            size=12,
                                            color=ft.colors.WHITE,
                                        ),
                                        bgcolor=type_color,
                                        padding=8,
                                        border_radius=15,
                                    ),
                                    ft.Container(
                                        content=ft.Text(
                                            result.status,
                                            size=12,
                                            color=ft.colors.WHITE,
                                        ),
                                        bgcolor=ft.colors.PINK_700,
                                        padding=8,
                                        border_radius=15,
                                    ),
                                ],
                                spacing=10,
                            ),
                        ],
                        spacing=10,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.icons.LINK,
                        icon_color=ft.colors.PINK_400,
                        tooltip="Copy URL",
                        on_click=copy_url,
                    ),
                ],
                spacing=20,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
            padding=15,
            border_radius=12,
            animate=ft.animation.Animation(300, "easeOut"),
            on_hover=lambda e: self.handle_card_hover(e),
            on_click=lambda e: self.show_details(e, result),
        )
        return card

    def handle_card_hover(self, e):
        e.control.scale = 1.02 if e.data == "true" else 1.0
        e.control.update()

    def show_details(self, e, result: Result):
        self.selected_result = result

        details = Doujindesu(result.url, proxy=self.proxy).get_details()

        if not details:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text("Failed to load details!", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)
            return

        type_color = ft.colors.PINK_700 if details.type.lower() == "doujinshi" else ft.colors.GREEN_700

        download_btn = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.DOWNLOAD_ROUNDED, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                    ft.Text("Download", size=16, weight=ft.FontWeight.W_500, color=ft.colors.ON_SURFACE_VARIANT),
                ],
                tight=True,
                spacing=8,
            ),
            bgcolor=ft.colors.PINK,
            color=ft.colors.ON_PRIMARY,
            on_click=lambda e: self.handle_download_click(e, result),
            style=ft.ButtonStyle(
                shape={
                    ft.ControlState.DEFAULT: ft.RoundedRectangleBorder(radius=12),
                },
                padding=ft.padding.symmetric(horizontal=32, vertical=20),
                animation_duration=200,
                shadow_color=ft.colors.with_opacity(0.2, ft.colors.SHADOW),
                elevation={"pressed": 0, "": 2},
                overlay_color=ft.colors.with_opacity(0.1, ft.colors.ON_PRIMARY),
            ),
        )

        details_image_stack = ft.Stack(
            [
                ft.Image(
                    src=details.thumbnail,
                    width=250,
                    height=350,
                    fit=ft.ImageFit.COVER,
                    border_radius=ft.border_radius.all(12),
                ),
                ft.Container(
                    width=250,
                    height=350,
                    blur=10 if self.blur_thumbnails else 0,
                    bgcolor=ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK),
                    border_radius=ft.border_radius.all(12),
                    animate=ft.animation.Animation(300, "easeOut"),
                    visible=self.blur_thumbnails,
                ),
            ]
        )

        details_image_container = ft.Container(
            content=details_image_stack,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border_radius=ft.border_radius.all(12),
            on_hover=lambda e: self.handle_image_hover(e),
            on_click=lambda e: self.handle_image_click(e),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
            ),
            animate=ft.animation.Animation(300, "easeOut"),
        )

        text_color = ft.colors.GREY_800 if self.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_400

        details_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=ft.colors.PINK_400,
                            tooltip="Back to Results",
                            on_click=self.show_search_results,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            [
                                details_image_container,
                            ],
                            col={"sm": 12, "md": 4},
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            [
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                details.name,
                                                size=24,
                                                weight=ft.FontWeight.BOLD,
                                                color=text_color,
                                            ),
                                            ft.Divider(height=2, color=ft.colors.PINK_400),
                                            ft.Text(
                                                f"Series: {details.series}",
                                                size=16,
                                                color=text_color,
                                            ),
                                            ft.Text(
                                                f"Author: {details.author}",
                                                size=16,
                                                color=text_color,
                                            ),
                                            ft.Text(
                                                f"Chapters: {len(details.chapter_urls)}",
                                                size=16,
                                                color=text_color,
                                            ),
                                            ft.Text(
                                                f"Genre: {', '.join(details.genre)}",
                                                size=16,
                                                color=text_color,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.Text(
                                                            genre,
                                                            size=12,
                                                            color=ft.colors.WHITE,
                                                        ),
                                                        bgcolor=ft.colors.PINK_700,
                                                        padding=ft.padding.all(8),
                                                        border_radius=15,
                                                    )
                                                    for genre in details.genre
                                                ],
                                                wrap=True,
                                                spacing=8,
                                            ),
                                            ft.Row(
                                                [
                                                    ft.Container(
                                                        content=ft.Text(
                                                            details.type,
                                                            size=14,
                                                            color=ft.colors.WHITE,
                                                        ),
                                                        bgcolor=type_color,
                                                        padding=10,
                                                        border_radius=20,
                                                    ),
                                                    ft.Container(
                                                        content=ft.Text(
                                                            details.status,
                                                            size=14,
                                                            color=ft.colors.WHITE,
                                                        ),
                                                        bgcolor=ft.colors.PINK_700,
                                                        padding=10,
                                                        border_radius=20,
                                                    ),
                                                    ft.Container(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(
                                                                    ft.icons.STAR,
                                                                    color=ft.colors.YELLOW_400,
                                                                    size=20,
                                                                ),
                                                                ft.Text(
                                                                    details.score,
                                                                    size=16,
                                                                    color=ft.colors.YELLOW_400,
                                                                    weight=ft.FontWeight.BOLD,
                                                                ),
                                                            ],
                                                            spacing=4,
                                                        ),
                                                        padding=10,
                                                    ),
                                                ],
                                                spacing=10,
                                            ),
                                        ],
                                        spacing=15,
                                    ),
                                    padding=20,
                                    border_radius=12,
                                    gradient=ft.LinearGradient(
                                        begin=ft.alignment.top_center,
                                        end=ft.alignment.bottom_center,
                                        colors=[
                                            ft.colors.with_opacity(0.05, ft.colors.WHITE),
                                            ft.colors.with_opacity(0.02, ft.colors.WHITE),
                                        ],
                                    ),
                                ),
                            ],
                            col={"sm": 12, "md": 8},
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Container(
                    content=ft.Row(
                        [download_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=20,
                ),
            ],
            spacing=30,
            scroll=ft.ScrollMode.AUTO,
        )

        self.details_view.content = details_content

        self.main_view.visible = False
        self.search_results_view.visible = False
        self.details_view.visible = True

        self.page.update()

    def show_search_results(self, e):
        """Show search results view and hide details view."""
        self.details_view.visible = False
        self.search_results_view.visible = True
        self.search_results.visible = True
        self.page.update()

    def convert_images_to_pdf(self, images, title):
        def sanitize_filename(filename):
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, "_")
            filename = filename.strip(". ")
            return filename

        safe_title = sanitize_filename(title)
        if not safe_title.lower().endswith(".pdf"):
            safe_title += ".pdf"

        pdf_path = os.path.join(self.result_folder, safe_title)

        ImageToPDFConverter(images, output_pdf_file=pdf_path).convert_images_to_pdf(images, pdf_path)
        self.main_status_text.value = f"PDF created: {pdf_path}"
        self.page.update()

    def handle_search(self, e):
        query = self.search_query.value
        if not query:
            self.main_status_text.value = "Please enter a manga name to search."
            self.main_status_text.visible = True
            self.page.update()
            return

        self.loading_animation.value = "Searching..."
        self.loading_animation.visible = True
        self.loading_animation.update()

        try:
            search_result = Doujindesu(url=None, proxy=self.proxy).search(query)
            self.results = search_result.results if search_result else []
            self.next_page_url = search_result.next_page_url if search_result else None
            self.previous_page_url = search_result.previous_page_url if search_result else None

            self.main_view.visible = False
            self.details_view.visible = False
            self.search_results_view.visible = True
            self.search_results.visible = True

            self.update_search_results()
        finally:
            self.loading_animation.visible = False
            self.loading_animation.update()

    def handle_download_by_url(self, e):
        url = self.url_input.value
        if not url:
            self.main_status_text.value = "Please enter a manga URL to download."
            self.main_status_text.visible = True
            self.page.update()
            return

        try:
            manga = Doujindesu(url, proxy=self.proxy)
            details = manga.get_details()
            if not details:
                self.snackbar.bgcolor = ft.colors.RED_700
                self.snackbar.content = ft.Text("Failed to get manga details!", color=ft.colors.WHITE)
                self.page.show_snack_bar(self.snackbar)
                return

            chapters = manga.get_all_chapters()
            if not chapters:
                self.snackbar.bgcolor = ft.colors.RED_700
                self.snackbar.content = ft.Text("No chapters found!", color=ft.colors.WHITE)
                self.page.show_snack_bar(self.snackbar)
                return

            if len(chapters) == 1:
                self.download_manga(e, url, all_chapters=True)
                return

            start_chapter = ft.TextField(
                label="Start Chapter",
                hint_text="e.g. 1",
                border=ft.InputBorder.UNDERLINE,
                width=150,
                keyboard_type=ft.KeyboardType.NUMBER,
            )

            end_chapter = ft.TextField(
                label="End Chapter",
                hint_text=f"e.g. {len(chapters)}",
                border=ft.InputBorder.UNDERLINE,
                width=150,
                keyboard_type=ft.KeyboardType.NUMBER,
            )

            chapter_selector = ft.Dropdown(
                label="Select Chapter",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=ft.colors.BLUE_700,
                focused_color=ft.colors.BLUE_700,
                text_size=16,
                content_padding=15,
                options=[ft.dropdown.Option(f"Chapter {i+1}") for i in range(len(chapters))],
                width=200,
            )

            def close_dialog(e):
                dialog.open = False
                self.page.update()

            def handle_download_choice(e, choice: str):
                dialog.open = False
                self.page.update()

                if choice == "single" and chapter_selector.value:
                    chapter_index = int(chapter_selector.value.split()[-1])
                    self.download_manga(e, url, chapter_index=str(chapter_index))
                elif choice == "range":
                    try:
                        start = int(start_chapter.value or "1")
                        end = int(end_chapter.value or str(len(chapters)))
                        if 1 <= start <= end <= len(chapters):
                            self.download_manga(e, url, chapter_range=(start, end))
                        else:
                            self.snackbar.bgcolor = ft.colors.RED_700
                            self.snackbar.content = ft.Text(
                                f"Invalid range! Please enter numbers between 1 and {len(chapters)}",
                                color=ft.colors.WHITE,
                            )
                            self.page.show_snack_bar(self.snackbar)
                    except ValueError:
                        self.snackbar.bgcolor = ft.colors.RED_700
                        self.snackbar.content = ft.Text(
                            "Please enter valid numbers for chapter range!",
                            color=ft.colors.WHITE,
                        )
                        self.page.show_snack_bar(self.snackbar)
                elif choice == "all":
                    self.download_manga(e, url, all_chapters=True)

            dialog_content = [
                ft.Text(f"Found {len(chapters)} chapters", size=16),
                ft.Divider(),
            ]

            if len(chapters) > 1:
                dialog_content.extend(
                    [
                        ft.Text("Download Single Chapter:", size=16),
                        chapter_selector,
                        ft.Divider(),
                        ft.Text("Download Range:", size=16),
                        ft.Row(
                            [start_chapter, ft.Text("to"), end_chapter],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ]
                )

            download_buttons = []
            if len(chapters) > 1:
                download_buttons.extend(
                    [
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.DOWNLOAD, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                                    ft.Text("Download Single", size=16, color=ft.colors.ON_SURFACE_VARIANT),
                                ],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.PINK_700,
                                color=ft.colors.WHITE,
                            ),
                            on_click=lambda e: handle_download_choice(e, "single"),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                                    ft.Text("Download Range", size=16, color=ft.colors.ON_SURFACE_VARIANT),
                                ],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.GREEN_700,
                                color=ft.colors.WHITE,
                            ),
                            on_click=lambda e: handle_download_choice(e, "range"),
                        ),
                    ]
                )

            download_buttons.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=20, color=ft.colors.ON_SURFACE_VARIANT),
                            ft.Text(
                                "Download All" if len(chapters) > 1 else "Download",
                                size=16,
                                color=ft.colors.ON_SURFACE_VARIANT,
                            ),
                        ],
                        spacing=8,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=ft.colors.ORANGE_700,
                        color=ft.colors.WHITE,
                    ),
                    on_click=lambda e: handle_download_choice(e, "all"),
                )
            )

            dialog_content.append(
                ft.Row(
                    download_buttons,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=10,
                    wrap=True,
                )
            )

            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    f"Download {details.name}",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                content=ft.Container(
                    content=ft.Column(
                        dialog_content,
                        spacing=20,
                        scroll=ft.ScrollMode.AUTO,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=min(400, self.page.width * 0.8),
                    height=min(600, self.page.height * 0.8),
                    padding=20,
                ),
                actions=[
                    ft.TextButton("Cancel", on_click=close_dialog),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
                content_padding=10,
                inset_padding=20,
            )

            self.page.overlay.append(dialog)
            dialog.open = True
            self.page.update()

        except Exception as e:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text(f"Error: {e!s}", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)

    def download_manga(
        self,
        e,
        url: str,
        chapter_index: str | None = None,
        chapter_range: tuple[int, int] | None = None,
        all_chapters: bool = False,
    ):
        if self.is_downloading:
            self.snackbar.bgcolor = ft.colors.ORANGE_700
            self.snackbar.content = ft.Text("Download already in progress!", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)
            return

        self.is_downloading = True

        if hasattr(self, "download_button") and self.download_button.visible:
            self.download_button.disabled = True
            self.download_button.update()

        progress_text = self.download_container.content.controls[1]
        progress_bar = self.download_container.content.controls[2]
        image_progress = self.download_container.content.controls[3]

        self.download_container.visible = True
        self.download_container.update()

        def get_title(manga: Doujindesu):
            return "-".join(manga.soup.title.text.split("-")[:-1]).strip()

        try:
            manga = Doujindesu(url, proxy=self.proxy)
            chapters = manga.get_all_chapters()

            self.download_container.visible = True
            self.download_container.update()

            if chapter_index:
                chapter_url = chapters[int(chapter_index) - 1]
                progress_text.value = f"Downloading Chapter {chapter_index}"
                progress_text.update()
                progress_bar.value = 0
                progress_bar.max = 1
                progress_bar.update()

                manga.url = chapter_url
                images = manga.get_all_images()
                if images:
                    image_progress.value = f"Processing {len(images)} images..."
                    image_progress.update()
                    title = get_title(manga)
                    self.convert_images_to_pdf(images, f"{title} - Chapter {chapter_index}")

                progress_bar.value = 1
                progress_bar.update()

            elif chapter_range:
                start, end = chapter_range
                total_chapters = end - start + 1
                progress_bar.value = 0
                progress_bar.max = total_chapters
                progress_bar.update()

                for idx, chapter_num in enumerate(range(start - 1, end), 1):
                    progress_text.value = f"Downloading Chapter {chapter_num + 1}/{end}"
                    progress_text.update()

                    manga.url = chapters[chapter_num]
                    images = manga.get_all_images()
                    if images:
                        image_progress.value = f"Processing {len(images)} images..."
                        image_progress.update()
                        title = get_title(manga)
                        self.convert_images_to_pdf(images, f"{title} - Chapter {chapter_num + 1}")

                        progress_bar.value = idx
                        progress_bar.update()

            elif all_chapters:
                total_chapters = len(chapters)
                progress_bar.value = 0
                progress_bar.max = total_chapters
                progress_bar.update()

                for idx, chapter_url in enumerate(chapters, 1):
                    progress_text.value = f"Downloading Chapter {idx}/{total_chapters}"
                    progress_text.update()

                    manga.url = chapter_url
                    images = manga.get_all_images()
                    if images:
                        image_progress.value = f"Processing {len(images)} images..."
                        image_progress.update()
                        title = "-".join(manga.soup.title.text.split("-")[:-1]).strip()
                        filename = f"{title} - Chapter {idx}" if len(chapters) > 1 else title
                        self.convert_images_to_pdf(images, filename)

                        progress_bar.value = idx
                        progress_bar.update()

            self.snackbar.bgcolor = ft.colors.GREEN_700
            self.snackbar.content = ft.Text(
                "Download completed, downloaded file(s) saved in result directory!", color=ft.colors.WHITE
            )
            self.page.show_snack_bar(self.snackbar)

        except Exception as e:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text(f"Error: {e!s}", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)

        finally:
            self.is_downloading = False

            if hasattr(self, "download_button") and self.download_button.visible:
                self.download_button.disabled = False
                self.download_button.update()

            if self.search_results.controls:
                for result in self.search_results.controls:
                    download_icon = result.content.controls[-1]
                    download_icon.disabled = False
                    download_icon.update()

            if self.details_view.visible and self.details_view.content:
                download_container = self.details_view.content.controls[-1]
                download_row = download_container.content
                download_btn = download_row.controls[0]
                download_btn.disabled = False
                download_btn.update()

            self.download_container.visible = False
            self.download_container.update()

    def build_main_view(self):
        form_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Search Manga" if self.selected_nav_index == 0 else "Download Manga",
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.colors.ON_SURFACE,
                                    ),
                                    ft.Text(
                                        "Find your favorite manga"
                                        if self.selected_nav_index == 0
                                        else "Download manga using URL",
                                        size=16,
                                        color=ft.colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                                spacing=4,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            padding=ft.padding.only(bottom=20),
                        ),
                        ft.Container(
                            content=ft.Column(
                                [
                                    ft.ResponsiveRow(
                                        [
                                            ft.Container(
                                                content=ft.Column(
                                                    [
                                                        self.search_query
                                                        if self.selected_nav_index == 0
                                                        else self.url_input
                                                    ],
                                                    spacing=10,
                                                ),
                                                col={"sm": 12, "md": 12, "lg": 12},
                                                padding=10,
                                            ),
                                        ],
                                    ),
                                    ft.ResponsiveRow(
                                        [
                                            ft.Container(
                                                content=ft.Column(
                                                    [
                                                        self.search_button
                                                        if self.selected_nav_index == 0
                                                        else self.download_button
                                                    ],
                                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                ),
                                                col={"sm": 12, "md": 12, "lg": 12},
                                                padding=10,
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        content=self.main_status_text,
                                        padding=10,
                                        alignment=ft.alignment.center,
                                    ),
                                ],
                                spacing=10,
                            ),
                            padding=ft.padding.symmetric(horizontal=20),
                        ),
                    ],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=40,
                border_radius=12,
            ),
            elevation=0,
            color=ft.colors.SURFACE_VARIANT,
        )

        return ft.Column(
            [
                ft.Container(
                    content=self.logo,
                    alignment=ft.alignment.center,
                    animate=ft.animation.Animation(300, "easeOut"),
                    padding=ft.padding.symmetric(vertical=40),
                    height=min(300, self.page.height * 0.3) if self.page else 300,
                ),
                ft.Container(
                    content=form_card,
                    padding=ft.padding.symmetric(horizontal=20),
                    width=min(600, self.page.width * 0.9) if self.page else 600,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

    def show_main_view(self, e=None):
        self.main_view.visible = True
        self.search_results_view.visible = False
        self.details_view.visible = False
        self.page.update()

    def show_search_results_view(self):
        self.main_view.visible = False
        self.search_results_view.visible = True
        self.details_view.visible = False
        self.page.update()

    def show_details_view(self):
        self.main_view.visible = False
        self.search_results_view.visible = False
        self.details_view.visible = True
        self.page.update()

    def build(self):
        pass

    def set_page(self, page):
        self.page = page

        self.page.theme = ft.Theme(
            color_scheme_seed=ft.colors.PINK,
            use_material3=True,
        )
        self.page.theme_mode = "dark"
        self.theme_mode = ft.ThemeMode.DARK

        def on_resized(e):
            self.main_view.content = self.build_main_view()
            self.page.update()

        self.page.on_resized = on_resized

        self.main_view = ft.Container(
            content=self.build_main_view(),
            visible=True,
            expand=True,
        )

        self.search_results_view = ft.Container(
            content=ft.Column(
                [
                    ft.ResponsiveRow(
                        [
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.ARROW_BACK,
                                            icon_color=ft.colors.PRIMARY,
                                            tooltip="Back to Search",
                                            on_click=self.show_main_view,
                                        ),
                                        ft.Text("Search Results", size=20, weight=ft.FontWeight.BOLD),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                                col={"sm": 12},
                                padding=10,
                            ),
                        ]
                    ),
                    ft.Container(
                        content=ft.Row(
                            [self.previous_button, self.next_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=ft.padding.only(bottom=20),
                    ),
                    ft.Container(
                        content=self.search_status_text,
                        padding=10,
                    ),
                    ft.Container(
                        content=self.search_results,
                        expand=True,
                        padding=ft.padding.symmetric(
                            horizontal=max(10, min(20, self.page.width * 0.03)) if self.page else 20,
                        ),
                    ),
                    ft.Container(
                        content=ft.Row(
                            [self.previous_button, self.next_button],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                        padding=ft.padding.symmetric(vertical=20),
                    ),
                ],
                spacing=20,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            visible=False,
            expand=True,
        )

        self.details_view = ft.Container(
            content=None,
            padding=40,
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=28,
            visible=False,
            expand=True,
        )

        self.page.add(
            ft.Row(
                [
                    self.nav_rail,
                    ft.Container(
                        content=ft.Stack(
                            [
                                self.main_view,
                                self.search_results_view,
                                self.details_view,
                                self.loading_animation,
                                self.download_container,
                            ],
                        ),
                        expand=True,
                        padding=ft.padding.symmetric(
                            horizontal=max(10, min(20, self.page.width * 0.02)) if self.page else 20,
                        ),
                    ),
                ],
                expand=True,
            )
        )

        self.page.update()

    def toggle_theme(self, e):
        self.is_dark = not self.is_dark
        e.control.selected = self.is_dark
        self.theme_mode = ft.ThemeMode.DARK if self.is_dark else ft.ThemeMode.LIGHT
        self.page.theme_mode = "dark" if self.is_dark else "light"
        self.page.update()

    def display_search_results(self, results: list[Result]):
        text_color = ft.colors.GREY_800 if self.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_400

        results_list = []
        for result in results:
            results_list.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Image(
                                            src=result.thumbnail,
                                            width=100,
                                            height=150,
                                            fit=ft.ImageFit.COVER,
                                            border_radius=10,
                                        ),
                                        ft.Column(
                                            [
                                                ft.Text(
                                                    result.name,
                                                    size=16,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=text_color,
                                                ),
                                                ft.Text(
                                                    f"Type: {result.type}",
                                                    size=14,
                                                    color=text_color,
                                                ),
                                                ft.Text(
                                                    f"Score: {result.score}",
                                                    size=14,
                                                    color=text_color,
                                                ),
                                                ft.Text(
                                                    f"Status: {result.status}",
                                                    size=14,
                                                    color=text_color,
                                                ),
                                            ],
                                            spacing=5,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.START,
                                    spacing=20,
                                ),
                            ]
                        ),
                        padding=20,
                    )
                )
            )

    def handle_image_hover(self, e):
        """Handle hover effect for manga thumbnails."""
        overlay = e.control.content.controls[1]
        if e.data == "true":
            overlay.blur = 0
            overlay.bgcolor = ft.colors.with_opacity(0, ft.colors.BLACK)
            overlay.visible = False
        else:
            overlay.blur = 10 if self.blur_thumbnails else 0
            overlay.bgcolor = ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK)
            overlay.visible = self.blur_thumbnails
        overlay.update()

    def handle_image_click(self, e):
        """Handle click effect for manga thumbnails."""
        overlay = e.control.content.controls[1]
        overlay.blur = 0
        overlay.bgcolor = ft.colors.with_opacity(0, ft.colors.BLACK)
        overlay.update()

    def toggle_blur(self, e):
        """Toggle blur effect on thumbnails."""
        self.blur_thumbnails = not self.blur_thumbnails
        e.control.selected = self.blur_thumbnails

        if self.search_results.controls:
            for result in self.search_results.controls:
                try:
                    overlay = result.content.controls[0].content.controls[1]
                    overlay.visible = self.blur_thumbnails
                    overlay.blur = 10 if self.blur_thumbnails else 0
                    overlay.bgcolor = ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK)
                    overlay.update()
                except (AttributeError, IndexError):
                    continue

        if self.details_view.visible and self.details_view.content:
            try:
                details_content = self.details_view.content
                responsive_row = details_content.controls[1]
                image_column = responsive_row.controls[0]
                image_container = image_column.controls[0]
                image_stack = image_container.content
                overlay = image_stack.controls[1]

                overlay.visible = self.blur_thumbnails
                overlay.blur = 10 if self.blur_thumbnails else 0
                overlay.bgcolor = ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK)
                overlay.update()
            except (AttributeError, IndexError):
                pass

        self.page.update()

    def handle_download_click(self, e, result):
        """Handle download button click from details view."""
        manga = Doujindesu(result.url, proxy=self.proxy)
        chapters = manga.get_all_chapters()

        if not chapters:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text("No chapters found!", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)
            return

        if len(chapters) == 1:
            self.download_manga(e, result.url, all_chapters=True)
            return

        input_style = {
            "border_radius": 8,
            "border_color": ft.colors.OUTLINE,
            "cursor_color": ft.colors.PINK,
            "text_size": 16,
            "content_padding": ft.padding.symmetric(horizontal=16, vertical=12),
            "filled": True,
            "bgcolor": ft.colors.SURFACE,
        }

        start_chapter = ft.TextField(
            label="Start Chapter",
            hint_text="e.g. 1",
            border=ft.InputBorder.OUTLINE,
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            **input_style,
        )

        end_chapter = ft.TextField(
            label="End Chapter",
            hint_text=f"e.g. {len(chapters)}",
            border=ft.InputBorder.OUTLINE,
            width=150,
            keyboard_type=ft.KeyboardType.NUMBER,
            **input_style,
        )

        chapter_selector = ft.Dropdown(
            label="Select Chapter",
            hint_text="Choose a chapter",
            border=ft.InputBorder.OUTLINE,
            focused_border_color=ft.colors.PINK,
            focused_color=ft.colors.PINK,
            text_size=16,
            content_padding=16,
            options=[ft.dropdown.Option(f"Chapter {i+1}") for i in range(len(chapters))],
            width=300,
        )

        def close_dialog(e):
            dialog.open = False
            self.page.update()

        def handle_download_choice(e, choice: str):
            dialog.open = False
            self.page.update()

            if choice == "single" and chapter_selector.value:
                chapter_index = int(chapter_selector.value.split()[-1])
                self.download_manga(e, result.url, chapter_index=str(chapter_index))
            elif choice == "range":
                try:
                    start = int(start_chapter.value or "1")
                    end = int(end_chapter.value or str(len(chapters)))
                    if 1 <= start <= end <= len(chapters):
                        self.download_manga(e, result.url, chapter_range=(start, end))
                    else:
                        self.snackbar.bgcolor = ft.colors.RED_700
                        self.snackbar.content = ft.Text(
                            f"Invalid range! Please enter numbers between 1 and {len(chapters)}",
                            color=ft.colors.WHITE,
                        )
                        self.page.show_snack_bar(self.snackbar)
                except ValueError:
                    self.snackbar.bgcolor = ft.colors.RED_700
                    self.snackbar.content = ft.Text(
                        "Please enter valid numbers for chapter range!",
                        color=ft.colors.WHITE,
                    )
                    self.page.show_snack_bar(self.snackbar)
            elif choice == "all":
                self.download_manga(e, result.url, all_chapters=True)

        dialog_content = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.icons.MENU_BOOK_ROUNDED,
                                            color=ft.colors.PINK,
                                            size=24,
                                        ),
                                        ft.Text(
                                            result.name,
                                            size=16,
                                            weight=ft.FontWeight.W_500,
                                            color=ft.colors.ON_SURFACE,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=8,
                                ),
                                ft.Text(
                                    f"{len(chapters)} chapters available",
                                    size=14,
                                    color=ft.colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                        ),
                        padding=ft.padding.only(bottom=16),
                    ),
                    ft.Divider(height=1, color=ft.colors.OUTLINE),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Download Single Chapter",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                chapter_selector,
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.icons.DOWNLOAD_ROUNDED, size=20, color=ft.colors.ON_SURFACE_VARIANT
                                            ),
                                            ft.Text("Download Single", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                                        ],
                                        tight=True,
                                        spacing=8,
                                    ),
                                    style=ft.ButtonStyle(
                                        color=ft.colors.ON_PRIMARY,
                                        bgcolor=ft.colors.PINK,
                                    ),
                                    on_click=lambda e: handle_download_choice(e, "single"),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        padding=ft.padding.symmetric(vertical=16),
                    ),
                    ft.Divider(height=1, color=ft.colors.OUTLINE),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "Download Range",
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                ft.Row(
                                    [start_chapter, ft.Text("to"), end_chapter],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=16,
                                ),
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        [
                                            ft.Icon(
                                                ft.icons.DOWNLOAD_FOR_OFFLINE_ROUNDED,
                                                size=20,
                                                color=ft.colors.ON_SURFACE_VARIANT,
                                            ),
                                            ft.Text("Download Range", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                                        ],
                                        tight=True,
                                        spacing=8,
                                    ),
                                    style=ft.ButtonStyle(
                                        color=ft.colors.ON_PRIMARY,
                                        bgcolor=ft.colors.PINK,
                                    ),
                                    on_click=lambda e: handle_download_choice(e, "range"),
                                ),
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                        ),
                        padding=ft.padding.symmetric(vertical=16),
                    ),
                    ft.Divider(height=1, color=ft.colors.OUTLINE),
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.icons.CLOUD_DOWNLOAD_ROUNDED, size=20, color=ft.colors.ON_SURFACE_VARIANT
                                    ),
                                    ft.Text("Download All", size=14, color=ft.colors.ON_SURFACE_VARIANT),
                                ],
                                tight=True,
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                color=ft.colors.ON_PRIMARY,
                                bgcolor=ft.colors.PINK,
                            ),
                            on_click=lambda e: handle_download_choice(e, "all"),
                        ),
                        padding=ft.padding.only(top=16),
                        alignment=ft.alignment.center,
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            padding=24,
            width=min(400, self.page.width * 0.9) if self.page else 400,
        )

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                f"Download {result.name}",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.ON_SURFACE,
                text_align=ft.TextAlign.CENTER,
            ),
            content=dialog_content,
            actions=[
                ft.TextButton(
                    text="Cancel",
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=ft.colors.PINK,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=12),
        )

        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
