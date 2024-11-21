# Dodesu

A Python application for downloading and converting manga from doujindesu.tv into PDF format, featuring both GUI and CLI interfaces.

## Table of Contents

* [📖 Introduction](#introduction)
* [⚙️ Features](#features)
* [⚠️ Requirements](#requirements)
* [📦 Installation](#installation)
* [💻 Usage](#usage)
* [🤝 Contributing](#contributing)

## Introduction

Dodesu is a powerful Python tool that automates the process of downloading manga chapters from doujindesu.tv and converting them into PDF format. It offers both a user-friendly graphical interface and a command-line interface to suit different user preferences.

## Features

* 🔍 Search manga by title or URL
* 📥 Batch download multiple chapters
* 📱 Modern, responsive GUI built with Flet
* 🖥️ Command-line interface for automation
* 🌙 Dark/Light theme support
* 📄 Automatic PDF conversion
* 🔄 Pagination support for search results
* 🖼️ High-quality image preservation
* 🚀 Multi-threaded downloads for better performance

## Requirements

* Python 3.11 or higher
* Internet connection
* Supported operating systems: Windows, macOS (haven't tested), Linux (haven't tested)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/MhankBarBAr/dodesu.git
cd dodesu
```

2. Install uv (recommended package manager):
```bash
pip install uv
```

3. Install dependencies:
```bash
uv pip install -r pyproject.toml
```

## Usage

### Graphical Interface (GUI)

To launch the GUI version:
```bash
uv run python -m dodesu --gui
```

### Command Line Interface (CLI)

To use the CLI version:
```bash
uv run python -m dodesu --cli
```

### Features Guide

1. **Search by Title**
   - Enter manga title in the search box
   - Browse through paginated results
   - Click on a manga to view details
   - Download individual chapters or entire series

2. **Download by URL**
   - Paste direct manga URL
   - Automatically downloads all available chapters
   - Converts to PDF with original quality

3. **Theme Switching**
   - Toggle between light and dark themes
   - Persistent theme preference

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request