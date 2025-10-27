"""
Template Engine for Blender MCP
Provides reusable templates for Blender operations with versioning, analytics, and LLM-friendly error handling.
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Optional Git support
try:
    import git
    HAS_GIT = True
except ImportError:
    HAS_GIT = False
    git = None

logger = logging.getLogger("BlenderMCP.TemplateEngine")

class TemplateManager:
    """
    Manages Blender operation templates with JSON file storage, optional Git versioning,
    and usage analytics.
    """

    def __init__(self, templates_dir: str = "templates", repo_path: Optional[str] = None):
        self.dir = Path(templates_dir)
        self.dir.mkdir(exist_ok=True)
        self.repo = None
        # Use environment variable for repo path if not provided
        if repo_path is None:
            repo_path = os.getenv("TEMPLATES_REPO_PATH", "templates_repo")
        if repo_path and HAS_GIT:
            repo_full = Path(repo_path)
            if not (repo_full / ".git").exists():
                self.repo = git.Repo.init(repo_full)
            else:
                self.repo = git.Repo(repo_full)
            logger.info(f"Git repo initialized at {repo_path}")
        self.analytics_file = self.dir / "analytics.json"
        self.cache: Dict[str, Dict] = {}  # In-mem cache for performance

    def _path(self, name: str) -> Path:
        """Get the file path for a template."""
        return self.dir / f"{name}.json"

    def list_templates(self, include_versions: bool = False) -> List[Dict[str, Any]]:
        """List all saved templates with optional version history."""
        names = [f.stem for f in self.dir.glob("*.json") if f.name != "analytics.json"]
        out = [{"name": n} for n in names]
        if include_versions and self.repo:
            for entry in out:
                try:
                    commits = list(self.repo.iter_commits(paths=str(self._path(entry["name"])), max_count=10))
                    entry["versions"] = [{
                        "hex": c.hexsha[:8],
                        "msg": c.message.strip(),
                        "time": c.committed_datetime.isoformat()
                    } for c in commits]
                except Exception as e:
                    logger.warning(f"Version fetch error for {entry['name']}: {e}")
        return out

    def save_template(self, name: str, data: Dict[str, Any], commit_message: Optional[str] = None) -> str:
        """Save or update a template with JSON data."""
        path = self._path(name)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        self.cache[name] = data
        if self.repo:
            try:
                self.repo.index.add([str(path)])
                self.repo.index.commit(commit_message or f"Update template: {name}")
            except Exception as e:
                logger.warning(f"Git commit failed: {e}")
        # Add schema hints for better LLM usage
        if "tags" not in data:
            logger.info(f"Hint: Add 'tags' to template '{name}' for better search (e.g., ['animation', 'lighting'])")
        self._log_usage(name, 0.0, True)
        logger.info(f"Saved template '{name}' (type: {data.get('type', 'generic')})")
        return f"Template '{name}' saved."

    def load_template(self, name: str) -> Dict[str, Any]:
        """Load a template from file or cache."""
        if name in self.cache:
            return self.cache[name]
        path = self._path(name)
        if not path.exists():
            raise FileNotFoundError(f"Template '{name}' not found.")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.cache[name] = data
        return data

    def modify_template(self, name: str, changes: Dict[str, Any], save: bool = False) -> Dict[str, Any]:
        """Apply changes to a template in-memory, optionally saving."""
        template = self.load_template(name)
        merged = deep_merge(template, changes)
        if save:
            return self.save_template(name, merged, f"Modified: {name}")
        logger.info(f"Modified '{name}' in-memory (not saved)")
        return merged

    def delete_template(self, name: str) -> str:
        """Delete a template."""
        path = self._path(name)
        if path.exists():
            path.unlink()
            if self.repo:
                try:
                    self.repo.index.remove([str(path)], working_tree=True)
                    self.repo.index.commit(f"Delete template {name}")
                except Exception as e:
                    logger.warning(f"Git delete commit failed: {e}")
            return f"Template '{name}' deleted."
        else:
            raise FileNotFoundError(f"Template '{name}' not found.")

    def search_templates(self, tags: List[str]) -> List[str]:
        """Search templates by tags."""
        matches = []
        for entry in self.list_templates():
            try:
                data = self.load_template(entry["name"])
                t_tags = data.get("tags", [])
                if set(tags).issubset(set(t_tags)):
                    matches.append(entry["name"])
            except Exception as e:
                logger.error(f"Load error for {entry['name']}: {e}")
        return matches

    def _log_usage(self, name: str, duration: float, success: bool):
        """Log template usage for analytics."""
        stats = {}
        af = self.analytics_file
        if af.exists():
            try:
                with open(af, "r", encoding="utf-8") as f:
                    stats = json.load(f)
            except Exception:
                pass
        entry = stats.setdefault(name, {"uses": 0, "total_time": 0.0, "successes": 0})
        entry["uses"] += 1
        entry["total_time"] += duration
        if success:
            entry["successes"] += 1
        entry["success_rate"] = entry["successes"] / entry["uses"] if entry["uses"] > 0 else 0.0
        with open(af, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)

    def get_stats(self, name: Optional[str] = None) -> Dict[str, Any]:
        """Get usage analytics."""
        if self.analytics_file.exists():
            with open(self.analytics_file, "r", encoding="utf-8") as f:
                stats = json.load(f)
            return {name: stats.get(name, {})} if name else stats
        return {}


def deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge dictionary b into a, returning a new dict.
    Non-destructive to inputs.
    """
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out