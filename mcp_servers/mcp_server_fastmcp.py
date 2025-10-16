#!/usr/bin/env python3
"""
FastMCP Server for CAM - Screen Capture for Python
Provides screenshot capture capabilities via Model Context Protocol using FastMCP.
"""

from fastmcp import FastMCP, Context
from pathlib import Path
import base64
from datetime import datetime
import asyncio
import cam


mcp = FastMCP("cam-server")


@mcp.tool()
def capture_screenshot(
    message: str = None,
    monitor_id: int = 0,
    capture_all: bool = False,
    quality: int = 85,
    return_base64: bool = False
) -> dict:
    """
    Capture a single screenshot with optional message and categorization.
    
    Args:
        message: Optional message to include in filename
        monitor_id: Monitor number (0-based, default: 0 for primary monitor)
        capture_all: Capture all monitors combined into single image (overrides monitor_id)
        quality: JPEG quality (1-100, default: 85)
        return_base64: Return screenshot as base64 string
    
    Returns:
        Dictionary with success status, path, and optionally base64 data
    """
    try:
        path = cam.capture(
            message=message,
            path=None,
            quality=quality,
            auto_categorize=True,
            verbose=False,
            monitor_id=monitor_id,
            capture_all=capture_all,
            max_cache_gb=1.0
        )
        
        if not path:
            return {
                "success": False,
                "error": "Failed to capture screenshot"
            }
        
        category = "stderr" if "-stderr.jpg" in path else "stdout"
        
        result = {
            "success": True,
            "path": path,
            "category": category,
            "message": f"Screenshot saved to {path}",
            "timestamp": datetime.now().isoformat()
        }
        
        if return_base64 and path:
            with open(path, "rb") as f:
                result["base64"] = base64.b64encode(f.read()).decode()
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def start_monitoring(
    interval: float = 1.0,
    monitor_id: int = 0,
    capture_all: bool = False,
    output_dir: str = None,
    quality: int = 60,
    verbose: bool = True
) -> dict:
    """
    Start continuous screenshot monitoring at regular intervals.
    
    Args:
        interval: Seconds between captures (default: 1.0)
        monitor_id: Monitor number (0-based, default: 0 for primary monitor)
        capture_all: Capture all monitors combined into single image (overrides monitor_id)
        output_dir: Directory for screenshots (default: ~/.cache/cam)
        quality: JPEG quality (1-100, default: 60)
        verbose: Show capture messages
    
    Returns:
        Dictionary with success status and monitoring details
    """
    # Check if already monitoring (simplified - FastMCP doesn't have persistent state)
    cache_dir = Path.home() / ".cache" / "cam"
    monitoring_file = cache_dir / ".monitoring"
    
    if monitoring_file.exists():
        return {
            "success": False,
            "message": "Monitoring already active (detected existing .monitoring file)"
        }
    
    try:
        monitoring_worker = cam.start_monitor(
            output_dir=output_dir or "~/.cache/cam/",
            interval=interval,
            jpeg=True,
            quality=quality,
            on_capture=None,
            on_error=None,
            verbose=verbose,
            monitor_id=monitor_id,
            capture_all=capture_all
        )
        
        # Create monitoring marker file
        cache_dir.mkdir(parents=True, exist_ok=True)
        monitoring_file.write_text(f"started_{datetime.now().isoformat()}")
        
        return {
            "success": True,
            "message": f"Started monitoring with {interval}s interval on monitor {monitor_id}",
            "output_dir": output_dir or "~/.cache/cam/",
            "interval": interval,
            "monitor_id": monitor_id,
            "capture_all": capture_all,
            "quality": quality
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def stop_monitoring() -> dict:
    """
    Stop continuous screenshot monitoring.
    
    Returns:
        Dictionary with success status and final statistics
    """
    cache_dir = Path.home() / ".cache" / "cam"
    monitoring_file = cache_dir / ".monitoring"
    
    if not monitoring_file.exists():
        return {
            "success": False,
            "message": "Monitoring not active"
        }
    
    try:
        cam.stop()
        
        # Remove monitoring marker file
        monitoring_file.unlink()
        
        # Get stats
        screenshots = list(cache_dir.glob("*.jpg"))
        
        return {
            "success": True,
            "message": "Monitoring stopped",
            "screenshots_in_cache": len(screenshots)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def get_monitoring_status() -> dict:
    """
    Get current monitoring status and statistics.
    
    Returns:
        Dictionary with monitoring status and cache statistics
    """
    cache_dir = Path.home() / ".cache" / "cam"
    monitoring_file = cache_dir / ".monitoring"
    
    status = {
        "active": monitoring_file.exists(),
        "cache_dir": str(cache_dir)
    }
    
    # Get cache size
    if cache_dir.exists():
        screenshots = list(cache_dir.glob("*.jpg"))
        total_size = sum(f.stat().st_size for f in screenshots)
        status.update({
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "screenshot_count": len(screenshots)
        })
    
    return status


@mcp.tool()
def analyze_screenshot(path: str) -> dict:
    """
    Analyze a screenshot for error indicators (stdout/stderr categorization).
    
    Args:
        path: Path to screenshot to analyze
    
    Returns:
        Dictionary with analysis results
    """
    try:
        from cam.utils import _detect_category
        
        category = _detect_category(path)
        
        path_obj = Path(path)
        if not path_obj.exists():
            return {
                "success": False,
                "error": f"File not found: {path}"
            }
        
        return {
            "success": True,
            "path": path,
            "category": category,
            "is_error": category == "stderr",
            "size_kb": round(path_obj.stat().st_size / 1024, 2),
            "modified": datetime.fromtimestamp(path_obj.stat().st_mtime).isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_recent_screenshots(limit: int = 10, category: str = "all") -> dict:
    """
    List recent screenshots from cache.
    
    Args:
        limit: Maximum number of screenshots to list
        category: Filter by category (stdout/stderr/all)
    
    Returns:
        Dictionary with list of recent screenshots
    """
    try:
        cache_dir = Path.home() / ".cache" / "cam"
        if not cache_dir.exists():
            return {
                "success": True,
                "screenshots": [],
                "message": "Cache directory does not exist"
            }
        
        screenshots = list(cache_dir.glob("*.jpg"))
        
        # Filter by category if specified
        if category == "stdout":
            screenshots = [s for s in screenshots if "-stdout.jpg" in s.name]
        elif category == "stderr":
            screenshots = [s for s in screenshots if "-stderr.jpg" in s.name]
        
        # Sort by modification time (newest first)
        screenshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        screenshots = screenshots[:limit]
        
        result_list = []
        for screenshot in screenshots:
            cat = "stderr" if "-stderr.jpg" in screenshot.name else "stdout"
            result_list.append({
                "filename": screenshot.name,
                "path": str(screenshot),
                "category": cat,
                "size_kb": round(screenshot.stat().st_size / 1024, 2),
                "modified": datetime.fromtimestamp(screenshot.stat().st_mtime).isoformat()
            })
        
        return {
            "success": True,
            "screenshots": result_list,
            "count": len(result_list),
            "total_in_cache": len(list(cache_dir.glob("*.jpg")))
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def clear_cache(max_size_gb: float = 1.0, clear_all: bool = False) -> dict:
    """
    Clear screenshot cache or manage cache size.
    
    Args:
        max_size_gb: Keep cache under this size in GB (removes oldest files)
        clear_all: Remove all cached screenshots
    
    Returns:
        Dictionary with cleanup results
    """
    try:
        cache_dir = Path.home() / ".cache" / "cam"
        if not cache_dir.exists():
            return {
                "success": True,
                "message": "Cache directory does not exist"
            }
        
        if clear_all:
            removed = 0
            for screenshot in cache_dir.glob("*.jpg"):
                try:
                    screenshot.unlink()
                    removed += 1
                except:
                    pass
            
            return {
                "success": True,
                "message": f"Removed {removed} screenshots",
                "removed_count": removed
            }
        else:
            from cam.utils import _manage_cache_size
            
            _manage_cache_size(cache_dir, max_size_gb)
            
            # Get new cache size
            total_size = sum(f.stat().st_size for f in cache_dir.glob("*.jpg"))
            
            return {
                "success": True,
                "message": f"Cache managed to stay under {max_size_gb}GB",
                "cache_size_mb": round(total_size / (1024 * 1024), 2),
                "max_size_gb": max_size_gb
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def create_gif(
    session_id: str = None,
    image_paths: list = None,
    pattern: str = None,
    output_path: str = None,
    duration: float = 0.5,
    optimize: bool = True,
    max_frames: int = None
) -> dict:
    """
    Create an animated GIF from screenshots to summarize sessions or workflows.
    
    Args:
        session_id: Session ID to create GIF from (use 'latest' for most recent)
        image_paths: List of image file paths to create GIF from
        pattern: Glob pattern for images to include
        output_path: Output GIF file path (auto-generated if not specified)
        duration: Duration per frame in seconds (default: 0.5)
        optimize: Optimize GIF for smaller file size
        max_frames: Maximum number of frames to include
    
    Returns:
        Dictionary with GIF creation results
    """
    try:
        from cam.gif import GifCreator
        
        creator = GifCreator()
        
        # Determine which creation method to use
        if session_id:
            if session_id == "latest":
                result_path = creator.create_gif_from_recent_session(
                    "~/.cache/cam",
                    duration,
                    optimize,
                    max_frames
                )
            else:
                result_path = creator.create_gif_from_session(
                    session_id,
                    output_path,
                    "~/.cache/cam",
                    duration,
                    optimize,
                    max_frames
                )
        elif image_paths:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"~/.cache/cam/custom_gif_{timestamp}.gif"
            
            result_path = creator.create_gif_from_files(
                image_paths,
                output_path,
                duration,
                optimize
            )
        elif pattern:
            result_path = creator.create_gif_from_pattern(
                pattern,
                output_path,
                duration,
                optimize,
                max_frames
            )
        else:
            return {
                "success": False,
                "error": "Must specify either session_id, image_paths, or pattern"
            }
        
        if result_path:
            path_obj = Path(result_path)
            file_size = path_obj.stat().st_size / 1024  # KB
            
            return {
                "success": True,
                "path": result_path,
                "size_kb": round(file_size, 2),
                "message": f"GIF created successfully: {result_path}",
                "duration_per_frame": duration,
                "optimized": optimize
            }
        else:
            return {
                "success": False,
                "error": "Failed to create GIF - no suitable images found"
            }
        
    except ImportError:
        return {
            "success": False,
            "error": "PIL (Pillow) is required for GIF creation. Install with: pip install Pillow"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.tool()
def list_sessions(limit: int = 10) -> dict:
    """
    List available monitoring sessions that can be converted to GIFs.
    
    Args:
        limit: Maximum number of sessions to list
    
    Returns:
        Dictionary with available sessions
    """
    try:
        from cam.gif import GifCreator
        
        creator = GifCreator()
        sessions = creator.get_recent_sessions("~/.cache/cam")
        sessions = sessions[:limit]
        
        session_details = []
        cache_dir = Path.home() / ".cache" / "cam"
        
        for session_id in sessions:
            jpg_files = list(cache_dir.glob(f"{session_id}_*.jpg"))
            png_files = list(cache_dir.glob(f"{session_id}_*.png"))
            
            if not jpg_files and not png_files:
                continue
                
            files = jpg_files + png_files
            files.sort()
            
            if files:
                first_file = files[0]
                last_file = files[-1]
                total_size = sum(f.stat().st_size for f in files)
                
                session_details.append({
                    "session_id": session_id,
                    "screenshot_count": len(files),
                    "first_screenshot": first_file.name,
                    "last_screenshot": last_file.name,
                    "total_size_kb": round(total_size / 1024, 2),
                    "start_time": datetime.fromtimestamp(first_file.stat().st_mtime).isoformat(),
                    "end_time": datetime.fromtimestamp(last_file.stat().st_mtime).isoformat()
                })
        
        return {
            "success": True,
            "sessions": session_details,
            "count": len(session_details),
            "message": f"Found {len(session_details)} monitoring sessions"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@mcp.resource("screenshot://{filename}")
def get_screenshot(filename: str) -> str:
    """
    Get a screenshot from cache by filename.
    
    Args:
        filename: The screenshot filename to retrieve
    
    Returns:
        Base64 encoded screenshot data
    """
    cache_dir = Path.home() / ".cache" / "cam"
    filepath = cache_dir / filename
    
    if not filepath.exists():
        raise ValueError(f"Screenshot not found: {filename}")
    
    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode()
    
    return content


@mcp.resource("screenshots://recent")
def list_screenshots_resource(limit: int = 20) -> str:
    """
    List recent screenshots as a resource.
    
    Args:
        limit: Maximum number of screenshots to return
    
    Returns:
        JSON string with screenshot metadata
    """
    import json
    
    cache_dir = Path.home() / ".cache" / "cam"
    if not cache_dir.exists():
        return json.dumps({"screenshots": [], "message": "Cache directory does not exist"})
    
    screenshots = list(cache_dir.glob("*.jpg"))
    screenshots.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    screenshots = screenshots[:limit]
    
    result = []
    for img_file in screenshots:
        category = "stderr" if "-stderr.jpg" in img_file.name else "stdout"
        mtime = datetime.fromtimestamp(img_file.stat().st_mtime)
        
        result.append({
            "filename": img_file.name,
            "category": category,
            "size_kb": round(img_file.stat().st_size / 1024, 2),
            "modified": mtime.isoformat(),
            "uri": f"screenshot://{img_file.name}"
        })
    
    return json.dumps({"screenshots": result, "count": len(result)})


if __name__ == "__main__":
    mcp.run()