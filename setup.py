#!/usr/bin/env python
import os

from setuptools import find_packages, setup


def get_version():
    with open(os.path.join(os.path.dirname(__file__), "version.py")) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip("\"'")


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="drf_orjson_renderer",
    version=get_version(),
    description="Django RestFramework JSON Renderer Backed by orjson",
    long_description_content_type="text/markdown",
    long_description=readme(),
    author="brianjbuck",
    author_email="brian@thebuckpasser.com",
    url="https://github.com/brianjbuck/drf_orjson_renderer",
    packages=find_packages(),
    py_modules=["version"],
    license="MIT",
    install_requires=[
        "django>=3.2",
        "djangorestframework",
        "orjson>=3.3.0",
    ],
    python_requires=">=3.9",
    zip_safe=True,
    keywords=["drf_orjson_renderer", "rest_framework", "orjson"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
