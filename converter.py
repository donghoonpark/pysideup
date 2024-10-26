import ast
import argparse
import logging
import os
import astor
import re

# Set up logging
logging.basicConfig(level=logging.INFO)

class PySide2ToPySide6Converter(ast.NodeTransformer):
    def __init__(self):
        self.used_symbols = set()
        self.symbol_to_module = {
            # QtCore
            'QTimer': 'PySide6.QtCore', 'QDate': 'PySide6.QtCore', 'QTime': 'PySide6.QtCore',
            'QDateTime': 'PySide6.QtCore', 'QObject': 'PySide6.QtCore', 'QEvent': 'PySide6.QtCore',
            'QThread': 'PySide6.QtCore', 'QMutex': 'PySide6.QtCore', 'QWaitCondition': 'PySide6.QtCore',
            'QSemaphore': 'PySide6.QtCore', 'QSettings': 'PySide6.QtCore', 'QCoreApplication': 'PySide6.QtCore',
            'QAbstractEventDispatcher': 'PySide6.QtCore', 'QRegularExpression': 'PySide6.QtCore',
            'QRegularExpressionValidator': 'PySide6.QtCore', 'QDesktopServices': 'PySide6.QtCore',
            'Qt': 'PySide6.QtCore',
            # QtGui
            'QFont': 'PySide6.QtGui', 'QPixmap': 'PySide6.QtGui', 'QImage': 'PySide6.QtGui',
            'QIcon': 'PySide6.QtGui', 'QColor': 'PySide6.QtGui', 'QPen': 'PySide6.QtGui',
            'QBrush': 'PySide6.QtGui', 'QKeySequence': 'PySide6.QtGui', 'QScreen': 'PySide6.QtGui',
            'QCursor': 'PySide6.QtGui', 'QPalette': 'PySide6.QtGui', 'QTextFormat': 'PySide6.QtGui',
            'QTextCursor': 'PySide6.QtGui', 'QTextCharFormat': 'PySide6.QtGui', 'QAction': 'PySide6.QtGui',
            'QSize': 'PySide6.QtGui', 'QRegion': 'PySide6.QtGui', 'QDesktopWidget': 'PySide6.QtGui',
            'QPrinterInfo': 'PySide6.QtPrintSupport',
            # QtWidgets
            'QWidget': 'PySide6.QtWidgets', 'QHBoxLayout': 'PySide6.QtWidgets', 'QVBoxLayout': 'PySide6.QtWidgets',
            'QPushButton': 'PySide6.QtWidgets', 'QLabel': 'PySide6.QtWidgets', 'QMainWindow': 'PySide6.QtWidgets',
            'QDialog': 'PySide6.QtWidgets', 'QLineEdit': 'PySide6.QtWidgets', 'QCheckBox': 'PySide6.QtWidgets',
            'QRadioButton': 'PySide6.QtWidgets', 'QTableWidget': 'PySide6.QtWidgets', 'QTabWidget': 'PySide6.QtWidgets',
            'QGridLayout': 'PySide6.QtWidgets', 'QFormLayout': 'PySide6.QtWidgets', 'QGroupBox': 'PySide6.QtWidgets',
            'QListView': 'PySide6.QtWidgets', 'QTreeView': 'PySide6.QtWidgets', 'QComboBox': 'PySide6.QtWidgets',
            'QSpinBox': 'PySide6.QtWidgets', 'QDoubleSpinBox': 'PySide6.QtWidgets', 'QSlider': 'PySide6.QtWidgets',
            'QProgressBar': 'PySide6.QtWidgets', 'QFrame': 'PySide6.QtWidgets', 'QToolBar': 'PySide6.QtWidgets',
            'QMenuBar': 'PySide6.QtWidgets', 'QMenu': 'PySide6.QtWidgets', 'QStatusBar': 'PySide6.QtWidgets',
            'QMessageBox': 'PySide6.QtWidgets', 'QFileDialog': 'PySide6.QtWidgets', 'QStackedWidget': 'PySide6.QtWidgets',
            'QSplitter': 'PySide6.QtWidgets', 'QGraphicsView': 'PySide6.QtWidgets', 'QGraphicsScene': 'PySide6.QtWidgets',
            'QGraphicsItem': 'PySide6.QtWidgets', 'QScrollArea': 'PySide6.QtWidgets', 'QTableView': 'PySide6.QtWidgets',
            'QListWidget': 'PySide6.QtWidgets', 'QListWidgetItem': 'PySide6.QtWidgets', 'QSizePolicy': 'PySide6.QtWidgets',
            # QtPrintSupport
            'QPrinter': 'PySide6.QtPrintSupport', 'QPrintDialog': 'PySide6.QtPrintSupport',
            'QPrintPreviewWidget': 'PySide6.QtPrintSupport', 'QPrintPreviewDialog': 'PySide6.QtPrintSupport',
            # QtConcurrent
            'QtConcurrent': 'PySide6.QtConcurrent',
            # QtMultimedia
            'QMediaPlayer': 'PySide6.QtMultimedia', 'QAudio': 'PySide6.QtMultimedia',
            # QtNetwork
            'QNetworkAccessManager': 'PySide6.QtNetwork', 'QNetworkRequest': 'PySide6.QtNetwork',
            # QtOpenGL
            'QOpenGLWidget': 'PySide6.QtOpenGLWidgets'
        }

    def visit_ImportFrom(self, node):
        if node.module and node.module.startswith('PySide2'):
            logging.info(f"Removing import from {node.module}")
            return None  # Remove PySide2 imports entirely
        return node

    def visit_Name(self, node):
        # Collect all used symbols in the code
        if isinstance(node.ctx, ast.Load):
            self.used_symbols.add(node.id)
        return node

    def add_imports(self, tree):
        """
        Add the correct PySide6 imports based on the used symbols.
        """
        imports_to_add = {}
        for symbol in self.used_symbols:
            if symbol in self.symbol_to_module:
                module = self.symbol_to_module[symbol]
                if module not in imports_to_add:
                    imports_to_add[module] = []
                imports_to_add[module].append(symbol)

        # Combine imports from the same module into one line
        final_imports = []
        for module, symbols in imports_to_add.items():
            symbols = list(set(symbols))  # Remove duplicates
            final_imports.append(ast.ImportFrom(module=module, names=[ast.alias(name=sym, asname=None) for sym in symbols], level=0))
            logging.info(f"Consolidated import: from {module} import {symbols}")

        tree.body = final_imports + [node for node in tree.body if not isinstance(node, ast.ImportFrom) or not node.module.startswith('PySide2')]
        return tree


