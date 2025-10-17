<!-- ---
!-- Timestamp: 2025-10-17 02:47:12
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/cammy/TODO.md
!-- --- -->

- [x] Get virtual desktops (✓ in `.dev/multi-desktop/`)
- [x] Get monitors (✓ in `.dev/multi-desktop/`)
- [x] Get visible apps (✓ in `.dev/multi-desktop/`)
- [ ] Capture URL pages like puppeteer (http://127.0.0.1:8000/ on Windows host)
  - Note: Already have `mcp__puppeteer__*` tools available
  - Can integrate with cammy for unified API
- [ ] Expose these functionalities as MCP server
  - Multi-monitor capture
  - Window enumeration
  - Selective window capture
  - Virtual desktop detection
- [ ] Save with readable name with rotating based on time or size
- [ ] Integrate `.dev/multi-desktop/` features into main cammy library
  - Add `scope` parameter: "window", "monitor", "desktop", "all"
  - Add `window_handle` parameter for selective capture
  - Update MCP server with new tools

- [ ] Rename cammy as cammy
  - [ ] Rename method names as well

<!-- EOF -->