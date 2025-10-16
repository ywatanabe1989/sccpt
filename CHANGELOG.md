# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-10-17

### Fixed
- **URL capture now runs in truly headless mode** - Playwright no longer opens visible browser windows that interfere with user work
- Fixed layout corruption in URL screenshots by properly controlling viewport size
- Added DISPLAY environment variable handling for WSL environments to prevent visible browser launches
- Improved timeout handling for URL capture (30s page load + configurable wait time)

### Added
- `url_width` and `url_height` parameters for URL capture viewport control (default: 1920x1080)
- Stealth browser arguments for better rendering quality

### Changed
- Playwright is now the primary method for URL capture (headless)
- PowerShell method remains as fallback for Windows host URLs

## [0.2.0] - 2025-10-17

### Added
- Renamed project from `screenshot-capture` to `cam`
- Multi-desktop support for capturing all monitors
- Enhanced MCP server with comprehensive screenshot tools
- URL capture via browser (Playwright)
- App-specific window capture
- GIF creation from monitoring sessions

### Changed
- Simplified API with intuitive aliases (`snap`, `start`, `stop`)
- Improved error handling and user feedback
- Better cache management

## [0.1.0] - Initial Release

- Basic screenshot capture functionality
- WSL and Windows support
- Continuous monitoring
