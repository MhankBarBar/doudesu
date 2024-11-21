"""
Main entry point for the Dodesu package.
Handles both CLI and GUI modes.
"""

import argparse
import sys
from importlib.util import find_spec

from rich.console import Console

from .cli import run_cli

console = Console()


def check_gui_dependencies() -> bool:
    """Check if GUI dependencies are installed."""
    return find_spec("flet") is not None


def run_gui():
    """Run the GUI version of the application."""
    try:
        import flet as ft
        from .doudesu_flet import DoujindesuApp

        def main(page: ft.Page):
            # Configure page
            page.title = "Doujindesu Downloader"
            page.window.width = 00
            page.window.height = 900
            page.window.resizable = True

            # Initialize and add app
            app = DoujindesuApp()
            app.set_page(page)
            page.add(app.build())

        ft.app(target=main)
    except ImportError:
        console.print(
            "[red]GUI dependencies not installed. Please install with:[/red]"
            "\n[yellow]pip install dodesu[gui][/yellow]"
        )
        sys.exit(1)


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(
        description="Dodesu - A manga downloader for doujindesu.tv"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run in GUI mode (requires dodesu[gui] installation)",
    )
    parser.add_argument("--search", type=str, help="Search manga by keyword")
    parser.add_argument("--url", type=str, help="Download manga by URL")
    parser.add_argument(
        "--interactive", action="store_true", help="Run in interactive CLI mode"
    )

    args = parser.parse_args()

    if args.gui:
        if check_gui_dependencies():
            run_gui()
        else:
            console.print(
                "[red]GUI dependencies not installed. Please install with:[/red]"
                "\n[yellow]pip install dodesu[gui][/yellow]"
            )
            sys.exit(1)
    elif args.search:
        from .doudesu import Doujindesu

        results = Doujindesu.search(args.search)
        if results:
            for manga in results.results:
                console.print(f"\n[bold]{manga.name}[/bold]")
                console.print(f"URL: {manga.url}")
                console.print(f"Type: {manga.type}")
                console.print(f"Score: {manga.score}")
        else:
            console.print("[red]No results found[/red]")
    elif args.url:
        from .doudesu import Doujindesu

        try:
            manga = Doujindesu(args.url)
            details = manga.get_details()
            if details:
                console.print(f"\n[bold]Title: {details.name}[/bold]")
                console.print(f"Author: {details.author}")
                console.print(f"Series: {details.series}")
                console.print(f"Score: {details.score}")
                console.print("\nDownloading chapters...")
                chapters = manga.get_all_chapters()
                for chapter_url in chapters:
                    manga.url = chapter_url
                    console.print(f"\nDownloading: {chapter_url}")
                    images = manga.get_all_images()
                    if images:
                        console.print(f"Found {len(images)} images")
            else:
                console.print("[red]Could not get manga details[/red]")
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
    elif args.interactive:
        try:
            run_cli()
        except KeyboardInterrupt:
            console.print("\n[red]Exiting...[/red]")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
