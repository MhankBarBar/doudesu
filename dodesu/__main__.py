import argparse

import flet as ft

from .cli import cli_main
from .doudesu_flet import DoujindesuApp


def parse_args():
    parser = argparse.ArgumentParser(description="Doujindesu Downloader")
    parser.add_argument("--gui", action="store_true", help="Run in GUI mode using Flet")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    return parser.parse_args()


def gui_main(page: ft.Page):
    page.title = "Doujindesu Downloader"
    page.window.width = 800
    page.window.height = 900
    page.window.resizable = True

    app = DoujindesuApp()
    app.set_page(page)
    page.add(app.build())


def main():
    args = parse_args()
    if args.gui:
        ft.app(target=gui_main, view=ft.AppView.FLET_APP)
    elif args.cli:
        cli_main()
    else:
        print("Please specify either --gui or --cli mode")


if __name__ == "__main__":
    main()
