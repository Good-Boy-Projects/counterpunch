<div align="center">

<img src="packaging/trufont-logo-1024.png" alt="Counterpunch icon" width="128">

# Counterpunch

**A UFO-native font editor for macOS and Linux**

</div>

Counterpunch is a modern font editor built with Python 3 and PySide6 (Qt 6). It is a
fork of [TruFont](https://trufont.github.io), ported from PyQt5 to PySide6 and
developed independently. It works directly on UFO sources. It is built for
macOS, with Linux support planned.

**Status:** early development (0.x). Expect rough edges - I'm working on it!.

## Getting started

Counterpunch is currently run from source. Only macOS is supported at the
moment; Linux is planned.

1.  Install [uv](https://docs.astral.sh/uv/) (`brew install uv`) and
    Python 3.12.

2.  Clone the repository and create a virtual environment:

    ```
    git clone git@github.com:Good-Boy-Projects/counterpunch.git
    cd counterpunch
    uv venv --python 3.12
    source .venv/bin/activate
    ```

3.  Install in editable mode:

    ```
    uv pip install -e ".[dev]"
    ```

4.  Run the app:

    ```
    python -m trufont
    ```

The Python package is still named `trufont` internally.

## Building the macOS app

Install PyInstaller in the virtual environment, then run the packaging script:

```
uv pip install pyinstaller
./packaging/build-app.sh
```

The app is written to `dist/Counterpunch.app`. Copy it to `/Applications` to
launch it from the Dock. Builds are unsigned, so macOS may ask you to approve
the first launch.

## Versioning

Releases use semantic version tags with a `v` prefix, such as `v0.1.1`. The
version is derived from the latest git tag, so a tag must be a valid Python
version (no suffixes like `-beta`; use `rc1` or `b1` for pre-releases).

## License

Counterpunch is licensed under the GNU GPL v3 or the GNU LGPL v3, at your
option, as inherited from TruFont. See `COPYRIGHT`, `LICENSE.GPLv3` and
`LICENSE.LGPLv3`. Credits are in `THANKS`.