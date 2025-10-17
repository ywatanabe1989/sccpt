# Multi-Desktop Screenshot Capture

Experimental feature for capturing screenshots across multiple monitors and virtual desktops.

## Features

### 1. Monitor Detection & Counting
- Enumerate all physical monitors
- Detect monitor resolution, position, and DPI
- Identify primary monitor
- Count total monitors

### 2. Virtual Desktop Detection
- Detect virtual desktop support (Windows 10/11)
- Enumerate visible windows across desktops
- Get window handles and process information

### 3. Selective Window Capture
- Capture specific application windows by handle
- Enumerate all visible windows
- Filter by process name or title
- Capture individual apps without full screen

### 4. Multi-Desktop Capture
- Capture all monitors simultaneously
- Save each monitor/desktop separately
- Support for both WSL→Windows and native Linux
- Automatic JPEG compression

## Architecture

```
┌─────────────────────────────────────────────┐
│           Capture Scope Hierarchy            │
├─────────────────────────────────────────────┤
│ Level 1: Window    → Individual app window  │
│ Level 2: Monitor   → Physical monitor       │
│ Level 3: Desktop   → Virtual desktop        │
│ Level 4: All       → All monitors/desktops  │
└─────────────────────────────────────────────┘
```

## Usage

### Basic Detection

```python
from multi_desktop_capture import MultiDesktopCapture

# Initialize
capture = MultiDesktopCapture(verbose=True)

# Detect monitors and virtual desktops
info = capture.enumerate_desktops()
print(f"Monitors: {info['Monitors']['Count']}")
print(f"Virtual Desktops: {info['VirtualDesktops']['EstimatedCount']}")
print(f"Visible Windows: {info['Windows']['VisibleCount']}")
```

### Capture All Desktops

```python
# Capture all monitors/desktops at once
paths = capture.capture_all_desktops()

# Results saved to ~/.cache/sccpt/multi-desktop/
for path in paths:
    print(f"Saved: {path}")
```

### Selective Window Capture

```python
# Get list of windows
info = capture.enumerate_desktops()
windows = info['Windows']['Details']

# Capture specific window by handle
from selective_capture import capture_window_by_handle

window_handle = windows[0]['Handle']
screenshot = capture_window_by_handle(window_handle)
```

## PowerShell Scripts

### 1. `detect_monitors_and_desktops.ps1`
Returns JSON with:
- Monitor count, resolution, position
- Virtual desktop support status
- Visible window list with handles

### 2. `capture_all_desktops.ps1`
Captures all monitors and returns base64-encoded images in JSON.

### 3. `capture_window_by_handle.ps1`
Captures a specific window by its handle using `PrintWindow` API.

### 4. `enumerate_virtual_desktops.ps1`
Enumerates all visible windows (proxy for virtual desktop detection).

## Testing

Run the test suite:

```bash
cd .dev/multi-desktop/tests
python test_detection.py
```

This will:
1. Detect and count monitors
2. List virtual desktops
3. Enumerate all visible windows
4. Capture a sample window
5. Perform full multi-desktop capture

## Output Structure

```
~/.cache/sccpt/multi-desktop/
├── 20251017_123456_desktop_00_primary_DISPLAY1.jpg
├── 20251017_123456_desktop_01_DISPLAY2.jpg
└── tests/
    └── window_capture_20251017_123456_chrome.jpg
```

## Platform Support

| Platform | Monitors | Virtual Desktops | Window Capture |
|----------|----------|------------------|----------------|
| WSL→Windows | ✅ Full | ⚠️ Limited* | ✅ Full |
| Linux (X11) | ✅ Full | ✅ Full (wmctrl) | ✅ Full |
| Linux (Wayland) | ⚠️ Limited | ❌ | ❌ |

*Windows does not officially expose Virtual Desktop API via PowerShell. Detection uses window enumeration as a proxy.

## Requirements

### Windows (via WSL)
- PowerShell access from WSL
- .NET Framework (already installed on Windows)

### Linux
- `wmctrl` for virtual desktop enumeration
- `scrot` or `import` for screenshots
- X11 display server

## Integration with sccpt

This feature can be integrated into the main sccpt library by:

1. Adding `capture_scope` parameter to `sccpt.cpt()`:
   ```python
   sccpt.cpt(scope="window")    # Single window
   sccpt.cpt(scope="monitor")   # Single monitor (current)
   sccpt.cpt(scope="desktop")   # Current virtual desktop
   sccpt.cpt(scope="all")       # All monitors/desktops
   ```

2. Adding window selection to `sccpt.start()`:
   ```python
   sccpt.start(window_handle=12345)  # Monitor specific window
   ```

3. Adding MCP tools for AI assistants:
   - `enumerate_windows` - List all visible windows
   - `capture_window` - Capture specific window
   - `capture_all_monitors` - Capture all monitors

## Known Limitations

1. **Virtual Desktop Detection (Windows)**: Windows 10/11 does not expose the Virtual Desktop API through PowerShell. We use visible window enumeration as a proxy.

2. **Wayland Support**: Wayland has security restrictions that prevent screenshot capture in many scenarios.

3. **Window Capture Limitations**: Some applications (e.g., games with DirectX exclusive fullscreen) may not capture correctly using `PrintWindow` API.

## Future Enhancements

- [ ] True virtual desktop detection using Windows COM API
- [ ] Real-time window change detection
- [ ] Window focus-aware capture
- [ ] Support for multi-monitor window spanning
- [ ] Integration with sccpt monitoring mode
- [ ] MCP server tools for AI-driven capture
