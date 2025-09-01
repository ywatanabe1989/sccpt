#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for easy screen capture.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional
from .capture import ScreenshotWorker, CaptureManager

# Global manager instance
_manager = CaptureManager()


def _manage_cache_size(cache_dir: Path, max_size_gb: float = 1.0):
    """
    Manage cache directory size by removing old files if size exceeds limit.
    
    Parameters
    ----------
    cache_dir : Path
        Directory to manage
    max_size_gb : float
        Maximum size in GB (default: 1.0)
    """
    if not cache_dir.exists():
        return
    
    max_size_bytes = max_size_gb * 1024 * 1024 * 1024  # Convert GB to bytes
    
    # Get all files with their sizes and modification times
    files = []
    total_size = 0
    
    for file_path in cache_dir.glob("*.jpg"):
        if file_path.is_file():
            size = file_path.stat().st_size
            mtime = file_path.stat().st_mtime
            files.append((file_path, size, mtime))
            total_size += size
    
    # Also check PNG files
    for file_path in cache_dir.glob("*.png"):
        if file_path.is_file():
            size = file_path.stat().st_size
            mtime = file_path.stat().st_mtime
            files.append((file_path, size, mtime))
            total_size += size
    
    # If under limit, nothing to do
    if total_size <= max_size_bytes:
        return
    
    # Sort by modification time (oldest first)
    files.sort(key=lambda x: x[2])
    
    # Remove oldest files until under limit
    for file_path, size, _ in files:
        if total_size <= max_size_bytes:
            break
        try:
            file_path.unlink()
            total_size -= size
        except:
            pass  # File might be in use


