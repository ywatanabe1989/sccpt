#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Entry point for python -m cammy
"""

import sys

# Import from src/cammy/cli.py
from src.cammy.cli import main

if __name__ == "__main__":
    sys.exit(main())

