from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, AsyncIterator
from pydantic import BaseModel, Field
from enum import Enum
from pathlib import Path
import importlib
import json
import asyncio
import sys
import traceback


class HookName(str, Enum):
    """Available plugin hooks"""
    FILE_CHANGED = "file_changed"
    FILE_SAVED = "file_saved"
    FILE_OPENED = "file_opened"
    FILE_CLOSED = "file_closed"
    CHAT_MESSAGE = "chat_message"
    CHAT_COMPLETION = "chat_completion"
    SETTINGS_CHANGED = "settings_changed"
    EDITOR_READY = "editor_ready"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    SESSION_CREATED = "session_created"
    SESSION_LOADED = "session_loaded"


class PluginManifest(BaseModel):
    """Plugin manifest describing metadata"""
    name: str
    version: str
    description: str
    author: str
    homepage: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    hooks: List[str] = Field(default_factory=list)
    routes: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class PluginContext(BaseModel):
    """Context passed to plugins containing app state"""
    app_root: Path
    plugins_dir: Path
    settings: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class Route(BaseModel):
    """Plugin route definition"""
    path: str
    method: str
    handler: str
    description: str = ""


class Plugin(ABC):
    """Abstract base class for plugins"""

    manifest: PluginManifest

    @abstractmethod
    async def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin with context"""
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        """Cleanup when plugin is unloaded"""
        pass

    async def on_hook(self, hook_name: HookName, **kwargs) -> Any:
        """Handle a hook - override in subclasses"""
        return None

    def get_routes(self) -> Optional[List[Route]]:
        """Return additional FastAPI routes if any"""
        return None

    def get_middlewares(self) -> List[Any]:
        """Return additional middlewares if any"""
        return []


class PluginManager:
    """Manages plugin lifecycle"""

    def __init__(self, plugins_dir: Path, context: PluginContext):
        self.plugins_dir = plugins_dir
        self.context = context
        self.plugins: Dict[str, Plugin] = {}
        self.enabled_plugins: set = set()
        self._hooks: Dict[HookName, List[Callable]] = {h: [] for h in HookName}
        self._route_hooks: List[Dict[str, Any]] = []
        self._middlewares: List[Any] = []

    def discover_plugins(self) -> List[PluginManifest]:
        """Discover available plugins by scanning for manifest.json files"""
        manifests = []
        if not self.plugins_dir.exists():
            return manifests

        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "manifest.json").exists():
                try:
                    with open(item / "manifest.json") as f:
                        data = json.load(f)
                        manifests.append(PluginManifest(**data))
                except Exception as e:
                    print(f"Error loading manifest for {item.name}: {e}")
        return manifests

    def _load_plugin_module(self, plugin_name: str) -> Optional[type]:
        """Load plugin class from plugin directory"""
        try:
            # Try to import from app.plugins.sample_plugins.{plugin_name}
            module_name = f"app.plugins.sample_plugins.{plugin_name}"
            if module_name not in sys.modules:
                module = importlib.import_module(module_name)
            else:
                module = sys.modules[module_name]

            # Find the Plugin subclass
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, Plugin) and attr != Plugin:
                    return attr
            return None
        except Exception as e:
            print(f"Error loading plugin module {plugin_name}: {e}")
            traceback.print_exc()
            return None

    async def load_plugin(self, plugin_name: str) -> bool:
        """Load and initialize a plugin"""
        if plugin_name in self.plugins:
            return True

        plugin_path = self.plugins_dir / plugin_name
        manifest_path = plugin_path / "manifest.json"

        if not manifest_path.exists():
            print(f"Plugin {plugin_name} not found at {manifest_path}")
            return False

        try:
            # Load manifest
            with open(manifest_path) as f:
                manifest_data = json.load(f)
                manifest = PluginManifest(**manifest_data)

            # Load plugin class
            plugin_class = self._load_plugin_module(plugin_name)
            if plugin_class is None:
                print(f"Could not find Plugin class in {plugin_name}")
                return False

            # Instantiate and initialize
            plugin = plugin_class()
            plugin.manifest = manifest
            await plugin.initialize(self.context)

            self.plugins[plugin_name] = plugin
            self.enabled_plugins.add(plugin_name)

            # Register hooks
            for hook_name_str in manifest.hooks:
                try:
                    hook_name = HookName(hook_name_str)
                    self._hooks[hook_name].append(
                        lambda h=hook_name, p=plugin: p.on_hook(h)
                    )
                except ValueError:
                    print(f"Unknown hook name: {hook_name_str}")

            # Register routes
            routes = plugin.get_routes()
            if routes:
                for route in routes:
                    self._route_hooks.append({
                        "plugin": plugin_name,
                        "path": route.path,
                        "method": route.method,
                        "handler": route.handler
                    })

            # Register middlewares
            self._middlewares.extend(plugin.get_middlewares())

            print(f"Loaded plugin: {plugin_name}")
            return True

        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            traceback.print_exc()
            return False

    async def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        if plugin_name not in self.plugins:
            return False

        try:
            plugin = self.plugins[plugin_name]
            await plugin.shutdown()
            del self.plugins[plugin_name]
            self.enabled_plugins.discard(plugin_name)
            print(f"Unloaded plugin: {plugin_name}")
            return True
        except Exception as e:
            print(f"Error unloading plugin {plugin_name}: {e}")
            return False

    async def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a plugin"""
        await self.unload_plugin(plugin_name)
        return await self.load_plugin(plugin_name)

    def get_plugin_manifest(self, plugin_name: str) -> Optional[PluginManifest]:
        """Get manifest for a plugin"""
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].manifest
        return None

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all discovered plugins with status"""
        manifests = self.discover_plugins()
        result = []
        for m in manifests:
            result.append({
                "manifest": m,
                "enabled": m.name in self.enabled_plugins,
                "loaded": m.name in self.plugins
            })
        return result

    def get_routes(self) -> List[Dict[str, Any]]:
        """Get all plugin routes"""
        return self._route_hooks

    def get_middlewares(self) -> List[Any]:
        """Get all plugin middlewares"""
        return self._middlewares

    async def invoke_hook(self, hook_name: HookName, **kwargs) -> List[Any]:
        """Invoke all handlers for a hook"""
        results = []
        for handler in self._hooks.get(hook_name, []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(**kwargs)
                else:
                    result = handler(**kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook {hook_name} handler error: {e}")
                traceback.print_exc()
        return results

    async def load_all_plugins(self) -> None:
        """Discover and load all available plugins"""
        for manifest in self.discover_plugins():
            try:
                await self.load_plugin(manifest.name)
            except Exception as e:
                print(f"Failed to load plugin {manifest.name}: {e}")

    async def unload_all_plugins(self) -> None:
        """Unload all loaded plugins"""
        for plugin_name in list(self.enabled_plugins):
            try:
                await self.unload_plugin(plugin_name)
            except Exception as e:
                print(f"Error unloading plugin {plugin_name}: {e}")
