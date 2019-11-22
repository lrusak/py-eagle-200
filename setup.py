# SPDX-License-Identifier: GPL-2.0-only

import os

from setuptools import setup

from libeagle import __version__ as version

req_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
requirements = [line for line in open(req_file) if line]

desc_file = os.path.join(os.path.dirname(__file__), "README.md")
long_description = [line for line in open(desc_file) if line]

setup(
    name="py-eagle-200",
    version=version,
    author="Lukas Rusak",
    author_email="lorusak@gmail.com",
    url="https://rainforestautomation.com",
    description="A python wrapper library for the eagle-200 REST API.",
    long_description=long_description,
    license="GPLv2",
    packages=["libeagle"],
    package_dir={"libeagle": "libeagle"},
    install_requires=requirements,
    python_requires=">=3",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
    ],
)
