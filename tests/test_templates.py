"""
Unit tests for Blender MCP Template Engine
Run with: python -m pytest tests/test_templates.py
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.blender_mcp.server.template_engine import TemplateManager, deep_merge


class TestTemplateManager:
    """Test TemplateManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = TemplateManager(templates_dir=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_load_template(self):
        """Test saving and loading a template."""
        test_data = {"tags": ["test"], "actions": [{"tool": "test_tool", "params": {"param1": "value1"}}]}
        result = self.manager.save_template("test_template", test_data)
        assert "saved" in result.lower()

        loaded = self.manager.load_template("test_template")
        assert loaded == test_data

    def test_list_templates(self):
        """Test listing templates."""
        self.manager.save_template("template1", {"tags": ["tag1"]})
        self.manager.save_template("template2", {"tags": ["tag2"]})

        templates = self.manager.list_templates()
        names = [t["name"] for t in templates]
        assert "template1" in names
        assert "template2" in names

    def test_search_templates(self):
        """Test searching templates by tags."""
        self.manager.save_template("anim_template", {"tags": ["animation", "test"]})
        self.manager.save_template("light_template", {"tags": ["lighting", "test"]})

        results = self.manager.search_templates(["animation"])
        assert "anim_template" in results
        assert "light_template" not in results

    def test_modify_template(self):
        """Test modifying templates."""
        original = {"tags": ["original"], "value": 1}
        self.manager.save_template("modify_test", original)

        changes = {"tags": ["modified"], "new_value": 2}
        modified = self.manager.modify_template("modify_test", changes, save=False)

        expected = {"tags": ["modified"], "value": 1, "new_value": 2}
        assert modified == expected

        # Original should still be unchanged
        loaded = self.manager.load_template("modify_test")
        assert loaded == original

    def test_delete_template(self):
        """Test deleting templates."""
        self.manager.save_template("delete_test", {"test": "data"})
        result = self.manager.delete_template("delete_test")
        assert "deleted" in result.lower()

        with pytest.raises(FileNotFoundError):
            self.manager.load_template("delete_test")


class TestDeepMerge:
    """Test deep_merge utility function."""

    def test_simple_merge(self):
        """Test basic dictionary merging."""
        a = {"key1": "value1", "key2": "original"}
        b = {"key2": "updated", "key3": "new"}
        result = deep_merge(a, b)

        expected = {"key1": "value1", "key2": "updated", "key3": "new"}
        assert result == expected

    def test_nested_merge(self):
        """Test nested dictionary merging."""
        a = {"nested": {"inner1": "a", "inner2": "b"}}
        b = {"nested": {"inner2": "updated", "inner3": "new"}}
        result = deep_merge(a, b)

        expected = {"nested": {"inner1": "a", "inner2": "updated", "inner3": "new"}}
        assert result == expected

    def test_non_dict_values(self):
        """Test merging with non-dict values."""
        a = {"key": "original"}
        b = {"key": ["list", "value"]}
        result = deep_merge(a, b)

        assert result["key"] == ["list", "value"]

    def test_empty_inputs(self):
        """Test merging with empty dictionaries."""
        result = deep_merge({}, {"key": "value"})
        assert result == {"key": "value"}

        result = deep_merge({"key": "value"}, {})
        assert result == {"key": "value"}


if __name__ == "__main__":
    pytest.main([__file__])