[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)


# Exception Finder CLI
A small command‑line script to discover all `Exception` subclasses in a given Python module or package and display their inheritance tree.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributing](#contributing)
- [Possible Future Plans](#possible-future-plans)

## Features

- 🔍 Recursively scans a module or package (and its submodules) for all classes derived from `Exception`.
- 🌳 Prints a clean, indented inheritance tree starting from the built‑in `Exception` class.
- 🚫 Zero external dependencies—uses only Python’s built‑in libraries (`argparse`, `importlib`, `inspect`, `pkgutil`, etc.).

## Requirements

- Python 3.6 or later
- No third‑party modules required

## Installation

Right now it’s just a standalone script. Simply download or clone this repo:

```bash
git clone https://github.com/OMGnotThatGuy/exc_tree.git
cd exc_tree
chmod +x exc_tree.py
```

## Usage

```bash
% ./exc_tree.py requests
Exception
├── OSError
│   └── requests.exceptions.RequestException
│       ├── requests.exceptions.ChunkedEncodingError
│       ├── requests.exceptions.ConnectionError
│       │   ├── requests.exceptions.ConnectTimeout
│       │   ├── requests.exceptions.ProxyError
│       │   └── requests.exceptions.SSLError
│       ├── requests.exceptions.ContentDecodingError
│       ├── requests.exceptions.HTTPError
│       ├── requests.exceptions.InvalidHeader
│       ├── requests.exceptions.InvalidJSONError
│       │   └── requests.exceptions.JSONDecodeError
│       ├── requests.exceptions.InvalidSchema
│       ├── requests.exceptions.InvalidURL
│       │   └── requests.exceptions.InvalidProxyURL
│       ├── requests.exceptions.MissingSchema
│       ├── requests.exceptions.RetryError
│       ├── requests.exceptions.StreamConsumedError
│       ├── requests.exceptions.Timeout
│       │   └── requests.exceptions.ReadTimeout
│       ├── requests.exceptions.TooManyRedirects
│       ├── requests.exceptions.UnrewindableBodyError
│       └── requests.exceptions.URLRequired
├── RuntimeError
│   └── requests.cookies.CookieConflictError
├── TypeError
├── urllib3.exceptions.HTTPError
├── ValueError
│   └── json.decoder.JSONDecodeError
└── Warning
    ├── DeprecationWarning
    └── requests.exceptions.RequestsWarning
        ├── requests.exceptions.FileModeWarning
        └── requests.exceptions.RequestsDependencyWarning
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

# Contributing
Contributions, issues and feature requests are welcome! Feel free to open a pull request or submit an issue.

# Possible Future Plans
 - 📦 Turn this into an installable package
 - 🔧 Add options for custom output formats (JSON, DOT/Graphviz, etc.)
 - ⚙️ Allow filtering by base exception
