import os
import json
import importlib.util
from typing import Dict, List
from .plugin_base import Plugin, PluginManifest, PluginContext


class PluginLoader:
    """Loads and manages individual plugins"""

    @staticmethod
    def load_plugin_from_directory(plugin_dir: str) -> Plugin:
        """Load a plugin from its directory"""
        # Load manifest
        manifest_path = os.path.join(plugin_dir, "manifest.json")
        if not os.path.exists(manifest_path):
            raise FileNotFoundError(f"Plugin manifest not found in {plugin_dir}")

        with open(manifest_path, 'r') as f:
            manifest_data = json.load(f)
            manifest = PluginManifest(**manifest_data)

        # Load plugin module
        plugin_module_path = os.path.join(plugin_dir, "__init__.py")
        if not os.path.exists(plugin_module_path):
            raise FileNotFoundError(f"Plugin __init__.py not found in {plugin_dir}")

        # Generate unique module name
        plugin_name = os.path.basename(plugin_dir)
        module_name = f"plugin_{plugin_name}_{manifest.name.replace('-', '_')}"

        spec = importlib.util.spec_from_file_location(module_name, plugin_module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Instantiate plugin
        if not hasattr(module, 'PluginImpl'):
            raise AttributeError(f"Plugin module missing PluginImpl class")

        return module.PluginImpl(manifest)
