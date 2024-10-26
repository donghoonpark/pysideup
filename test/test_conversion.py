import unittest
import tempfile
import os
import ast
from converter import process_file

class TestPySide2ToPySide6Conversion(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = os.path.join(self.test_dir.name, 'test_file.py')

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def write_test_file(self, content):
        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def read_test_file(self):
        with open(self.test_file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def ast_equal_ignore_import_order(self, code1, code2):
        tree1 = ast.parse(code1)
        tree2 = ast.parse(code2)

        # Extract import nodes for comparison
        def extract_import_nodes(tree):
            return [node for node in tree.body if isinstance(node, (ast.Import, ast.ImportFrom))]

        imports1 = extract_import_nodes(tree1)
        imports2 = extract_import_nodes(tree2)

        # Compare import nodes by ensuring they contain the same names and attributes, ignoring order
        imports1_dict = {}
        for node in imports1:
            module = node.module if isinstance(node, ast.ImportFrom) else None
            names = tuple(sorted(alias.name for alias in node.names))
            imports1_dict[(module, names)] = ast.dump(node)

        imports2_dict = {}
        for node in imports2:
            module = node.module if isinstance(node, ast.ImportFrom) else None
            names = tuple(sorted(alias.name for alias in node.names))
            imports2_dict[(module, names)] = ast.dump(node)

        # Compare only the keys of the import dictionaries
        if set(imports1_dict.keys()) != set(imports2_dict.keys()):
            return False

        # Extract non-import nodes for comparison
        def extract_non_import_nodes(tree):
            return [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]

        non_imports1 = extract_non_import_nodes(tree1)
        non_imports2 = extract_non_import_nodes(tree2)

        # Compare non-import nodes by their AST representation
        return ast.dump(ast.Module(body=non_imports1)) == ast.dump(ast.Module(body=non_imports2))

    def test_conversion(self):
        # Input PySide2 code
        input_code = """
from PySide2.QtWidgets import QWidget, QVBoxLayout
from PySide2.QtGui import QIcon

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowIcon(QIcon())
        """
        # Expected PySide6 code
        expected_output_code = """
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QIcon

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowIcon(QIcon())
        """

        # Write the input code to the test file
        self.write_test_file(input_code)

        # Run the conversion process on the test file
        process_file(self.test_file_path)

        # Read the converted code
        output_code = self.read_test_file()

        # Assert that the output code matches the expected output, ignoring import order
        self.assertTrue(self.ast_equal_ignore_import_order(output_code, expected_output_code))

    def test_conversion_with_qaction(self):
        # Input PySide2 code
        input_code = """
from PySide2.QtWidgets import QWidget, QVBoxLayout, QAction

class TestWidgetWithAction(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with QAction")
        layout = QVBoxLayout()
        self.setLayout(layout)
        action = QAction("Test Action", self)
        """
        # Expected PySide6 code
        expected_output_code = """
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QAction

class TestWidgetWithAction(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with QAction")
        layout = QVBoxLayout()
        self.setLayout(layout)
        action = QAction("Test Action", self)
        """

        # Write the input code to the test file
        self.write_test_file(input_code)

        # Run the conversion process on the test file
        process_file(self.test_file_path)

        # Read the converted code
        output_code = self.read_test_file()

        # Assert that the output code matches the expected output, ignoring import order
        self.assertTrue(self.ast_equal_ignore_import_order(output_code, expected_output_code))

    def test_conversion_with_wildcard_import(self):
        # Input PySide2 code with wildcard import
        input_code = """
from PySide2.QtWidgets import *

class TestWidgetWithWildcard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with Wildcard Import")
        layout = QVBoxLayout()
        self.setLayout(layout)
        """
        # Expected PySide6 code
        expected_output_code = """
from PySide6.QtWidgets import QWidget, QVBoxLayout

class TestWidgetWithWildcard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with Wildcard Import")
        layout = QVBoxLayout()
        self.setLayout(layout)
        """

        # Write the input code to the test file
        self.write_test_file(input_code)

        # Run the conversion process on the test file
        process_file(self.test_file_path)

        # Read the converted code
        output_code = self.read_test_file()

        # Assert that the output code matches the expected output, ignoring import order
        self.assertTrue(self.ast_equal_ignore_import_order(output_code, expected_output_code))

    def test_conversion_with_wildcard_and_qaction(self):
        # Input PySide2 code with wildcard import and QAction
        input_code = """
from PySide2.QtWidgets import *
from PySide2.QtWidgets import QAction

class TestWidgetWithWildcardAndAction(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with Wildcard and QAction")
        layout = QVBoxLayout()
        self.setLayout(layout)
        action = QAction("Test Action", self)
        """
        # Expected PySide6 code
        expected_output_code = """
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QAction

class TestWidgetWithWildcardAndAction(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with Wildcard and QAction")
        layout = QVBoxLayout()
        self.setLayout(layout)
        action = QAction("Test Action", self)
        """

        # Write the input code to the test file
        self.write_test_file(input_code)

        # Run the conversion process on the test file
        process_file(self.test_file_path)

        # Read the converted code
        output_code = self.read_test_file()

        # Assert that the output code matches the expected output, ignoring import order
        self.assertTrue(self.ast_equal_ignore_import_order(output_code, expected_output_code))

    def test_conversion_with_multiple_imports(self):
        # Input PySide2 code with multiple import statements for same module
        input_code = """
from PySide2.QtWidgets import QWidget
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtGui import QIcon

class TestWidgetWithMultipleImports(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with Multiple Imports")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowIcon(QIcon())
        """
        # Expected PySide6 code
        expected_output_code = """
from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtGui import QIcon

class TestWidgetWithMultipleImports(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test with Multiple Imports")
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowIcon(QIcon())
        """

        # Write the input code to the test file
        self.write_test_file(input_code)

        # Run the conversion process on the test file
        process_file(self.test_file_path)

        # Read the converted code
        output_code = self.read_test_file()

        # Assert that the output code matches the expected output, ignoring import order
        self.assertTrue(self.ast_equal_ignore_import_order(output_code, expected_output_code))

    def test_conversion_with_exec_method(self):
        # Input PySide2 code with exec_() method
        input_code = """
from PySide2.QtWidgets import QApplication

app = QApplication([])
app.exec_()
        """
        # Expected PySide6 code with exec() method
        expected_output_code = """
from PySide6.QtWidgets import QApplication

app = QApplication([])
app.exec()
        """

        # Write the input code to the test file
        self.write_test_file(input_code)

        # Run the conversion process on the test file
        process_file(self.test_file_path)

        # Read the converted code
        output_code = self.read_test_file()

        # Assert that the output code matches the expected output, ignoring import order
        self.assertTrue(self.ast_equal_ignore_import_order(output_code, expected_output_code))

if __name__ == '__main__':
    unittest.main()
