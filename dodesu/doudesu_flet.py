import flet as ft
import os

from .converter import ImageToPDFConverter
from .doudesu import Doujindesu, Result
from .loading_animation import LoadingAnimation


class DoujindesuApp:
    def __init__(self):
        self.page = None
        self.doujindesu = None
        self.results = []
        self.selected_result = None
        self.next_page_url = None
        self.previous_page_url = None
        self.result_folder = "result"

        # Create result folder if it doesn't exist
        os.makedirs(self.result_folder, exist_ok=True)

        # Initialize UI elements
        self.logo = ft.Image(
            src="assets/logo.png",
            width=200,
            height=80,
            fit=ft.ImageFit.CONTAIN,
        )
        self.nav_rail = ft.NavigationRail(
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.SEARCH, label="Search by Keyword"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.LINK, label="Download by URL"
                ),
            ],
            selected_index=0,
            on_change=self.handle_option_change,
        )
        self.search_query = ft.TextField(
            label="Manga name", width=300, visible=True, on_submit=self.handle_search
        )
        self.url_input = ft.TextField(
            label="Manga URL",
            width=300,
            visible=False,
            hint_text="Enter manga URL here...",
            on_submit=self.handle_download_by_url,
        )
        self.status_text = ft.Text(size=16, color=ft.colors.BLUE)

        # Add download state flag
        self.is_downloading = False

        # Update button styles
        button_style = {
            "bgcolor": ft.colors.BLUE_700,
            "color": ft.colors.WHITE,
            "style": ft.ButtonStyle(
                padding=ft.padding.all(15),
                shape={
                    ft.MaterialState.DEFAULT: ft.RoundedRectangleBorder(radius=8),
                },
            ),
        }

        self.search_button = ft.ElevatedButton(
            "Search", icon=ft.icons.SEARCH, on_click=self.handle_search, **button_style
        )

        self.download_button = ft.ElevatedButton(
            "Download",
            icon=ft.icons.DOWNLOAD,
            on_click=self.handle_download_by_url,
            visible=False,
            **button_style,
        )

        self.previous_button = ft.ElevatedButton(
            "Previous",
            icon=ft.icons.ARROW_BACK,
            on_click=self.handle_previous,
            visible=False,
            **button_style,
        )

        self.next_button = ft.ElevatedButton(
            "Next",
            icon=ft.icons.ARROW_FORWARD,
            on_click=self.handle_next,
            visible=False,
            **button_style,
        )

        self.search_results = ft.ListView(
            expand=True,
            spacing=10,
            padding=20,
            animate_size=300,
        )

        self.loading_animation = LoadingAnimation()
        self.download_progress = ft.ProgressBar(visible=False)
        self.download_status = ft.Text(visible=False)

        self.main_view = ft.Container(
            content=self.build_main_view(), visible=True, expand=True
        )

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
                            ft.Text(
                                "Search Results", size=20, weight=ft.FontWeight.BOLD
                            ),
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
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                self.url_input,
                                self.download_button,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=20,
                        ),
                        padding=40,
                        border_radius=10,
                    ),
                    self.status_text,
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            visible=False,
            expand=True,
            alignment=ft.alignment.center,
        )

        self.download_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text(
                        "Downloading...",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.ProgressRing(width=40, height=40, stroke_width=4),
                    ft.Text(
                        "",
                        size=16,
                        color=ft.colors.WHITE,
                    ),
                    ft.ProgressBar(width=300),
                    ft.Text(
                        "",
                        size=14,
                        color=ft.colors.GREY_400,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
            ),
            bgcolor=ft.colors.BLACK54,
            padding=30,
            border_radius=10,
            visible=False,
        )

    def handle_previous(self, e):
        if self.previous_page_url:
            self.loading_animation.content.controls[
                1
            ].value = "Loading previous page..."
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
            self.search_results.controls = [
                self.create_result_control(result) for result in self.results
            ]
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
            self.main_view.visible = True
            self.url_download_view.visible = False
            self.search_results_view.visible = False
            self.details_view.visible = False
            self.search_query.visible = True
            self.url_input.visible = False
            self.search_button.visible = True
            self.download_button.visible = False
        else:  # Download by URL
            self.main_view.visible = False
            self.url_download_view.visible = True
            self.search_results_view.visible = False
            self.details_view.visible = False
            self.search_query.visible = False
            self.url_input.visible = True
            self.search_button.visible = False
            self.download_button.visible = True

        self.page.update()

    def create_result_control(self, result: Result):
        # Get color based on type
        type_color = (
            ft.colors.BLUE_700
            if result.type.lower() == "doujinshi"
            else ft.colors.GREEN_700
        )

        card = ft.Container(
            content=ft.Row(
                [
                    ft.Image(
                        result.thumbnail,
                        width=120,
                        height=180,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(8),
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                result.name,
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.WHITE,
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
                        icon=ft.icons.DOWNLOAD,
                        icon_color=ft.colors.BLUE_400,
                        tooltip="Download",
                        on_click=lambda e: self.download_manga(e, result.url),
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

        # Get detailed information using get_details
        details = Doujindesu(result.url).get_details()

        if not details:
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text(
                "Failed to load details!", color=ft.colors.WHITE
            )
            self.page.show_snack_bar(self.snackbar)
            return

        # Get color based on type
        type_color = (
            ft.colors.BLUE_700
            if details.type.lower() == "doujinshi"
            else ft.colors.GREEN_700
        )

        details_content = ft.Column(
            [
                ft.Container(
                    content=ft.Image(
                        details.thumbnail,
                        width=200,
                        height=300,
                        fit=ft.ImageFit.COVER,
                        border_radius=ft.border_radius.all(12),
                    ),
                    animate=ft.animation.Animation(300, "easeOut"),
                ),
                ft.Text(
                    details.name,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.WHITE,
                ),
                ft.Text(
                    f"Series: {details.series}",
                    size=16,
                    color=ft.colors.GREY_400,
                ),
                ft.Text(
                    f"Author: {details.author}",
                    size=16,
                    color=ft.colors.GREY_400,
                ),
                ft.Text(
                    f"Chapters: {len(details.chapter_urls)}",
                    size=16,
                    color=ft.colors.GREY_400,
                ),
                ft.Text(
                    f"Genre: {', '.join(details.genre)}",
                    size=16,
                    color=ft.colors.GREY_400,
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
                    ],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text(
                    f"Score: {details.score}",
                    size=16,
                    color=ft.colors.YELLOW_400,
                ),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Download",
                            icon=ft.icons.DOWNLOAD,
                            on_click=lambda e: self.download_manga(e, result.url),
                            bgcolor=ft.colors.BLUE_700,
                        ),
                        ft.ElevatedButton(
                            "Back",
                            icon=ft.icons.ARROW_BACK,
                            on_click=self.show_search_results,
                            bgcolor=ft.colors.GREY_700,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            spacing=20,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # Update the content instead of recreating the container
        self.details_view.content = details_content

        # Hide search results and show details
        self.search_results.visible = False
        self.details_view.visible = True

        # Update both views
        self.details_view.update()
        self.search_results.update()

    def show_search_results(self, e):
        self.details_view.visible = False
        self.search_results.visible = True
        self.details_view.update()
        self.search_results.update()

    def convert_images_to_pdf(self, images, title):
        # Create full path for the PDF file
        pdf_path = os.path.join(self.result_folder, title)
        
        ImageToPDFConverter(images, output_pdf_file=pdf_path).convert_images_to_pdf(
            images, pdf_path
        )
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
            self.previous_page_url = (
                search_result.previous_page_url if search_result else None
            )
            self.update_search_results()
            self.show_search_results_view()  # Switch to search results view
        finally:
            self.loading_animation.visible = False
            self.loading_animation.update()

    def handle_download_by_url(self, e):
        url = self.url_input.value
        if not url:
            self.status_text.value = "Please enter a manga URL to download."
            self.status_text.update()
            return

        self.status_text.value = "Downloading images..."
        self.status_text.update()
        self.download_manga(e, url)

    def download_manga(self, e, url: str):
        if self.is_downloading:
            self.snackbar.bgcolor = ft.colors.ORANGE_700
            self.snackbar.content = ft.Text(
                "Download already in progress!", color=ft.colors.WHITE
            )
            self.page.show_snack_bar(self.snackbar)
            return

        self.is_downloading = True

        # Disable all download buttons
        self.download_button.disabled = True
        self.download_button.update()

        # If we're in search results, disable all download icons
        if self.search_results.controls:
            for result in self.search_results.controls:
                download_icon = result.content.controls[
                    -1
                ]  # Get the download icon button
                download_icon.disabled = True
                download_icon.update()

        # If we're in details view, disable the download button
        if self.details_view.visible and self.details_view.content:
            buttons_row = self.details_view.content.controls[-1]  # Get the buttons row
            download_btn = buttons_row.controls[0]  # Get the download button
            download_btn.disabled = True
            download_btn.update()

        try:
            # Show download progress container
            progress_text = self.download_container.content.controls[2]
            progress_bar = self.download_container.content.controls[3]
            image_progress = self.download_container.content.controls[4]

            self.download_container.visible = True
            self.download_container.update()

            self.doujindesu = Doujindesu(url)
            chapters = self.doujindesu.get_all_chapters()

            if not chapters:
                self.status_text.value = "No chapters found."
                self.status_text.update()
                self.snackbar.bgcolor = ft.colors.RED_700
                self.snackbar.content = ft.Text(
                    "No chapters found!", color=ft.colors.WHITE
                )
                self.page.show_snack_bar(self.snackbar)
                return

            total_chapters = len(chapters)
            progress_bar.value = 0
            progress_bar.max = total_chapters
            downloaded_files = []

            for idx, chapter_url in enumerate(chapters, 1):
                self.doujindesu.url = chapter_url
                progress_text.value = f"Downloading Chapter {idx}/{total_chapters}"
                progress_text.update()

                images = self.doujindesu.get_all_images()

                if images:
                    total_images = len(images)
                    for img_idx, _ in enumerate(images, 1):
                        image_progress.value = (
                            f"Processing image {img_idx}/{total_images}"
                        )
                        image_progress.update()

                    title = (
                        "-".join(
                            self.doujindesu.soup.title.text.split("-")[:-1]
                        ).strip()
                        + ".pdf"
                    )
                    self.convert_images_to_pdf(images, title)
                    # Store relative path for display
                    downloaded_files.append(os.path.join(self.result_folder, title))
                    progress_bar.value = idx
                    progress_bar.update()

            self.status_text.value = "Download completed!"
            self.status_text.update()

            # Show completion notification with file names
            self.snackbar.bgcolor = ft.colors.GREEN_700
            self.snackbar.content = ft.Text(
                f"Download completed! Saved {len(downloaded_files)} file(s) in {self.result_folder}/",
                color=ft.colors.WHITE,
            )
            self.page.show_snack_bar(self.snackbar)

        except Exception as e:
            # Show error notification
            self.snackbar.bgcolor = ft.colors.RED_700
            self.snackbar.content = ft.Text(f"Error: {str(e)}", color=ft.colors.WHITE)
            self.page.show_snack_bar(self.snackbar)

        finally:
            self.is_downloading = False

            # Re-enable all download buttons
            self.download_button.disabled = False
            self.download_button.update()

            # Re-enable search result download icons
            if self.search_results.controls:
                for result in self.search_results.controls:
                    download_icon = result.content.controls[-1]
                    download_icon.disabled = False
                    download_icon.update()

            # Re-enable details view download button
            if self.details_view.visible and self.details_view.content:
                buttons_row = self.details_view.content.controls[-1]
                download_btn = buttons_row.controls[0]
                download_btn.disabled = False
                download_btn.update()

            self.download_container.visible = False
            self.download_container.update()

    def build_main_view(self):
        return ft.Column(
            [
                ft.Container(
                    content=self.logo,
                    alignment=ft.alignment.center,
                    animate=ft.animation.Animation(300, "easeOut"),
                ),
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [self.search_query, self.url_input],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            ft.Row(
                                [self.search_button, self.download_button],
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=20,
                    border_radius=10,
                ),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
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
        return ft.Row(
            [
                self.nav_rail,
                ft.VerticalDivider(width=1),
                ft.Stack(
                    [
                        self.main_view,
                        self.url_download_view,
                        self.search_results_view,
                        self.details_view,
                        self.loading_animation,
                        self.download_container,
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        )

    def set_page(self, page):
        self.page = page
        # Set window to maximized on start
        self.page.window_maximized = True
        self.page.update()
