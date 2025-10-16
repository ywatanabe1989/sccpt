# MCP Server

This directory contains the Model Context Protocol (MCP) server for the CAM project.

## Available Server

### FastMCP Server (`mcp_server_fastmcp.py`)
- **Framework**: FastMCP 2.0
- **Features**: 
  - Modern FastMCP framework with Pythonic decorators
  - Comprehensive screenshot capture and monitoring tools
  - Resource-based screenshot access
  - Built-in testing support
  - Easy deployment options

## Running the Server

```bash
# Run via FastMCP CLI (recommended)
fastmcp run mcp_servers/mcp_server_fastmcp.py

# Or directly with Python
python mcp_servers/mcp_server_fastmcp.py
```

## Available Tools

The server provides the following functionality:

1. **capture_screenshot** - Take single screenshots
2. **start_monitoring** - Begin continuous screenshot monitoring
3. **stop_monitoring** - Stop monitoring session
4. **get_monitoring_status** - Check monitoring status and cache info
5. **analyze_screenshot** - Analyze screenshots for error indicators
6. **list_recent_screenshots** - List cached screenshots
7. **clear_cache** - Manage screenshot cache
8. **create_gif** - Create animated GIFs from sessions
9. **list_sessions** - List available monitoring sessions

## Resources

- **screenshot://{filename}** - Access individual screenshots
- **screenshots://recent** - Get list of recent screenshots

## Testing

Tests are available for the MCP server:

```bash
# Run all tests (includes MCP server tests)
./run_pytests.sh

# Or run MCP server tests specifically
pytest tests/test_mcp_server.py -v
```

## Configuration

Configure the server in your MCP client (e.g., Claude Desktop) by adding to the MCP configuration file:

```json
{
  "mcpServers": {
    "cam": {
      "command": "fastmcp",
      "args": ["run", "/path/to/mcp_servers/mcp_server_fastmcp.py"]
    }
  }
}
```

## Development

For extending the MCP server:

1. Follow the FastMCP patterns in `mcp_server_fastmcp.py`
2. Add tests in `tests/test_mcp_server.py`
3. Update this README with new functionality