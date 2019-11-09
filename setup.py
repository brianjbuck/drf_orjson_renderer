#!/usr/bin/env python

from pip._internal.download import PipSession
from pip._internal.req import parse_requirements
from setuptools import setup

import version


# TESTS_REQUIRES = [
#     str(r.req)
#     for r in parse_requirements("requirements/dev.txt", session=PipSession())
# ]


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="drf_orjson_renderer",
    version=version.__version__,
    # summary="Django Rest Framework ORJSON Renderer",
    # description_content_type="text/markdown; charset=UTF-8; variant=GFM",
    description=readme(),
    author="brianjbuck",
    author_email="brian@thebuckpasser.com",
    url="https://github.com/brianjbuck/drf-orjson-renderer",
    packages=["drf_orjson_renderer"],
    license="MIT",
    install_requires=["django", "djangorestframework", "orjson"],
    # tests_requires=TESTS_REQUIRES,
    python_requires=">=3.6.0",
    zip_safe=True,
    keywords=["drf_orjson_renderer", "rest_framework", "orjson"],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
)