def normalize_code(code):
    """
    Normalize code by removing extra spaces, blank lines, and indentation differences.
    """
    return re.sub(r'\s+', ' ', code).strip()


def process_file(file_path: str):
    """
    Reads a file, parses the AST, converts PySide2 code to PySide6 code, and writes the updated code back.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # Parse the AST
        tree = ast.parse(source_code)
        converter = PySide2ToPySide6Converter()
        tree = converter.visit(tree)
        tree = converter.add_imports(tree)

        # Generate the updated source code using astor
        updated_code = astor.to_source(tree)

        # Normalize both input and output code for better comparison
        normalized_updated_code = normalize_code(updated_code)
        normalized_source_code = normalize_code(source_code)

        # Write back the updated code only if changes were made
        if normalized_updated_code != normalized_source_code:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(updated_code)
            logging.info(f"Conversion completed. The file '{file_path}' has been updated.")
        else:
            logging.info(f"No changes required for the file '{file_path}'.")

    except Exception as e:
        logging.error(f"An error occurred while processing '{file_path}': {e}")


def process_directory(directory: str, exclude_dirs: list):
    """
    Processes all .py files in the given directory and its subdirectories,
    excluding specified directories.
    """
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in exclude_dirs]

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                process_file(file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PySide2 code to PySide6.')
    parser.add_argument('directory', help='Directory to convert')
    parser.add_argument('--exclude', nargs='*', default=[], help='Directories to exclude from conversion')
    args = parser.parse_args()

    process_directory(args.directory, args.exclude)
