"""
Main entry point for the Doudesu package.
Handles both CLI and GUI modes.
"""

import argparse
import sys
from importlib.util import find_spec

from rich.console import Console

from .core import Doujindesu
from .ui import run_cli
from .ui.cli import (
    ImageToPDFConverter,
    display_manga_details,
    get_int_input,
    select_chapters,
)

console = Console()


def check_gui_dependencies() -> bool:
    """Check if GUI dependencies are installed."""
    return find_spec("flet") is not None


def check_api_dependencies() -> bool:
    """Check if API dependencies are installed."""
    return all(find_spec(pkg) is not None for pkg in ["fastapi", "uvicorn"])


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser(description="Doudesu - A manga downloader for doujindesu.tv")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run in GUI mode (requires doudesu[gui] installation)",
    )
    parser.add_argument(
        "--browser",
        action="store_true",
        help="Run GUI in browser mode on localhost:6969",
    )
    parser.add_argument("--search", type=str, help="Search manga by keyword")
    parser.add_argument("--page", type=int, default=1, help="Page number for search results (default: 1)")
    parser.add_argument("--url", type=str, help="Download manga by URL")
    parser.add_argument("--cli", action="store_true", help="Run in interactive CLI mode")
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run in API mode (requires doudesu[api] installation)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=6969,
        help="Port number for API server (default: 6969)",
    )

    args = parser.parse_args()

    if args.gui or args.browser:
        if check_gui_dependencies():
            from .ui import run_gui

            run_gui(browser_mode=args.browser)
        else:
            console.print(
                "[red]GUI dependencies not installed. Please install with:[/red]"
                "\n[yellow]pip install doudesu\[gui][/yellow]"  # noqa: W605
            )
            sys.exit(1)
    elif args.search:
        try:
            current_results = Doujindesu.search(args.search, args.page)
            if not current_results or not current_results.results:
                console.print("[red]No results found[/red]")
                return

            console.print(f"\n[bold cyan]Search Results (Page {args.page}):[/bold cyan]")
            for i, manga in enumerate(current_results.results, 1):
                type_color = "green" if manga.type.lower() == "manga" else "yellow"
                score_color = "green" if float(manga.score) >= 7 else "yellow"

                console.print(f"\n[bold white]{i}. {manga.name}[/bold white]")
                console.print(f"   URL: [blue]{manga.url}[/blue]")
                console.print(f"   Type: [{type_color}]{manga.type}[/{type_color}]")
                console.print(f"   Score: [{score_color}]★ {manga.score}[/{score_color}]")

            if current_results.next_page_url:
                next_page = args.page + 1
                console.print(f"\n[blue]Next page available. Use --page {next_page} to view[/blue]")
            if current_results.previous_page_url:
                prev_page = args.page - 1
                console.print(f"[blue]Previous page available. Use --page {prev_page} to view[/blue]")

            selection = get_int_input(
                "Select manga number (0 to cancel)",
                0,
                len(current_results.results),
            )

            if selection == 0:
                return

            selected_manga = current_results.results[selection - 1]
            manga = Doujindesu(selected_manga.url)
            details = manga.get_details()

            display_manga_details(details)

            chapters = manga.get_all_chapters()
            if not chapters:
                console.print("[red]No chapters found[/red]")
                return

            selected_indices = select_chapters(len(chapters))
            for idx in selected_indices:
                chapter_url = chapters[idx]
                console.print(f"\n[cyan]Downloading Chapter {idx + 1}...[/cyan]")

                manga.url = chapter_url
                images = manga.get_all_images()

                if images:
                    console.print(f"Found {len(images)} images")
                    title = f"{details.name} - Chapter {idx + 1}"
                    pdf_path = f"result/{title}.pdf"
                    ImageToPDFConverter(images, pdf_path).convert_images_to_pdf(images, pdf_path)
                    console.print(f"[green]Saved as: {pdf_path}[/green]")
                else:
                    console.print("[red]No images found in chapter[/red]")

        except KeyboardInterrupt:
            console.print("\n[red]Operation cancelled[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e!s}[/red]")
    elif args.url:
        try:
            manga = Doujindesu(args.url)
            details = manga.get_details()

            display_manga_details(details)

            chapters = manga.get_all_chapters()
            if not chapters:
                console.print("[red]No chapters found[/red]")
                return

            selected_indices = select_chapters(len(chapters))
            for idx in selected_indices:
                chapter_url = chapters[idx]
                console.print(f"\n[cyan]Downloading Chapter {idx + 1}...[/cyan]")

                manga.url = chapter_url
                images = manga.get_all_images()

                if images:
                    console.print(f"Found {len(images)} images")
                    title = f"{details.name} - Chapter {idx + 1}"
                    pdf_path = f"result/{title}.pdf"
                    ImageToPDFConverter(images, pdf_path).convert_images_to_pdf(images, pdf_path)
                    console.print(f"[green]Saved as: {pdf_path}[/green]")
                else:
                    console.print("[red]No images found in chapter[/red]")

        except KeyboardInterrupt:
            console.print("\n[red]Operation cancelled[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e!s}[/red]")
    elif args.cli:
        try:
            run_cli()
        except KeyboardInterrupt:
            console.print("\n[red]Exiting...[/red]")
    elif args.api:
        if check_api_dependencies():
            import uvicorn

            from .api import app

            console.print(f"[green]Starting API server on port {args.port}...[/green]")
            uvicorn.run(app, host="0.0.0.0", port=args.port)
        else:
            console.print(
                "[red]API dependencies not installed. Please install with:[/red]"
                "\n[yellow]pip install doudesu\[api][/yellow]"  # noqa: W605
            )
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
