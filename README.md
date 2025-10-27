# Blender MCP (Model Context Protocol)

A Blender addon that enables AI assistants (like Claude) to interact with Blender through the Model Context Protocol (MCP).

## Installation

### 1. Install the Blender Addon

1. Download or clone this repository
2. Copy the entire `src/blender_mcp/addon/` directory to your Blender addons folder:
   - **Windows**: `%APPDATA%\Blender Foundation\Blender\4.x\scripts\addons\`
   - **macOS**: `~/Library/Application Support/Blender/4.x/scripts/addons/`
   - **Linux**: `~/.config/blender/4.x/scripts/addons/`

3. Rename the copied directory from `addon` to `blender_mcp`

4. Open Blender and go to `Edit > Preferences > Add-ons`
5. Search for "Blender MCP" and enable the addon

### 2. Install the MCP Server

The MCP server runs outside Blender and communicates with it via sockets.

1. Install Python dependencies:
   ```bash
   pip install mcp-server-fastmcp
   ```

2. Or if using the provided virtual environment:
   ```bash
   # Activate the virtual environment
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   ```

### 3. Configure Your MCP Client

Add the Blender MCP server to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp.server"],
      "env": {
        "BLENDER_HOST": "localhost",
        "BLENDER_PORT": "9876"
      }
    }
  }
}
```

## Usage

1. **Start Blender** and enable the Blender MCP addon
2. **Start your MCP client** (Claude Desktop, etc.) with the server configured
3. **In Blender**, click the "Connect to MCP server" button in the BlenderMCP panel (N-panel > BlenderMCP)
4. **Use Claude** to interact with Blender through natural language commands

## Features

### Core Tools
- **Scene Information**: Get details about objects, materials, and scene structure
- **Object Manipulation**: Query and modify 3D objects
- **Viewport Screenshots**: Capture Blender's 3D viewport
- **Code Execution**: Run Python code directly in Blender

### Template Engine
- **Template Management**: Create, save, and reuse complex operations
- **Dynamic Overrides**: Apply templates with parameter modifications
- **Template Search**: Discover templates by tags and categories
- **Usage Analytics**: Track template performance and success rates
- **Version Control**: Optional Git versioning for template evolution

### Asset Integrations
- **PolyHaven**: Download HDRIs, textures, and 3D models
- **Sketchfab**: Search and download 3D models
- **Hyper3D Rodin**: Generate 3D models from text or images

## Configuration

### Blender Addon Settings
- **Port**: Socket port for communication (default: 9876)
- **PolyHaven**: Enable/disable PolyHaven integration
- **Hyper3D**: Configure API keys and modes
- **Sketchfab**: Configure API key for model downloads

### Environment Variables
- `BLENDER_HOST`: Host address (default: localhost)
- `BLENDER_PORT`: Port number (default: 9876)

## Architecture

The system consists of two main components:

1. **Blender Addon** (`src/blender_mcp/addon/`): Runs inside Blender, handles UI and executes Blender operations
2. **MCP Server** (`src/blender_mcp/server/`): Runs outside Blender, provides MCP tools and manages communication

## Development

### Project Structure
```
src/blender_mcp/
├── addon/              # Blender addon code
│   ├── handlers.py     # Base command handlers
│   ├── polyhaven_handlers.py  # PolyHaven integration
│   ├── hyper3d_handlers.py    # Hyper3D integration
│   ├── sketchfab_handlers.py  # Sketchfab integration
│   ├── ui.py           # Blender UI components
│   ├── server.py       # Socket server for addon
│   └── __main__.py     # Addon registration
└── server/             # MCP server code
    ├── connection.py   # MCP server and socket client
    ├── tools.py        # Core Blender tools
    ├── integrations.py # Integration tools
    ├── template_engine.py     # Template storage and management
    ├── template_tools.py      # MCP tools for templates
    ├── prompts.py      # MCP prompts
    └── __main__.py     # Server entry point
templates/              # Template storage directory
├── template_name.json  # Template definitions
└── analytics.json      # Usage statistics
```

### Running Tests
```bash
# Test server modules
python -m pytest tests/

# Or manually test imports
python -c "from src.blender_mcp.server.connection import mcp; print('OK')"
```

## Troubleshooting

### Connection Issues
- Ensure the Blender addon is enabled and running
- Check that the port numbers match between client and server
- Verify firewall settings allow socket connections

### Integration Issues
- Check API keys are properly configured in Blender
- Ensure internet connectivity for external services
- Review Blender console for error messages

### Performance
- Large scenes may take time to process
- Asset downloads depend on internet speed
- 3D generation can take several minutes

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See LICENSE file for details.
