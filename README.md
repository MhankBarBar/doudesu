<div align="center">
    <img src="./doudesu/assets/images/logo.png" alt="logo" width="200">
</div>

A powerful manga downloader and Python wrapper for doujindesu.tv with both CLI and GUI interfaces.

![Python Version](https://img.shields.io/pypi/pyversions/doudesu?logo=python)
![License](https://img.shields.io/pypi/l/doudesu?logo=gnu)
![PyPI Version](https://img.shields.io/pypi/v/doudesu?logo=pypi)
![Downloads](https://img.shields.io/pypi/dm/doudesu?logo=pypi)

## Features

- 🔍 Search manga by title with pagination
- 📱 Modern GUI interface with dark/light theme
- 💻 Feature-rich CLI interface
- 📖 Download single or multiple chapters
- 📑 Automatic PDF conversion
- 🌙 Dark/Light theme support
- 🎨 Beautiful and intuitive interface

## Installation

### Basic Installation
```bash
pip install doudesu
```

### With GUI Support
> [!NOTE]
> GUI support requires `flet` to be installed.
> Currently tested on Windows only.
```bash
pip install doudesu[gui]
```

## Command-Line Usage

### Available Commands
```bash
# Launch GUI interface (requires GUI support)
doudesu --gui

# Launch GUI in browser mode on localhost:6969
doudesu --browser

# Launch interactive CLI interface
doudesu --cli

# Search manga by keyword
doudesu --search "manga name"

# Download manga directly by URL
doudesu --url "https://doujindesu.tv/manga/your-manga-url"

# Show help message
doudesu --help
```

### Command Options
```
Options:
  --gui          Run in GUI mode (requires doudesu[gui] installation)
  --browser      Run GUI in browser mode on localhost:6969
  --search TEXT  Search manga by keyword
  --url TEXT     Download manga by URL
  --cli          Run in interactive CLI mode
```

### CLI Features

- 🎨 Colorful and intuitive interface
- 📄 Detailed manga information
- 📚 Chapter selection options:
  - Download all chapters
  - Download specific chapter
  - Download range of chapters
- 🔄 Pagination support for search results
- ✨ Progress indicators
- 🎯 Smart single-chapter handling

### GUI Features

- 🎨 Modern and responsive design
- 🌓 Dark/Light theme toggle
- 🖼️ Thumbnail previews
- 📊 Download progress tracking
- 🔍 Advanced search capabilities

## Python API Usage

```python
from doudesu import Doujindesu

# Search for manga
results = Doujindesu.search("manga name")
for manga in results.results:
    print(f"Title: {manga.name}")
    print(f"URL: {manga.url}")

manga = Doujindesu("https://doujindesu.tv/manga/your-manga-url")
details = manga.get_details()
chapters = manga.get_all_chapters()

# Get chapter images
manga.url = chapters[0]  # Set to specific chapter
images = manga.get_all_images()
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
