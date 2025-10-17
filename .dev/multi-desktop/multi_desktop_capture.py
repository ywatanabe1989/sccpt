#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Desktop Screenshot Capture
Extends sccpt to capture from multiple virtual desktops/monitors simultaneously.
"""

import json
import subprocess
import base64
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
import sys
import os

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class MultiDesktopCapture:
    """Capture screenshots from multiple virtual desktops/monitors."""

    def __init__(self, output_dir: str = None, verbose: bool = True):
        """
        Initialize multi-desktop capture.

        Args:
            output_dir: Directory to save screenshots (defaults to ~/.cache/sccpt/multi-desktop)
            verbose: Enable verbose output
        """
        if output_dir is None:
            output_dir = Path.home() / ".cache" / "sccpt" / "multi-desktop"

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.verbose = verbose

        # Detect platform
        self.is_wsl = self._is_wsl()

        if self.verbose:
            platform = "WSL" if self.is_wsl else "Native Linux"
            print(f"🖥️  Multi-Desktop Capture initialized ({platform})")
            print(f"📁 Output: {self.output_dir}")

    def _is_wsl(self) -> bool:
        """Check if running in WSL."""
        return sys.platform == "linux" and "microsoft" in os.uname().release.lower()

    def enumerate_desktops(self) -> Dict:
        """
        Enumerate all available virtual desktops/monitors.

        Returns:
            Dictionary with desktop information
        """
        if self.verbose:
            print("\n🔍 Enumerating virtual desktops...")

        if self.is_wsl:
            return self._enumerate_windows_desktops()
        else:
            return self._enumerate_linux_desktops()

    def _enumerate_windows_desktops(self) -> Dict:
        """Enumerate Windows virtual desktops via PowerShell."""
        try:
            script_path = Path(__file__).parent / "powershell" / "enumerate_virtual_desktops.ps1"

            if not script_path.exists():
                if self.verbose:
                    print(f"⚠️  PowerShell script not found: {script_path}")
                return {"error": "Script not found"}

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
                if self.verbose:
                    print("❌ PowerShell not found")
                return {"error": "PowerShell not found"}

            # Execute enumeration script
            cmd = [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass",
                   "-File", str(script_path)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())
                if self.verbose:
                    print(f"✓ Found {data.get('TotalWindows', 0)} windows")
                return data
            else:
                if self.verbose:
                    print(f"❌ Enumeration failed: {result.stderr}")
                return {"error": result.stderr}

        except Exception as e:
            if self.verbose:
                print(f"❌ Error enumerating desktops: {e}")
            return {"error": str(e)}

    def _enumerate_linux_desktops(self) -> Dict:
        """Enumerate Linux virtual desktops."""
        try:
            # Try wmctrl first
            result = subprocess.run(["wmctrl", "-d"], capture_output=True, text=True, timeout=2)

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                desktops = []
                for line in lines:
                    parts = line.split(None, 9)
                    if len(parts) >= 2:
                        desktops.append({
                            "id": parts[0],
                            "name": parts[-1] if len(parts) > 2 else f"Desktop {parts[0]}"
                        })

                if self.verbose:
                    print(f"✓ Found {len(desktops)} virtual desktops")

                return {
                    "TotalDesktops": len(desktops),
                    "Desktops": desktops,
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        except FileNotFoundError:
            if self.verbose:
                print("⚠️  wmctrl not installed")
        except Exception as e:
            if self.verbose:
                print(f"❌ Error: {e}")

        return {"error": "Unable to enumerate desktops"}

    def capture_all_desktops(self, session_id: str = None) -> List[str]:
        """
        Capture screenshots from all virtual desktops/monitors.

        Args:
            session_id: Optional session identifier for grouping captures

        Returns:
            List of paths to captured screenshots
        """
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.verbose:
            print(f"\n📸 Starting multi-desktop capture (session: {session_id})")

        if self.is_wsl:
            return self._capture_windows_all_desktops(session_id)
        else:
            return self._capture_linux_all_desktops(session_id)

    def _capture_windows_all_desktops(self, session_id: str) -> List[str]:
        """Capture all Windows monitors/desktops."""
        try:
            script_path = Path(__file__).parent / "powershell" / "capture_all_desktops.ps1"

            if not script_path.exists():
                if self.verbose:
                    print(f"⚠️  PowerShell script not found: {script_path}")
                return []

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
                if self.verbose:
                    print("❌ PowerShell not found")
                return []

            # Execute capture script
            cmd = [ps_exe, "-NoProfile", "-ExecutionPolicy", "Bypass",
                   "-File", str(script_path)]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0 and result.stdout.strip():
                data = json.loads(result.stdout.strip())

                saved_paths = []
                for idx, screen in enumerate(data.get("Screens", [])):
                    device_name = screen.get("DeviceName", f"screen_{idx}")
                    # Clean device name for filename
                    device_clean = device_name.replace("\\", "_").replace(".", "_")
                    is_primary = screen.get("IsPrimary", False)
                    primary_tag = "_primary" if is_primary else ""

                    filename = f"{session_id}_desktop_{idx:02d}{primary_tag}_{device_clean}.jpg"
                    filepath = self.output_dir / filename

                    # Decode and save base64 image
                    img_data = base64.b64decode(screen.get("Base64Data", ""))

                    # Convert PNG to JPEG with PIL
                    try:
                        from PIL import Image
                        import io
                        img = Image.open(io.BytesIO(img_data))
                        if img.mode == 'RGBA':
                            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                            rgb_img.paste(img, mask=img.split()[3])
                            img = rgb_img
                        img.save(str(filepath), 'JPEG', quality=85, optimize=True)
                    except ImportError:
                        # Fallback to PNG if PIL not available
                        filepath = filepath.with_suffix('.png')
                        with open(filepath, 'wb') as f:
                            f.write(img_data)

                    saved_paths.append(str(filepath))

                    if self.verbose:
                        bounds = screen.get("Bounds", {})
                        print(f"✓ Captured: {filename} ({bounds.get('Width')}x{bounds.get('Height')})")

                if self.verbose:
                    print(f"\n✓ Total captures: {len(saved_paths)}")

                return saved_paths
            else:
                if self.verbose:
                    print(f"❌ Capture failed: {result.stderr}")
                return []

        except Exception as e:
            if self.verbose:
                print(f"❌ Error capturing desktops: {e}")
                import traceback
                traceback.print_exc()
            return []

    def _capture_linux_all_desktops(self, session_id: str) -> List[str]:
        """Capture all Linux virtual desktops."""
        saved_paths = []

        try:
            # Get desktop info
            result = subprocess.run(["wmctrl", "-d"], capture_output=True, text=True, timeout=2)

            if result.returncode != 0:
                if self.verbose:
                    print("❌ wmctrl failed")
                return []

            lines = result.stdout.strip().split("\n")

            for line in lines:
                parts = line.split(None, 9)
                if len(parts) >= 2:
                    desktop_id = parts[0]
                    desktop_name = parts[-1] if len(parts) > 2 else f"Desktop_{desktop_id}"
                    desktop_name_clean = desktop_name.replace(" ", "_")

                    # Switch to desktop
                    subprocess.run(["wmctrl", "-s", desktop_id], timeout=1)

                    # Small delay for desktop switch
                    import time
                    time.sleep(0.2)

                    # Capture using scrot or import
                    filename = f"{session_id}_desktop_{desktop_id}_{desktop_name_clean}.jpg"
                    filepath = self.output_dir / filename

                    # Try scrot first
                    result = subprocess.run(["scrot", "-q", "85", str(filepath)],
                                          capture_output=True, timeout=5)

                    if result.returncode == 0 and filepath.exists():
                        saved_paths.append(str(filepath))
                        if self.verbose:
                            print(f"✓ Captured: {filename}")

            if self.verbose:
                print(f"\n✓ Total captures: {len(saved_paths)}")

            return saved_paths

        except Exception as e:
            if self.verbose:
                print(f"❌ Error capturing desktops: {e}")
            return saved_paths


def main():
    """Demo usage of multi-desktop capture."""
    print("=" * 60)
    print("Multi-Desktop Screenshot Capture - Demo")
    print("=" * 60)

    # Initialize
    capture = MultiDesktopCapture(verbose=True)

    # Enumerate desktops
    desktops = capture.enumerate_desktops()
    print(f"\n📊 Desktop Info:\n{json.dumps(desktops, indent=2)}")

    # Capture all
    paths = capture.capture_all_desktops()

    if paths:
        print("\n" + "=" * 60)
        print("✅ Multi-desktop capture completed!")
        print("=" * 60)
        print(f"\n📁 Saved {len(paths)} screenshots:")
        for path in paths:
            print(f"   • {path}")
    else:
        print("\n❌ No screenshots captured")


if __name__ == "__main__":
    main()
