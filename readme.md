# PySideUp

This repository contains PySideUp, a tool for converting PySide2 code to PySide6. The conversion updates imports, changes outdated components, and ensures your project is compatible with PySide6.

## Features
- **Automatic Import Update**: Converts PySide2 imports to PySide6 equivalents.
- **Wildcard Handling**: Converts wildcard imports to explicitly imported components.

## Installation
You can install PySideUp from PyPI:
```sh
pip install pysideup
```

## Usage
To convert a PySide2 file to PySide6, use the `pysideup` command:
```sh
pysideup <directory_path>
```
You can also specify directories to exclude using `--exclude`.

## Example Conversions
### Before Conversion (PySide2)
```python
from PySide2.QtWidgets import QWidget, QVBoxLayout, QAction
from PySide2.QtGui import QIcon

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with QAction")
        layout = QVBoxLayout()
        self.setLayout(layout)
        action = QAction("Test Action", self)
        self.setWindowIcon(QIcon())
```

### After Conversion (PySide6)
```python
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QAction, QIcon

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with QAction")
        layout = QVBoxLayout()
        self.setLayout(layout)
        action = QAction("Test Action", self)
        self.setWindowIcon(QIcon())
```

## Running Unit Tests
Unit tests are provided to ensure that the conversion works as expected. To run the tests, execute:
```sh
python -m unittest discover
```
The tests cover various cases, including multiple imports, wildcard imports, and aliased imports.

## Contributing
Contributions are welcome! Feel free to submit issues or pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.

