"""
Main entry point for the Doudesu package.
Handles both CLI and GUI modes.
"""

import argparse
import sys
from importlib.util import find_spec

from rich.console import Console

from .core import Doujindesu
from .ui import run_cli, run_gui

console = Console()


def check_gui_dependencies() -> bool:
    """Check if GUI dependencies are installed."""
    return find_spec("flet") is not None


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
    parser.add_argument("--url", type=str, help="Download manga by URL")
    parser.add_argument("--cli", action="store_true", help="Run in interactive CLI mode")

    args = parser.parse_args()

    if args.gui or args.browser:
        if check_gui_dependencies():
            run_gui(browser_mode=args.browser)
        else:
            console.print(
                "[red]GUI dependencies not installed. Please install with:[/red]"
                "\n[yellow]pip install doudesu\[gui][/yellow]"  # noqa: W605
            )
            sys.exit(1)
    elif args.search:
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
        try:
            manga = Doujindesu(args.url)
            details = manga.get_details()
            if details:
                console.print(f"\n[bold]Title: {details.name}[/bold]")
                console.print(f"Author: {details.author}")
                console.print(f"Series: {details.series}")
                console.print(f"Score: {details.score}")
                console.print(f"Chapters: {len(manga.get_all_chapters())}")
                console.print("FYI, if you want to download the chapters, you can use the --cli flag")
            else:
                console.print("[red]Could not get manga details[/red]")
        except Exception as e:
            console.print(f"[red]Error: {e!s}[/red]")
    elif args.cli:
        try:
            run_cli()
        except KeyboardInterrupt:
            console.print("\n[red]Exiting...[/red]")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
