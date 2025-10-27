"""
Plugin Loader for Blender MCP
Dynamically loads MCP tools from plugins directory.
"""

import os
import importlib.util
from pathlib import Path
from typing import Optional

class PluginLoader:
    """
    Loads MCP tool plugins from a directory.
    Plugins are Python files in plugins/ directory that register @mcp.tool() decorators.
    """

    def __init__(self, plugin_dir: str = "plugins"):
        self.dir = Path(plugin_dir)
        self.dir.mkdir(exist_ok=True)

    def load_all(self, mcp_instance=None):
        """
        Load all plugins from the plugin directory.
        If mcp_instance is provided, plugins can access it for tool registration.
        """
        for file in self.dir.glob("*.py"):
            if file.stem.startswith("__"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                module = importlib.util.module_from_spec(spec)
                # Make mcp instance available to plugins if needed
                if mcp_instance:
                    module.mcp = mcp_instance
                spec.loader.exec_module(module)
                print(f"Loaded plugin: {file.name}")
            except Exception as e:
                print(f"Failed loading plugin {file.name}: {e}")