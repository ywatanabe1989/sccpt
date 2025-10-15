#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-08-24 19:05:21 (ywatanabe)"
# File: /home/ywatanabe/proj/sccpt/__main__.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./__main__.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
import sys

from .cpt import main

if __name__ == "__main__":
    sys.exit(main())

# EOF
