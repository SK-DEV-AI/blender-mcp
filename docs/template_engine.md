# Blender MCP Template Engine

The Template Engine extends Blender MCP with reusable templates for Blender operations, enabling LLMs to create, save, and apply complex animation and scene setups efficiently.

## Overview

Templates allow LLMs to:
- Save frequently used operations (lighting, animations, materials)
- Apply templates with parameter overrides
- Search and discover existing templates
- Track usage analytics
- Version templates with Git (optional)

## Template Structure

Templates are JSON files with the following structure:

```json
{
  "type": "animation|lighting|material|scene",
  "tags": ["tag1", "tag2"],
  "description": "Human-readable description",
  "actions": [
    {
      "tool": "tool_name",
      "params": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}
```

## MCP Tools

### Template Management

- `list_templates(include_versions=False)` - List all saved templates
- `create_template(name, config)` - Create or update a template
- `apply_template(name, overrides=None)` - Apply template with optional overrides
- `search_templates(tags)` - Search templates by tags
- `get_template_stats(name=None)` - Get usage analytics
- `modify_template(name, changes, save=False)` - Modify template in-memory or save
- `delete_template(name)` - Delete a template

## Usage Examples

### Creating a Template

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "create_template",
    "arguments": {
      "name": "phone_hover",
      "config": {
        "type": "animation",
        "tags": ["gadget", "hover"],
        "description": "Phone with hover animation",
        "actions": [
          {
            "tool": "execute_blender_code",
            "params": {
              "code": "import bpy\nobj = bpy.data.objects['Phone']\nobj.location.z += 1\nobj.keyframe_insert('location', frame=1)"
            }
          }
        ]
      }
    }
  }
}
```

### Applying with Overrides

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "apply_template",
    "arguments": {
      "name": "phone_hover",
      "overrides": {
        "actions": [
          {
            "params": {
              "code": "import bpy\nobj = bpy.data.objects['Phone']\nobj.location.z += 2\nobj.keyframe_insert('location', frame=1)"
            }
          }
        ]
      }
    }
  }
}
```

## Template Storage

Templates are stored as JSON files in the `templates/` directory:
- `templates/template_name.json` - Template definition
- `templates/analytics.json` - Usage statistics

Optional Git versioning in `templates_repo/` directory.

## Error Handling

All template operations include robust error handling with detailed error messages for LLM debugging:

- File not found errors
- JSON parsing errors
- Tool execution failures
- Git operation failures

Errors are logged to `mcp_server.log` and returned via MCP ToolError responses.

## Integration with Existing Tools

Templates can call any existing Blender MCP tools:
- `execute_blender_code` - Direct Python execution
- `search_sketchfab_models` - Asset discovery
- `download_sketchfab_model` - Asset import
- `get_scene_info` - Scene queries

## Analytics

Track template usage with success rates and performance metrics:
```json
{
  "template_name": {
    "uses": 5,
    "total_time": 12.34,
    "successes": 4,
    "success_rate": 0.8
  }
}
```

## Example Workflow

1. LLM searches for existing templates: `search_templates(["animation", "gadget"])`
2. If none found, creates new template: `create_template("phone_anim", {...})`
3. Applies template with customizations: `apply_template("phone_anim", overrides)`
4. Renders result using existing tools

This enables efficient reuse of complex operations while maintaining flexibility for customization.