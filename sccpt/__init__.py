#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCCPT - Screen Capture for Python
A lightweight, cross-platform screen capture library optimized for WSL and Windows.

Features:
- Windows host screen capture from WSL
- JPEG compression for smaller file sizes  
- Continuous monitoring with configurable intervals
- Human-readable timestamps
- Thread-safe operation

Usage:
    import sccpt
    
    # Single screenshot
    sccpt.capture("debug message")
    
    # Continuous monitoring
    sccpt.start()
    # ... do work ...
    sccpt.stop()
"""

from .utils import (
    capture,
    start_monitor, 
    stop_monitor
)
from .gif import (
    create_gif_from_session,
    create_gif_from_files,
    create_gif_from_pattern,
    create_gif_from_latest_session
)

# Convenience aliases - these are the main public API
cpt = capture      # Short alias for quick typing
start = start_monitor
stop = stop_monitor

__version__ = "0.1.0"
__author__ = "Yusuke Watanabe"
__email__ = "Yusuke.Watanabe@scitex.ai"

# Only expose the essential functions
__all__ = [
    "capture",
    "cpt",
    "start",
    "stop",
    "create_gif_from_session",
    "create_gif_from_files", 
    "create_gif_from_pattern",
    "create_gif_from_latest_session"
]