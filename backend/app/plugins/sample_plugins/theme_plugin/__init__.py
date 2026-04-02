from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.plugins.plugin_base import Plugin, PluginManifest, PluginContext, HookName, Route


class Theme(BaseModel):
    """Represents a color theme"""
    id: str
    name: str
    colors: Dict[str, str]


class ThemePlugin(Plugin):
    """Plugin that provides custom themes for the IDE"""

    manifest = PluginManifest(
        name="theme_plugin",
        version="1.0.0",
        description="Provides custom themes for the IDE",
        author="llama-ide Team",
        keywords=["theme", "customization", "appearance"],
        hooks=["startup"],
        routes=["/plugins/themes"],
        dependencies=[]
    )

    def __init__(self):
        self.themes: Dict[str, Theme] = {
            "midnight": Theme(
                id="midnight",
                name="Midnight",
                colors={
                    "bg": "#0d1117",
                    "fg": "#c9d1d9",
                    "accent": "#58a6ff",
                    "surface": "#161b22",
                    "border": "#30363d"
                }
            ),
            "ocean": Theme(
                id="ocean",
                name="Ocean",
                colors={
                    "bg": "#1a2332",
                    "fg": "#e6edf3",
                    "accent": "#3b82f6",
                    "surface": "#222d3d",
                    "border": "#3d4f6a"
                }
            ),
            "forest": Theme(
                id="forest",
                name="Forest",
                colors={
                    "bg": "#1a2f1a",
                    "fg": "#d4edda",
                    "accent": "#22c55e",
                    "surface": "#243324",
                    "border": "#3d5c3d"
                }
            ),
            "sunset": Theme(
                id="sunset",
                name="Sunset",
                colors={
                    "bg": "#2d1f1f",
                    "fg": "#f5e6e6",
                    "accent": "#f97316",
                    "surface": "#3d2a2a",
                    "border": "#5c3d3d"
                }
            ),
            "nordic": Theme(
                id="nordic",
                name="Nordic",
                colors={
                    "bg": "#2e3440",
                    "fg": "#eceff4",
                    "accent": "#88c0d0",
                    "surface": "#3b4252",
                    "border": "#4c566a"
                }
            )
        }
        self._context: Optional[PluginContext] = None

    async def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin"""
        self._context = context
        print(f"Initialized {self.manifest.name}")

    async def shutdown(self) -> None:
        """Cleanup when plugin is unloaded"""
        print(f"Shutting down {self.manifest.name}")

    def get_routes(self) -> List[Route]:
        """Return plugin routes"""
        return [
            Route(
                path="/plugins/themes",
                method="GET",
                handler="list_themes",
                description="List all available themes"
            ),
            Route(
                path="/plugins/themes/{theme_id}",
                method="GET",
                handler="get_theme",
                description="Get a specific theme by ID"
            )
        ]

    def list_themes(self) -> List[Theme]:
        """Handler for GET /plugins/themes"""
        return list(self.themes.values())

    def get_theme(self, theme_id: str) -> Theme:
        """Handler for GET /plugins/themes/{theme_id}"""
        if theme_id not in self.themes:
            raise ValueError(f"Unknown theme: {theme_id}")
        return self.themes[theme_id]
