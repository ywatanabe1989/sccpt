#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-17 03:19:30 (ywatanabe)"
# File: /home/ywatanabe/proj/cam/src/cam/cli.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./src/cam/cli.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
CLI for cam - AI's Camera
"""

import argparse
import sys


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="cam - AI's Camera: Capture screenshots from anywhere",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m cam                        # Capture current screen
  python -m cam --all                  # Capture all monitors
  python -m cam --app chrome           # Capture Chrome window
  python -m cam --url 127.0.0.1:8000   # Capture URL
  python -m cam --monitor 1            # Capture monitor 1
  python -m cam --list                 # List available windows

  python -m cam --start                # Start monitoring
  python -m cam --stop                 # Stop monitoring
  python -m cam --gif                  # Create GIF from session
  python -m cam --mcp                  # Start MCP server
        """,
    )

    # Capture options
    parser.add_argument(
        "message", nargs="?", help="Optional message for filename"
    )
    parser.add_argument(
        "--all", action="store_true", help="Capture all monitors"
    )
    parser.add_argument(
        "--app", type=str, help="App name to capture (e.g., chrome)"
    )
    parser.add_argument(
        "--url", type=str, help="URL to capture (e.g., 127.0.0.1:8000)"
    )
    parser.add_argument(
        "--monitor", type=int, default=0, help="Monitor ID (0-based)"
    )
    parser.add_argument(
        "--quality", type=int, default=85, help="JPEG quality (1-100)"
    )
    parser.add_argument("-o", "--output", type=str, help="Output path")

    # Actions
    parser.add_argument(
        "--list", action="store_true", help="List available windows"
    )
    parser.add_argument(
        "--info", action="store_true", help="Show display info"
    )
    parser.add_argument(
        "--start", action="store_true", help="Start monitoring"
    )
    parser.add_argument("--stop", action="store_true", help="Stop monitoring")
    parser.add_argument(
        "--gif", action="store_true", help="Create GIF from latest session"
    )
    parser.add_argument("--mcp", action="store_true", help="Start MCP server")

    # Options
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Monitoring interval in seconds",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode"
    )

    args = parser.parse_args()

    # Import cam after parsing to avoid import overhead for --help
    import cam

    verbose = not args.quiet

    try:
        # Handle actions
        if args.list:
            info = cam.get_info()
            windows = info.get("Windows", {}).get("Details", [])
            print(f"\n📱 Visible Windows ({len(windows)}):")
            print("=" * 60)
            for i, win in enumerate(windows, 1):
                print(f"{i}. [{win['ProcessName']}] {win['Title']}")
                print(f"   Handle: {win['Handle']} | PID: {win['ProcessId']}")
            return 0

        elif args.info:
            info = cam.get_info()
            monitors = info.get("Monitors", {})
            windows = info.get("Windows", {})
            vd = info.get("VirtualDesktops", {})

            print("\n🖥️  Display Information")
            print("=" * 60)
            print(f"\n📺 Monitors: {monitors.get('Count')}")
            print(f"   Primary: {monitors.get('PrimaryMonitor')}")

            for i, mon in enumerate(monitors.get("Details", [])):
                bounds = mon.get("Bounds", {})
                print(f"\n   Monitor {i}:")
                print(f"     Device: {mon.get('DeviceName')}")
                print(
                    f"     Resolution: {bounds.get('Width')}x{bounds.get('Height')}"
                )
                print(f"     Primary: {mon.get('IsPrimary')}")

            print(f"\n🪟 Windows: {windows.get('VisibleCount')}")
            print(
                f"   On current virtual desktop: {len(windows.get('Details', []))}"
            )

            print(f"\n🖥️  Virtual Desktops:")
            print(f"   Supported: {vd.get('Supported')}")
            print(f"   Note: {vd.get('Note')}")

            return 0

        elif args.start:
            print(f"📸 Starting monitoring (interval: {args.interval}s)...")
            cam.start(
                interval=args.interval,
                verbose=verbose,
                monitor_id=args.monitor,
                all=args.all,
            )
            print(
                "✅ Monitoring started. Press Ctrl+C to stop, or run: python -m cam --stop"
            )
            print(f"📁 Saving to: ~/.cache/cam/")

            # Keep running
            try:
                import time

                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                cam.stop()
                print("\n✅ Monitoring stopped")

            return 0

        elif args.stop:
            cam.stop()
            print("✅ Monitoring stopped")
            return 0

        elif args.gif:
            print("📹 Creating GIF from latest session...")
            path = cam.gif()
            if path:
                print(f"✅ GIF created: {path}")
                return 0
            else:
                print("❌ No session found")
                return 1

        elif args.mcp:
            print("🤖 Starting cam MCP server...")
            print("Add to Claude Code settings:")
            print("{")
            print('  "mcpServers": {')
            print('    "cam": {')
            print('      "command": "python",')
            print('      "args": ["-m", "cam", "--mcp"]')
            print("    }")
            print("  }")
            print("}")
            print()

            # Start MCP server
            import asyncio
            from pathlib import Path

            mcp_server_path = (
                Path(__file__).parent.parent.parent / "mcp_server_cam.py"
            )

            # Import and run MCP server
            sys.path.insert(0, str(mcp_server_path.parent))
            import mcp_server_cam

            asyncio.run(mcp_server_cam.main())
            return 0

        # Default: capture screenshot
        else:
            path = cam.snap(
                message=args.message,
                path=args.output,
                quality=args.quality,
                monitor_id=args.monitor,
                all=args.all,
                app=args.app,
                url=args.url,
                verbose=verbose,
            )

            if path:
                if not args.quiet:
                    print(f"✅ {path}")
                return 0
            else:
                print("❌ Screenshot failed")
                return 1

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

# EOF
