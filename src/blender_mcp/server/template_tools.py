"""
Template Tools for Blender MCP
MCP tools for managing and applying Blender operation templates.
"""

from .connection import mcp, get_blender_connection, logger
from .template_engine import TemplateManager, deep_merge
import time
from typing import List, Dict, Optional, Any
from mcp.server.fastmcp.exceptions import ToolError

# Global template manager instance
template_manager = TemplateManager(repo_path="templates_repo")

@mcp.tool()
def list_templates(include_versions: bool = False) -> List[Dict[str, Any]]:
    """
    List all saved template names, optionally with version history.

    Parameters:
    - include_versions: Include Git version history if available
    """
    logger.info("Tool: list_templates called")
    try:
        return template_manager.list_templates(include_versions)
    except Exception as e:
        logger.error(f"list_templates error: {e}")
        raise ToolError(f"Failed to list templates: {e}")

@mcp.tool()
def create_template(name: str, config: Dict[str, Any]) -> str:
    """
    Create or update a template with given JSON data.

    Parameters:
    - name: Template name (used as filename)
    - config: Template configuration (JSON structure with actions, tags, etc.)
    """
    logger.info(f"Tool: create_template called: {name}")
    try:
        return template_manager.save_template(name, config)
    except Exception as e:
        logger.error(f"create_template error: {e}")
        raise ToolError(f"Failed to create template '{name}': {e}")

@mcp.tool()
def apply_template(name: str, overrides: Optional[Dict[str, Any]] = None) -> str:
    """
    Apply the template named 'name', with optional overrides.
    Executes the actions defined in the template.

    Parameters:
    - name: Template name to apply
    - overrides: Optional parameter overrides (deep-merged into template)
    """
    logger.info(f"Tool: apply_template called: {name}")
    start = time.time()
    try:
        data = template_manager.load_template(name)
        if overrides:
            data = deep_merge(data, overrides)
        # Execute actions (call other MCP tools)
        for step in data.get("actions", []):
            tool_name = step.get("tool")
            params = step.get("params", {})
            logger.info(f"Applying step tool={tool_name} params={params}")
            try:
                mcp.call_tool(tool_name, **params)
            except Exception as inner_e:
                logger.error(f"Error during step {tool_name}: {inner_e}")
                raise ToolError(f"Error calling tool '{tool_name}' with params {params}: {inner_e}")
        duration = time.time() - start
        template_manager._log_usage(name, duration, True)
        return f"Applied template '{name}' successfully (time: {duration:.2f}s)."
    except Exception as e:
        duration = time.time() - start
        template_manager._log_usage(name, duration, False)
        logger.error(f"apply_template failed: {e}")
        raise ToolError(f"Failed to apply template '{name}': {e}")

@mcp.tool()
def search_templates(tags: List[str]) -> List[str]:
    """
    Search templates by tags for quick discovery.

    Parameters:
    - tags: List of tags to search for (template must have all specified tags)
    """
    logger.info(f"Tool: search_templates called tags={tags}")
    try:
        return template_manager.search_templates(tags)
    except Exception as e:
        logger.error(f"search_templates error: {e}")
        raise ToolError(f"Failed to search templates: {e}")

@mcp.tool()
def get_template_stats(name: Optional[str] = None) -> Dict[str, Any]:
    """
    Get usage analytics for a template or all templates.

    Parameters:
    - name: Optional template name (returns stats for all if None)
    """
    logger.info(f"Tool: get_template_stats called name={name}")
    try:
        return template_manager.get_stats(name)
    except Exception as e:
        logger.error(f"get_template_stats error: {e}")
        raise ToolError(f"Failed to get template stats: {e}")

@mcp.tool()
def modify_template(name: str, changes: Dict[str, Any], save: bool = False) -> Dict[str, Any]:
    """
    Modify a template with changes, optionally saving.

    Parameters:
    - name: Template name to modify
    - changes: Changes to apply (deep-merged)
    - save: Whether to save the modified template
    """
    logger.info(f"Tool: modify_template called: {name}, save={save}")
    try:
        return template_manager.modify_template(name, changes, save)
    except Exception as e:
        logger.error(f"modify_template error: {e}")
        raise ToolError(f"Failed to modify template '{name}': {e}")

@mcp.tool()
def delete_template(name: str) -> str:
    """
    Delete a template.

    Parameters:
    - name: Template name to delete
    """
    logger.info(f"Tool: delete_template called: {name}")
    try:
        return template_manager.delete_template(name)
    except Exception as e:
        logger.error(f"delete_template error: {e}")
        raise ToolError(f"Failed to delete template '{name}': {e}")