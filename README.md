# JAME - just another Markdown editor

JAME (/ˌʤame/) is - as the name implies - *just another* Markdown editor programmed fully in Python.

## Scope of this project
This project is **not** meant to be a "perfect" Markdown editor with bucketloads of functionality; if I wanted to realize such an app, I would just import `commonmark.py` (or any other Markdown parsing library) + `pdfkit` and go from there.

So what is it for then? It aims - first and foremost - to serve as a *learning opportunity* for myself, especially regarding
- parsing in general (learning about different ways parsing can be done; mostly not visible in the code itself)
    - working with & converting to/from different file formats
- implementing & adhering to a given specification (this project intends (!) to *fully* implement [CommonMark](https://commonmark.org/))
- packaging & deploying a Python application

## Planned functionality
- Exporting to more file formats, including, but not limited to:
    - PDF
    - XML
    - LaTeX
- full [CommonMark](https://commonmark.org/) support (current status: 355 of 652 tests passing 😐)
- Syntax highlighting in the text editing field **(✓ DONE: `86329ed`)**
- Synchronized scrolling between the editing & preview pane

## Installation
### Pre-packaged binaries
Pre-packaged binaries are made avaliable for Linux & Windows in the Releases tab of this project.

### Building from source
Prerequisites for building this project from source are listed in the "Dependencies" section below. If you have all of them installed, follow the steps below.

1. Obtain the source code from this repository, either through the means of `git clone` (`git` is required for that, of course) or by downloading the source code .zip (or .tar.gz) from the Releases tab
2. Go into the root directory of this project (the one with this README in it)
3. Open up a terminal and run the command `pyinstaller (linux.spec|windows.spec)` (depending on the platform you are building on)
4. **That's it!**

(*Note:* I do not provide a .spec file nor a pre-packaged binary distribution for macOS as I do not have any Mac to test/build it on)

## Dependencies
**NOTE:** You do *not* need to install these dependencies if you are using one of the pre-packaged binaries, as they include them. Only install them if you want to build this project from source!

- [Python 3.10](https://www.python.org/downloads/) (yes, version 3.10, as I use "match"-statements in the source code)
- [qt](https://www.qt.io/), or rather [PyQt5](https://pypi.org/project/PyQt5/) to be exact (`pip install pyqt5`)