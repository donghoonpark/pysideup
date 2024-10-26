import ast
import argparse
import logging
import os
import astor
import re

from mappings import qtcore_mapping, qtgui_mapping, qtwidgets_mapping

# Set up logging
logging.basicConfig(level=logging.INFO)

class PySide2ToPySide6Converter(ast.NodeTransformer):
    def __init__(self):
        self.used_symbols = set()
        self.symbol_to_module = {**qtcore_mapping, **qtgui_mapping, **qtwidgets_mapping}

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

    def visit_Call(self, node):
        # Update exec_() to exec() for PySide6 compatibility
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'exec_':
            node.func.attr = 'exec'
            logging.info(f"Updated exec_() to exec() at line {node.lineno}")
        return self.generic_visit(node)

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
