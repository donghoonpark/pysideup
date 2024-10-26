from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pysideup",
    version="1.0.0",
    author="DongHoon Park",
    author_email="donghun94@gmail.com",
    description="A tool for converting PySide2 code to PySide6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DongHoonPark/pysideup",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "astor",
    ],
    entry_points={
        'console_scripts': [
            'pysideup=converter:main',
        ],
    },
    include_package_data=True,
)
