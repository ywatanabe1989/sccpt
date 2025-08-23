#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script for SCCPT - Screen Capture for Python
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = ""
if readme_path.exists():
    long_description = readme_path.read_text(encoding="utf-8")

setup(
    name="sccpt",
    version="0.1.0",
    author="Yusuke Watanabe",
    author_email="Yusuke.Watanabe@scitex.ai",
    description="Lightweight screen capture library optimized for WSL and Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ywatanabe/sccpt",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Core dependencies (minimal by default)
    ],
    extras_require={
        "full": [
            "mss>=6.0.0",  # For cross-platform screen capture
            "Pillow>=9.0.0",  # For image processing and JPEG support
        ],
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sccpt=sccpt.cli:main",
        ],
    },
    keywords="screenshot screen-capture wsl windows monitoring automation",
)