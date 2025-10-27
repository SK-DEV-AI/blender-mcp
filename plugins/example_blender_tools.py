"""
Example Blender Tools Plugin
Demonstrates how to add custom MCP tools for Blender operations.
"""

# This plugin can access the mcp instance if needed
# mcp = globals().get('mcp')  # Available if passed by loader

# Example: Custom hover animation tool
# @mcp.tool()  # Uncomment when mcp is available
def create_hover_animation(obj_name: str, height: float = 2.0, duration: int = 60) -> str:
    """
    Create a hover animation for a Blender object.

    Parameters:
    - obj_name: Name of the object to animate
    - height: Hover height in units
    - duration: Animation duration in frames
    """
    # This would call execute_blender_code or direct bpy operations
    # For now, just return a placeholder
    return f"Hover animation created for '{obj_name}' (height: {height}, duration: {duration})"

# Example: Custom lighting setup tool
# @mcp.tool()  # Uncomment when mcp is available
def setup_studio_lighting() -> str:
    """
    Set up three-point studio lighting in the scene.
    """
    # This would call execute_blender_code with lighting setup code
    return "Studio lighting setup complete"

print("Example Blender tools plugin loaded")