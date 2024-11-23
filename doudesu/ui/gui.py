"""
GUI interface for the Doujindesu manga downloader.
This module requires the 'gui' extra dependencies.
"""

import os
import sys
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
            page.add(app.build())

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

        # Create result folder if it doesn't exist
        os.makedirs(self.result_folder, exist_ok=True)

        self.logo = ft.Image(
            src="/images/logo.png" if self.is_dark else "/images/logo_light.png",
            width=250,
            height=250,
            fit=ft.ImageFit.CONTAIN,
            border_radius=ft.border_radius.all(12),
        )

        input_border = ft.InputBorder.UNDERLINE
        input_style = {
            "width": 300,
            "border_radius": 8,
            "border_color": ft.colors.BLUE_400,
            "focused_border_color": ft.colors.BLUE_700,
            "cursor_color": ft.colors.BLUE_700,
            "text_size": 16,
            "content_padding": 20,
        }

        self.search_query = ft.TextField(
            label="Search manga",
            hint_text="Enter manga name...",
            prefix_icon=ft.icons.SEARCH,
            border=input_border,
            visible=True,
            on_submit=self.handle_search,
            **input_style,
        )

        self.url_input = ft.TextField(
            label="Manga URL",
            hint_text="Enter manga URL here...",
            prefix_icon=ft.icons.LINK,
            border=input_border,
            visible=False,
            on_submit=self.handle_download_by_url,
            **input_style,
        )

        button_style = {
            "style": ft.ButtonStyle(
                bgcolor={
                    ft.MaterialState.DEFAULT: ft.colors.BLUE_700,
                    ft.MaterialState.HOVERED: ft.colors.BLUE_800,
                },
                shape={
                    ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=50),
                },
                padding=ft.padding.all(20),
                animation_duration=200,
                shadow_color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                elevation={"pressed": 0, "": 4},
            ),
            "color": ft.colors.WHITE,
        }

        self.search_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.icons.SEARCH, size=20),
                    ft.Text("Search", size=16, weight=ft.FontWeight.W_500),
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
                    ft.Icon(ft.icons.DOWNLOAD, size=20),
                    ft.Text("Download", size=16, weight=ft.FontWeight.W_500),
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
                    ft.Icon(ft.icons.ARROW_BACK, size=20),
                    ft.Text("Previous", size=16, weight=ft.FontWeight.W_500),
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
                    ft.Icon(ft.icons.ARROW_FORWARD, size=20),
                    ft.Text("Next", size=16, weight=ft.FontWeight.W_500),
                ],
                tight=True,
                spacing=8,
            ),
            on_click=self.handle_next,
            visible=False,
            **button_style,
        )

        self.nav_rail = ft.NavigationRail(
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.SEARCH,
                    selected_icon=ft.icons.SEARCH,
                    label="Search",
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.LINK,
                    selected_icon=ft.icons.LINK,
                    label="Download",
                ),
            ],
            selected_index=0,
            on_change=self.handle_option_change,
            min_width=80,
            min_extended_width=180,
            leading=ft.Column(
                [
                    ft.IconButton(
                        icon=ft.icons.DARK_MODE,
                        selected_icon=ft.icons.LIGHT_MODE,
                        icon_color=ft.colors.BLUE_400,
                        selected=self.is_dark,
                        on_click=self.toggle_theme,
                        tooltip="Toggle theme",
                        style=ft.ButtonStyle(
                            shape={
                                ft.MaterialState.DEFAULT: ft.CircleBorder(),
                            },
                        ),
                    ),
                    ft.IconButton(
                        icon=ft.icons.BLUR_ON,
                        selected_icon=ft.icons.BLUR_OFF,
                        icon_color=ft.colors.BLUE_400,
                        selected=self.blur_thumbnails,
                        on_click=self.toggle_blur,
                        tooltip="Toggle blur",
                        style=ft.ButtonStyle(
                            shape={
                                ft.MaterialState.DEFAULT: ft.CircleBorder(),
                            },
                        ),
                    ),
                ],
                spacing=0,
            ),
            bgcolor=ft.colors.SURFACE_VARIANT,
        )

        self.status_text = ft.Text(size=16, color=ft.colors.BLUE)

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

        self.main_view = ft.Container(content=self.build_main_view(), visible=True, expand=True)

        self.search_results_view = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.icons.ARROW_BACK,
                                icon_color=ft.colors.BLUE_400,
                                tooltip="Back to Search",
                                on_click=self.show_main_view,
                            ),
                            ft.Text("Search Results", size=20, weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row(
                        [
                            self.previous_button,
                            self.next_button,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    self.status_text,
                    self.search_results,
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "Previous",
                                icon=ft.icons.ARROW_BACK,
                                on_click=self.handle_previous,
                                visible=False,
                                **button_style,
                            ),
                            ft.ElevatedButton(
                                "Next",
                                icon=ft.icons.ARROW_FORWARD,
                                on_click=self.handle_next,
                                visible=False,
                                **button_style,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
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
            border_radius=12,
            visible=False,
            expand=True,
        )

        self.snackbar = ft.SnackBar(
            content=ft.Text(""),
            bgcolor=ft.colors.BLUE_700,
            action="OK",
        )

        self.url_download_view = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=self.logo,
                        alignment=ft.alignment.center,
                        animate=ft.animation.Animation(300, "easeOut"),
                        padding=20,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.ResponsiveRow(
                                    [
                                        ft.Column(
                                            [self.url_input],
                                            col={"sm": 12, "md": 8, "lg": 6},
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                ft.ResponsiveRow(
                                    [
                                        ft.Column(
                                            [self.download_button],
                                            col={"sm": 12, "md": 8, "lg": 6},
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=ft.padding.all(30),
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
                    self.status_text,
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=30,
            ),
            visible=False,
            expand=True,
            padding=40,
        )

        self.download_container = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.icons.DOWNLOAD, color=ft.colors.WHITE),
                            ft.Text(
                                "Downloading...",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
                            ),
                        ],
                        spacing=10,
                    ),
                    ft.Text(
                        "",  # Progress text
                        size=12,
                        color=ft.colors.WHITE,
                    ),
                    ft.ProgressBar(
                        width=200,
                        height=4,
                    ),
                    ft.Text(
                        "",  # Image progress
                        size=12,
                        color=ft.colors.GREY_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            bgcolor=ft.colors.with_opacity(0.9, ft.colors.BLACK),
            padding=15,
            border_radius=8,
            width=250,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.colors.with_opacity(0.3, ft.colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            visible=False,
            right=20,
            bottom=20,
            left=None,
            top=None,
        )

    def handle_previous(self, e):
        if self.previous_page_url:
            self.loading_animation.content.controls[1].value = "Loading previous page..."
            self.loading_animation.visible = True
            self.loading_animation.update()

            try:
                dodes = Doujindesu.get_search_by_url(self.previous_page_url)
                self.results = dodes.results
                self.next_page_url = dodes.next_page_url
                self.previous_page_url = dodes.previous_page_url
                self.update_search_results()
            finally:
                self.loading_animation.visible = False
                self.loading_animation.update()

    def handle_next(self, e):
        if self.next_page_url:
            self.loading_animation.content.controls[1].value = "Loading next page..."
            self.loading_animation.visible = True
            self.loading_animation.update()

            try:
                dodes = Doujindesu.get_search_by_url(self.next_page_url)
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
            self.status_text.value = f"Found {len(self.results)} result(s):"
        else:
            self.status_text.value = "No results found."

        # Get bottom navigation buttons
        bottom_nav = self.search_results_view.content.controls[-1].controls
        bottom_prev = bottom_nav[0]
        bottom_next = bottom_nav[1]

        # Update visibility for both top and bottom navigation buttons
        self.previous_button.visible = self.previous_page_url is not None
        self.next_button.visible = self.next_page_url is not None
        bottom_prev.visible = self.previous_page_url is not None
        bottom_next.visible = self.next_page_url is not None

        # Update all controls
        self.search_results.update()
        self.status_text.update()
        self.previous_button.update()
        self.next_button.update()
        bottom_prev.update()
        bottom_next.update()

    def handle_option_change(self, e):
        if self.nav_rail.selected_index == 0:  # Search by Keyword
            # Reset all views first
            self.details_view.visible = False
            self.search_results_view.visible = False
            self.url_download_view.visible = False
            self.main_view.visible = True

            # Reset search-related elements
            self.search_query.visible = True
            self.url_input.visible = False
            self.search_button.visible = True
            self.download_button.visible = False

            # Clear previous search results if any
            self.search_results.controls = []
            self.results = []
            self.next_page_url = None
            self.previous_page_url = None
            self.selected_result = None

        else:  # Download by URL
            # Reset all views first
            self.details_view.visible = False
            self.search_results_view.visible = False
            self.main_view.visible = False
            self.url_download_view.visible = True

            # Reset URL-related elements
            self.search_query.visible = False
            self.url_input.visible = True
            self.search_button.visible = False
            self.download_button.visible = True

        self.page.update()

    def create_result_control(self, result: Result):
        type_color = ft.colors.BLUE_700 if result.type.lower() == "doujinshi" else ft.colors.GREEN_700
        title_color = ft.colors.WHITE if self.theme_mode == ft.ThemeMode.DARK else ft.colors.GREY_800

        # Create a stack with blurred overlay
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
                                        bgcolor=ft.colors.BLUE_700,
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
                        icon_color=ft.colors.BLUE_400,
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

        details = Doujindesu(result.url).get_details()

        if not details:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text("Failed to load details!", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)
            return

        # Get color based on type
        type_color = ft.colors.BLUE_700 if details.type.lower() == "doujinshi" else ft.colors.GREEN_700

        # Create image stack with blur effect for details thumbnail
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

        # Create chapter dropdown if multiple chapters exist
        chapter_selector = None
        if len(details.chapter_urls) > 1:
            chapter_selector = ft.Dropdown(
                label="Select Chapter",
                border=ft.InputBorder.UNDERLINE,
                focused_border_color=ft.colors.BLUE_700,
                focused_color=ft.colors.BLUE_700,
                text_size=16,
                content_padding=15,
                options=[ft.dropdown.Option(f"Chapter {i+1}") for i in range(len(details.chapter_urls))],
                width=200,
            )

        # Get text color based on theme
        text_color = ft.colors.GREY_800 if self.theme_mode == ft.ThemeMode.LIGHT else ft.colors.GREY_400

        def handle_download_click(e):
            if len(details.chapter_urls) == 1:
                self.download_manga(e, result.url, all_chapters=True)
                return

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
                        end = int(end_chapter.value or str(len(details.chapter_urls)))
                        if 1 <= start <= end <= len(details.chapter_urls):
                            self.download_manga(e, result.url, chapter_range=(start, end))
                        else:
                            self.snackbar.bgcolor = ft.colors.RED_700
                            self.snackbar.content = ft.Text(
                                f"Invalid range! Please enter numbers between 1 and {len(details.chapter_urls)}",
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

            # Create range download dialog
            start_chapter = ft.TextField(
                label="Start Chapter",
                hint_text="e.g. 1",
                border=ft.InputBorder.UNDERLINE,
                width=150,
                keyboard_type=ft.KeyboardType.NUMBER,
            )

            end_chapter = ft.TextField(
                label="End Chapter",
                hint_text=f"e.g. {len(details.chapter_urls)}",
                border=ft.InputBorder.UNDERLINE,
                width=150,
                keyboard_type=ft.KeyboardType.NUMBER,
            )

            # Create dialog content based on chapter count
            dialog_content = [
                ft.Text(f"Found {len(details.chapter_urls)} chapters", size=16),
                ft.Divider(),
            ]

            if len(details.chapter_urls) > 1:
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

            # Create buttons based on chapter count
            download_buttons = []
            if len(details.chapter_urls) > 1:
                download_buttons.extend(
                    [
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.DOWNLOAD, size=20),
                                    ft.Text("Download Single", size=16),
                                ],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_700,
                                color=ft.colors.WHITE,
                            ),
                            on_click=lambda e: handle_download_choice(e, "single"),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=20),
                                    ft.Text("Download Range", size=16),
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
                            ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=20),
                            ft.Text(
                                "Download All" if len(details.chapter_urls) > 1 else "Download",
                                size=16,
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

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        # Single download button at the bottom
        ft.Container(
            content=ft.Row(
                [
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.icons.DOWNLOAD, size=20),
                                ft.Text("Download", size=16, weight=ft.FontWeight.W_500),
                            ],
                            spacing=8,
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE_700,
                            color=ft.colors.WHITE,
                        ),
                        on_click=handle_download_click,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
        )

        details_content = ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_color=ft.colors.BLUE_400,
                            tooltip="Back to Results",
                            on_click=self.show_search_results,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
                ft.ResponsiveRow(
                    [
                        # Left column - Image
                        ft.Column(
                            [
                                details_image_container,
                            ],
                            col={"sm": 12, "md": 4},
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        # Right column - Details
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
                                            ft.Divider(height=2, color=ft.colors.BLUE_400),
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
                                                        bgcolor=ft.colors.BLUE_700,
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
                                                        bgcolor=ft.colors.BLUE_700,
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
                                    padding=30,
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
                # Single download button at the bottom
                ft.Container(
                    content=ft.Row(
                        [
                            ft.ElevatedButton(
                                content=ft.Row(
                                    [
                                        ft.Icon(ft.icons.DOWNLOAD, size=20),
                                        ft.Text(
                                            "Download",
                                            size=16,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                    ],
                                    spacing=8,
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE_700,
                                    color=ft.colors.WHITE,
                                ),
                                on_click=handle_download_click,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=20,
                ),
            ],
            spacing=30,
            scroll=ft.ScrollMode.AUTO,
        )

        self.details_view.content = details_content
        self.search_results.visible = False
        self.details_view.visible = True
        self.details_view.update()
        self.search_results.update()

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
        self.status_text.value = f"PDF created: {pdf_path}"
        self.status_text.update()

    def handle_search(self, e):
        query = self.search_query.value
        if not query:
            self.status_text.value = "Please enter a manga name to search."
            self.status_text.update()
            return

        self.loading_animation.content.controls[1].value = "Searching..."
        self.loading_animation.visible = True
        self.loading_animation.update()

        try:
            search_result = Doujindesu.search(query)
            self.results = search_result.results if search_result else []
            self.next_page_url = search_result.next_page_url if search_result else None
            self.previous_page_url = search_result.previous_page_url if search_result else None
            self.update_search_results()
            self.show_search_results_view()
        finally:
            self.loading_animation.visible = False
            self.loading_animation.update()

    def handle_download_by_url(self, e):
        url = self.url_input.value
        if not url:
            self.status_text.value = "Please enter a manga URL to download."
            self.status_text.update()
            return

        try:
            manga = Doujindesu(url)
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

            # Create dialog content based on chapter count
            dialog_content = [
                ft.Text(f"Found {len(chapters)} chapters", size=16),
                ft.Divider(),
            ]

            # Only show chapter selector and range options if multiple chapters exist
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

            # Create buttons based on chapter count
            download_buttons = []
            if len(chapters) > 1:
                download_buttons.extend(
                    [
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.DOWNLOAD, size=20),
                                    ft.Text("Download Single", size=16),
                                ],
                                spacing=8,
                            ),
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE_700,
                                color=ft.colors.WHITE,
                            ),
                            on_click=lambda e: handle_download_choice(e, "single"),
                        ),
                        ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=20),
                                    ft.Text("Download Range", size=16),
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

            # Always add Download All button
            download_buttons.append(
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.DOWNLOAD_FOR_OFFLINE, size=20),
                            ft.Text(
                                "Download All" if len(chapters) > 1 else "Download",
                                size=16,
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

            self.page.dialog = dialog
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
        self.download_button.disabled = True
        self.download_button.update()

        # Get correct control indices based on our container structure
        progress_text = self.download_container.content.controls[1]  # Changed from 2
        progress_bar = self.download_container.content.controls[2]  # Changed from 3
        image_progress = self.download_container.content.controls[3]  # Changed from 4

        self.download_container.visible = True
        self.download_container.update()

        try:
            manga = Doujindesu(url)
            chapters = manga.get_all_chapters()

            self.download_container.visible = True
            self.download_container.update()

            if chapter_index:
                # Download specific chapter
                chapter_url = chapters[int(chapter_index) - 1]
                progress_text.value = f"Downloading Chapter {chapter_index}"
                progress_text.update()
                progress_bar.value = 0
                progress_bar.max = 1
                progress_bar.update()

                manga.url = chapter_url
                images = manga.get_all_images()
                if images:
                    image_progress.value = f"Processing {len(images)} images"
                    image_progress.update()
                    title = "-".join(manga.soup.title.text.split("-")[:-1]).strip()
                    self.convert_images_to_pdf(images, f"{title}.pdf")

                progress_bar.value = 1
                progress_bar.update()

            elif chapter_range:
                # Download range of chapters
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
                        image_progress.value = f"Processing {len(images)} images"
                        image_progress.update()
                        title = "-".join(manga.soup.title.text.split("-")[:-1]).strip()
                        self.convert_images_to_pdf(images, f"{title}.pdf")

                        progress_bar.value = idx
                        progress_bar.update()

            elif all_chapters:
                # Download all chapters
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
                        image_progress.value = f"Processing {len(images)} images"
                        image_progress.update()
                        title = "-".join(manga.soup.title.text.split("-")[:-1]).strip()
                        self.convert_images_to_pdf(images, f"{title}.pdf")

                        progress_bar.value = idx
                        progress_bar.update()

            self.snackbar.bgcolor = ft.colors.GREEN_700
            self.snackbar.content = ft.Text("Download completed!", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)

        except Exception as e:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text(f"Error: {e!s}", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)

        finally:
            self.is_downloading = False
            self.download_button.disabled = False
            self.download_button.update()

            # Update search results download icons
            if self.search_results.controls:
                for result in self.search_results.controls:
                    download_icon = result.content.controls[-1]
                    download_icon.disabled = False
                    download_icon.update()

            # Update details view download button
            if self.details_view.visible and self.details_view.content:
                # Get the download button from the last container in details_content
                download_container = self.details_view.content.controls[-1]  # Container
                download_row = download_container.content  # Row
                download_btn = download_row.controls[0]  # Button
                download_btn.disabled = False
                download_btn.update()

            self.download_container.visible = False
            self.download_container.update()

    def build_main_view(self):
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=self.logo,
                        alignment=ft.alignment.center,
                        animate=ft.animation.Animation(300, "easeOut"),
                        padding=20,
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.ResponsiveRow(
                                    [
                                        ft.Column(
                                            [self.search_query, self.url_input],
                                            col={"sm": 12, "md": 8, "lg": 6},
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                ft.ResponsiveRow(
                                    [
                                        ft.Column(
                                            [self.search_button, self.download_button],
                                            col={"sm": 12, "md": 8, "lg": 6},
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        ),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=ft.padding.all(30),
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
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=30,
            ),
            expand=True,
            padding=40,
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
        return ft.ResponsiveRow(
            [
                ft.Container(
                    content=self.nav_rail,
                    col={"sm": 2, "md": 1},
                    border=ft.border.only(right=ft.BorderSide(1, ft.colors.OUTLINE)),
                ),
                ft.Container(
                    content=ft.Stack(
                        [
                            self.main_view,
                            self.url_download_view,
                            self.search_results_view,
                            self.details_view,
                            self.loading_animation,
                            self.download_container,
                        ],
                    ),
                    col={"sm": 10, "md": 11},
                    expand=True,
                ),
            ],
            expand=True,
        )

    def set_page(self, page):
        self.page = page
        self.page.window_maximized = True
        self.page.theme_mode = "dark"
        self.theme_mode = ft.ThemeMode.DARK

        self.main_view.visible = True
        self.url_download_view.visible = False
        self.search_results_view.visible = False
        self.details_view.visible = False

        self.page.update()

    def toggle_theme(self, e):
        self.is_dark = not self.is_dark
        e.control.selected = self.is_dark
        self.theme_mode = ft.ThemeMode.DARK if self.is_dark else ft.ThemeMode.LIGHT
        self.page.theme_mode = "dark" if self.is_dark else "light"
        self.page.update()

    def display_search_results(self, results: list[Result]):
        # Get text color based on theme
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
        overlay = e.control.content.controls[1]  # Get the overlay container
        if e.data == "true":  # Mouse entered
            overlay.blur = 0
            overlay.bgcolor = ft.colors.with_opacity(0, ft.colors.BLACK)
            overlay.visible = False
        else:  # Mouse exited
            overlay.blur = 10 if self.blur_thumbnails else 0
            overlay.bgcolor = ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK)
            overlay.visible = self.blur_thumbnails
        overlay.update()

    def handle_image_click(self, e):
        """Handle click effect for manga thumbnails."""
        overlay = e.control.content.controls[1]  # Get the overlay container
        overlay.blur = 0
        overlay.bgcolor = ft.colors.with_opacity(0, ft.colors.BLACK)
        overlay.update()

    def toggle_blur(self, e):
        """Toggle blur effect on thumbnails."""
        self.blur_thumbnails = not self.blur_thumbnails
        e.control.selected = self.blur_thumbnails

        # Update all thumbnails in search results
        if self.search_results.controls:
            for result in self.search_results.controls:
                try:
                    overlay = result.content.controls[0].content.controls[1]  # Get overlay container
                    overlay.visible = self.blur_thumbnails
                    overlay.blur = 10 if self.blur_thumbnails else 0
                    overlay.bgcolor = ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK)
                    overlay.update()
                except (AttributeError, IndexError):
                    continue

        # Update details view if visible
        if self.details_view.visible and self.details_view.content:
            try:
                # Navigate through the control hierarchy to find the image overlay
                details_content = self.details_view.content
                responsive_row = details_content.controls[1]  # Get the ResponsiveRow
                image_column = responsive_row.controls[0]  # Get the first column (image column)
                image_container = image_column.controls[0]  # Get the image container
                image_stack = image_container.content  # Get the Stack
                overlay = image_stack.controls[1]

                overlay.visible = self.blur_thumbnails
                overlay.blur = 10 if self.blur_thumbnails else 0
                overlay.bgcolor = ft.colors.with_opacity(0.3 if self.blur_thumbnails else 0, ft.colors.BLACK)
                overlay.update()
            except (AttributeError, IndexError):
                pass

        self.page.update()
