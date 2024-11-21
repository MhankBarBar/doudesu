from rich.console import Console
from rich.prompt import Prompt
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
import os

from .converter import ImageToPDFConverter
from .doudesu import Doujindesu

console = Console()


def cli_main():
    try:
        console.print("[bold blue]Doujindesu Downloader CLI[/bold blue]")
        console.print("1. Search manga")
        console.print("2. Download by URL")

        choice = Prompt.ask("Choose an option", choices=["1", "2"])

        if choice == "1":
            search_manga()
        else:
            download_by_url()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/red]")


def display_results(results):
    console.print("\n[green]Search Results:[/green]")
    for idx, result in enumerate(results.results, 1):
        console.print(f"\n{idx}. {result.name}")
        console.print(f"   Type: [blue]{result.type}[/blue]")
        console.print(f"   Genre: {', '.join(result.genre)}")
        console.print(f"   Status: {result.status}")
        console.print(f"   Score: {result.score}")


def handle_navigation(results):
    while True:
        options = []
        if results.previous_page_url:
            options.append("p")
            console.print("\n[P]revious page", style="blue")
        if results.next_page_url:
            options.append("n")
            console.print("[N]ext page", style="blue")
        options.extend(["s", "q"])
        console.print("[S]elect manga to download")
        console.print("[Q]uit to main menu")

        choice = Prompt.ask("\nChoose an option", choices=options).lower()

        if choice == "q":
            return None
        elif choice == "s":
            return handle_selection(results)
        elif choice == "n" and results.next_page_url:
            return Doujindesu.get_search_by_url(results.next_page_url)
        elif choice == "p" and results.previous_page_url:
            return Doujindesu.get_search_by_url(results.previous_page_url)


def handle_selection(results):
    choice = Prompt.ask("\nEnter number to download (0 to cancel)", default="0")
    if choice.isdigit() and 0 < int(choice) <= len(results.results):
        selected = results.results[int(choice) - 1]
        download_manga(selected.url)
    return None


def search_manga():
    query = Prompt.ask("\nEnter manga name to search")
    console.print(f"\nSearching for: {query}")

    results = Doujindesu.search(query)
    while results and results.results:
        display_results(results)
        next_results = handle_navigation(results)
        if next_results is None:
            break
        results = next_results


def download_by_url():
    url = Prompt.ask("\nEnter manga URL")
    download_manga(url)


def download_manga(url: str):
    console.print(f"\n[blue]Downloading from: {url}[/blue]")

    result_dir = "result"
    os.makedirs(result_dir, exist_ok=True)

    doujin = Doujindesu(url)
    chapters = doujin.get_all_chapters()

    if not chapters:
        console.print("[red]No chapters found[/red]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        overall_task = progress.add_task("[cyan]Overall Progress", total=len(chapters))

        for chapter_url in chapters:
            doujin.url = chapter_url
            images = doujin.get_all_images()

            if images:
                title = "-".join(doujin.soup.title.text.split("-")[:-1]).strip()
                filename = os.path.join(result_dir, f"{title}.pdf")

                chapter_task = progress.add_task(
                    f"[green]Downloading: {title}", total=len(images)
                )

                converter = ImageToPDFConverter(images, filename)

                def progress_callback(current, total):
                    progress.update(chapter_task, completed=current)

                converter.convert_images_to_pdf(images, filename)

                progress.update(chapter_task, completed=len(images))
                progress.remove_task(chapter_task)

                progress.update(overall_task, advance=1)

                console.print(f"[green]✓[/green] Successfully downloaded: {title}")
            else:
                console.print("[red]✗[/red] No images found in chapter")
                progress.update(overall_task, advance=1)

    console.print("\n[bold green]Download completed![/bold green]")
