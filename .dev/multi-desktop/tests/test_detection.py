#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to demonstrate monitor/desktop detection and window enumeration.
"""

import sys
import json
import subprocess
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from multi_desktop_capture import MultiDesktopCapture


def parse_ps_json_output(output: str):
    """Parse JSON from PowerShell output, skipping non-JSON lines."""
    lines = output.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('{'):
            return json.loads(line)
    raise ValueError("No JSON found in PowerShell output")


def test_monitor_detection():
    """Test monitor detection and counting."""
    print("\n" + "=" * 70)
    print("TEST 1: Monitor & Virtual Desktop Detection")
    print("=" * 70)

    script_path = Path(__file__).parent.parent / "powershell" / "detect_monitors_and_desktops.ps1"

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return

    # Find PowerShell
    ps_paths = [
        "powershell.exe",
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
    ]

    ps_exe = None
    for path in ps_paths:
        try:
            result = subprocess.run([path, "-Command", "echo test"],
                                  capture_output=True, timeout=1)
            if result.returncode == 0:
                ps_exe = path
                break
        except:
            continue

    if not ps_exe:
        print("❌ PowerShell not found")
        return

    print(f"\n✓ Using PowerShell: {ps_exe}")
    print(f"✓ Running: {script_path.name}")

    # Execute detection script
    cmd = [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(script_path)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout.strip():
        try:
            data = parse_ps_json_output(result.stdout)
        except ValueError as e:
            print(f"❌ Failed to parse JSON: {e}")
            print(f"Output: {result.stdout[:500]}")
            return None

        # Display monitor information
        monitors = data.get("Monitors", {})
        print(f"\n📺 MONITORS: {monitors.get('Count', 0)} detected")
        print(f"   Primary: {monitors.get('PrimaryMonitor', 'Unknown')}")

        for idx, monitor in enumerate(monitors.get("Details", [])):
            bounds = monitor.get("Bounds", {})
            print(f"\n   Monitor {idx + 1}: {monitor.get('DeviceName')}")
            print(f"      Resolution: {bounds.get('Width')}x{bounds.get('Height')}")
            print(f"      Position: ({bounds.get('X')}, {bounds.get('Y')})")
            print(f"      Primary: {monitor.get('IsPrimary')}")
            print(f"      BitsPerPixel: {monitor.get('BitsPerPixel')}")

        # Display virtual desktop information
        vd = data.get("VirtualDesktops", {})
        print(f"\n🖥️  VIRTUAL DESKTOPS:")
        print(f"   Supported: {vd.get('Supported', False)}")
        print(f"   Estimated Count: {vd.get('EstimatedCount', 1)}")
        print(f"   Note: {vd.get('Note', '')}")

        # Display window information
        windows = data.get("Windows", {})
        print(f"\n🪟 VISIBLE WINDOWS: {windows.get('VisibleCount', 0)}")
        print(f"   Total Enumerated: {windows.get('TotalEnumerated', 0)}")

        # Show first 10 windows
        window_details = windows.get("Details", [])
        if window_details:
            print(f"\n   Top 10 Windows:")
            for idx, window in enumerate(window_details[:10]):
                print(f"      {idx + 1}. [{window.get('ProcessName')}] {window.get('Title')[:50]}")
                print(f"         Handle: {window.get('Handle')} | PID: {window.get('ProcessId')}")

        print(f"\n✓ Detection completed at: {data.get('Timestamp')}")

        return data
    else:
        print(f"\n❌ Detection failed")
        if result.stderr:
            print(f"Error: {result.stderr}")
        return None


def test_window_capture():
    """Test selective window capture."""
    print("\n" + "=" * 70)
    print("TEST 2: Selective Window Capture")
    print("=" * 70)

    # First, get window list
    detection_data = test_monitor_detection()

    if not detection_data:
        print("❌ Cannot test window capture without detection data")
        return

    windows = detection_data.get("Windows", {}).get("Details", [])

    if not windows:
        print("❌ No windows available for capture")
        return

    # Try to capture the first window
    first_window = windows[0]
    window_handle = first_window.get("Handle")
    window_title = first_window.get("Title")

    print(f"\n📸 Attempting to capture window:")
    print(f"   Title: {window_title}")
    print(f"   Handle: {window_handle}")

    script_path = Path(__file__).parent.parent / "powershell" / "capture_window_by_handle.ps1"

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return

    # Find PowerShell
    ps_exe = None
    ps_paths = [
        "powershell.exe",
        "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe",
    ]

    for path in ps_paths:
        try:
            result = subprocess.run([path, "-Command", "echo test"],
                                  capture_output=True, timeout=1)
            if result.returncode == 0:
                ps_exe = path
                break
        except:
            continue

    if not ps_exe:
        print("❌ PowerShell not found")
        return

    # Execute capture script
    cmd = [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", str(script_path),
           "-WindowHandle", str(window_handle)]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

    if result.returncode == 0 and result.stdout.strip():
        try:
            data = parse_ps_json_output(result.stdout)
        except ValueError as e:
            print(f"❌ Failed to parse JSON: {e}")
            return

        if data.get("Success"):
            print(f"\n✓ Window captured successfully!")
            print(f"   Dimensions: {data.get('Width')}x{data.get('Height')}")
            print(f"   Base64 size: {len(data.get('Base64Data', ''))} bytes")

            # Optionally save to file
            output_dir = Path.home() / ".cache" / "sccpt" / "multi-desktop" / "tests"
            output_dir.mkdir(parents=True, exist_ok=True)

            import base64
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            process_name = first_window.get("ProcessName", "unknown")
            filename = f"window_capture_{timestamp}_{process_name}.jpg"
            filepath = output_dir / filename

            img_data = base64.b64decode(data.get("Base64Data"))

            # Convert to JPEG
            try:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_data))
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                img.save(str(filepath), 'JPEG', quality=85, optimize=True)
                print(f"   Saved to: {filepath}")
            except ImportError:
                filepath = filepath.with_suffix('.png')
                with open(filepath, 'wb') as f:
                    f.write(img_data)
                print(f"   Saved to: {filepath} (PNG)")

        else:
            print(f"\n❌ Capture failed: {data.get('Error')}")
    else:
        print(f"\n❌ Capture script failed")
        if result.stderr:
            print(f"Error: {result.stderr}")


def test_multi_desktop_capture():
    """Test full multi-desktop capture."""
    print("\n" + "=" * 70)
    print("TEST 3: Full Multi-Desktop Capture")
    print("=" * 70)

    capture = MultiDesktopCapture(verbose=True)

    # Enumerate
    desktops = capture.enumerate_desktops()

    # Capture all
    paths = capture.capture_all_desktops()

    if paths:
        print(f"\n✓ Captured {len(paths)} screenshots")
        for path in paths:
            print(f"   • {path}")
    else:
        print("\n❌ No screenshots captured")


def main():
    """Run all tests."""
    print("=" * 70)
    print("SCCPT Multi-Desktop Feature Test Suite")
    print("=" * 70)

    # Test 1: Detection
    test_monitor_detection()

    # Test 2: Window capture
    test_window_capture()

    # Test 3: Multi-desktop capture
    test_multi_desktop_capture()

    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
