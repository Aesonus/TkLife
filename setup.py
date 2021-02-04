from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tklife",
    version="0.4.1",
    author="Cory Laughlin",
    author_email="corylcomposinger@gmail.com",
    description="""Contains some basic classes and convenience functions and methods
for Tkinter Applications""",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aesonus/TkLife",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)