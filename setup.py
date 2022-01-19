#!/usr/bin/env python

from setuptools import setup

import version


# TESTS_REQUIRES = [
#     str(r.req)
#     for r in parse_requirements("requirements/dev.txt", session=PipSession())
# ]


def readme():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="drf_orjson_renderer",
    version=version.__version__,
    description="Django RestFramework JSON Renderer Backed by orjson",
    long_description_content_type="text/markdown",
    long_description=readme(),
    author="brianjbuck",
    author_email="brian@thebuckpasser.com",
    url="https://github.com/brianjbuck/drf_orjson_renderer",
    packages=["drf_orjson_renderer"],
    license="MIT",
    install_requires=[
        "django>=3.2,<=4.0",
        "djangorestframework",
        "orjson>=3.3.0",
    ],
    python_requires=">=3.6.0",
    zip_safe=True,
    keywords=["drf_orjson_renderer", "rest_framework", "orjson"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