def capture(message: str = None, path: str = None, quality: int = 85, auto_categorize: bool = True, verbose: bool = True, monitor_id: int = 0, capture_all: bool = False, max_cache_gb: float = 1.0) -> str:
    """
    Take a single screenshot with automatic categorization.
    
    Automatically detects if called from exception handler and categorizes as 'error'.
    
    Parameters
    ----------
    message : str, optional
        Message to include in filename or metadata
    path : str, optional
        Output path. Supports ~ and <timestamp> placeholders.
        Default: "~/.cache/sccpt/<timestamp>.jpg" (adds -error suffix if in exception)
    quality : int
        JPEG quality (1-100)
    auto_categorize : bool
        Automatically detect and categorize (error, warning, normal)
    monitor_id : int
        Monitor number to capture (0-based index, default: 0 for primary monitor)
    capture_all : bool
        If True, capture all monitors combined (default: False)
    max_cache_gb : float
        Maximum cache size in GB, old files removed if exceeded (default: 1.0)
    
    Returns
    -------
    str
        Path to saved screenshot
    
    Examples
    --------
    >>> import sccpt
    >>> 
    >>> # Normal usage
    >>> sccpt.cpt()  # Saves to ~/.cache/sccpt/normal/
    >>> 
    >>> # Automatic error detection
    >>> try:
    ...     risky_operation()
    ... except Exception as e:
    ...     sccpt.cpt()  # Automatically saves to ~/.cache/sccpt/error/
    """
    # Take screenshot first to analyze it
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    temp_dir = "/tmp/sccpt_temp"
    Path(temp_dir).mkdir(exist_ok=True)
    
    # Take screenshot to temp location
    use_jpeg = True if path is None or path.lower().endswith(('.jpg', '.jpeg')) else False
    worker = ScreenshotWorker(
        output_dir=temp_dir,
        use_jpeg=use_jpeg,
        jpeg_quality=quality,
        verbose=False
    )
    
    worker.session_id = "capture"
    worker.screenshot_count = 0
    worker.monitor = monitor_id
    worker.capture_all = capture_all
    temp_path = worker._take_screenshot()
    
    if not temp_path:
        return None
    
    # Detect category if auto_categorize enabled
    category = "stdout"
    if auto_categorize:
        # First check if we're in an exception context
        if _is_in_exception_context():
            category = "stderr"
            # Add exception info to message
            import traceback
            exc_info = traceback.format_exc(limit=3)
            if message:
                message = f"{message}\n{exc_info}"
            else:
                message = exc_info
        else:
            # Try visual detection
            category = _detect_category(temp_path)
    
    # Normalize message for filename
    normalized_msg = ""
    if message:
        # Remove special chars, keep only alphanumeric and spaces
        import re
        normalized = re.sub(r'[^\w\s-]', '', message.split('\n')[0])  # First line only
        normalized = re.sub(r'[-\s]+', '-', normalized).strip('-')
        normalized_msg = f"-{normalized[:50]}" if normalized else ""  # Limit length
    
    # Add category suffix
    category_suffix = f"-{category}"
    
    # Handle path with category and message
    if path is None:
        # Simplified: no subdirectories, stdout/stderr suffixes
        path = f"~/.cache/sccpt/<timestamp><message><category_suffix>.jpg"
    
    # Expand user home
    path = os.path.expanduser(path)
    
    # Replace placeholders
    if "<timestamp>" in path:
        path = path.replace("<timestamp>", timestamp)
    if "<message>" in path:
        path = path.replace("<message>", normalized_msg)
    if "<category_suffix>" in path:
        path = path.replace("<category_suffix>", category_suffix)
    
    # Ensure directory exists
    output_dir = Path(path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Move to final location
    final_path = Path(path)
    Path(temp_path).rename(final_path)
    
    # Add message with category as metadata
    if message or category != "stdout":
        metadata = f"[{category.upper()}] {message}" if message else f"[{category.upper()}]"
        _add_message_metadata(str(final_path), metadata)
    
    # Manage cache size (remove old files if needed)
    cache_dir = Path(os.path.expanduser("~/.cache/sccpt"))
    if cache_dir.exists():
        _manage_cache_size(cache_dir, max_cache_gb)
    
    # Print path for user feedback (useful in interactive sessions)
    final_path_str = str(final_path)
    if verbose:
        try:
            if category == "stderr":
                print(f"📸 stderr: {final_path_str}")
            else:
                print(f"📸 stdout: {final_path_str}")
        except:
            # In case print fails in some environments
            pass
    
    return final_path_str


def take_screenshot(output_path: str = None, 
                   jpeg: bool = True,
                   quality: int = 85) -> Optional[str]:
    """
    Take a single screenshot (simple interface).
    
    Parameters
    ----------
    output_path : str, optional
        Where to save the screenshot
    jpeg : bool
        Use JPEG format (True) or PNG (False)
    quality : int
        JPEG quality (1-100)
    
    Returns
    -------
    str or None
        Path to saved screenshot
    """
    return _manager.take_single_screenshot(output_path, jpeg, quality)


def start_monitor(output_dir: str = "~/.cache/sccpt/",
                 interval: float = 1.0,
                 jpeg: bool = True,
                 quality: int = 60,
                 on_capture=None,
                 on_error=None,
                 verbose: bool = True,
                 monitor_id: int = 0,
                 capture_all: bool = False) -> ScreenshotWorker:
    """
    Start continuous screenshot monitoring.
    
    Parameters
    ----------
    output_dir : str
        Directory for screenshots (default: ~/.cache/sccpt/)
    interval : float
        Seconds between captures
    jpeg : bool
        Use JPEG compression
    quality : int
        JPEG quality (1-100)
    on_capture : callable, optional
        Function called with filepath after each capture
    on_error : callable, optional
        Function called with exception on errors
    verbose : bool
        Print status messages
    monitor_id : int
        Monitor number to capture (0-based index, default: 0 for primary monitor)
    capture_all : bool
        If True, capture all monitors combined (default: False)
    
    Returns
    -------
    ScreenshotWorker
        The worker instance
    
    Examples
    --------
    >>> # Simple monitoring
    >>> sccpt.start()
    
    >>> # With event hooks
    >>> sccpt.start(
    ...     on_capture=lambda path: print(f"Saved: {path}"),
    ...     on_error=lambda e: logging.error(e)
    ... )
    
    >>> # Detect specific screen content
    >>> def check_error_dialog(path):
    ...     if "error" in analyze_image(path):
    ...         send_alert(f"Error detected: {path}")
    >>> sccpt.start(on_capture=check_error_dialog)
    """
    # Expand user home directory
    output_dir = os.path.expanduser(output_dir)
    
    return _manager.start_capture(
        output_dir=output_dir,
        interval=interval,
        jpeg=jpeg,
        quality=quality,
        on_capture=on_capture,
        on_error=on_error,
        verbose=verbose,
        monitor_id=monitor_id,
        capture_all=capture_all
    )


def stop_monitor():
    """Stop continuous screenshot monitoring."""
    _manager.stop_capture()


def _is_in_exception_context() -> bool:
    """
    Check if we're currently in an exception handler.
    """
    import sys
    # Check if there's an active exception
    exc_info = sys.exc_info()
    return exc_info[0] is not None


def _detect_category(filepath: str) -> str:
    """
    Detect screenshot category based on content.
    Simple heuristic based on common error indicators.
    """
    try:
        # Try OCR-based detection if available
        from PIL import Image
        img = Image.open(filepath)
        
        # Simple color-based heuristics
        # Red dominant = likely error
        # Yellow/orange dominant = likely warning
        pixels = img.convert('RGB').getdata()
        red_count = sum(1 for r, g, b in pixels if r > 200 and g < 100 and b < 100)
        yellow_count = sum(1 for r, g, b in pixels if r > 200 and g > 150 and b < 100)
        
        total_pixels = len(pixels)
        red_ratio = red_count / total_pixels if total_pixels > 0 else 0
        yellow_ratio = yellow_count / total_pixels if total_pixels > 0 else 0
        
        # Thresholds for detection
        if red_ratio > 0.05:  # More than 5% red pixels
            return "error"
        elif yellow_ratio > 0.05:  # More than 5% yellow pixels
            return "warning"
        
    except:
        pass
    
    # Check filename for common error keywords
    filename_lower = str(filepath).lower()
    if any(word in filename_lower for word in ['error', 'fail', 'exception', 'crash']):
        return "stderr"
    elif any(word in filename_lower for word in ['warn', 'alert', 'caution']):
        return "stderr"  # Warnings also go to stderr
    
    return "stdout"


def _add_message_metadata(filepath: str, message: str):
    """Add message as metadata to image file."""
    try:
        # Try to add EXIF comment using PIL
        from PIL import Image
        from PIL.ExifTags import TAGS
        
        img = Image.open(filepath)
        
        # Add comment to image metadata
        exif = img.getexif()
        exif[0x9286] = message  # UserComment EXIF tag
        
        # Save with metadata
        img.save(filepath, exif=exif)
    except:
        # If PIL not available, create companion text file
        text_path = Path(filepath).with_suffix('.txt')
        text_path.write_text(f"{datetime.now().isoformat()}: {message}\n")


# Convenience exports
__all__ = [
    "capture",
    "take_screenshot", 
    "start_monitor",
    "stop_monitor",
]