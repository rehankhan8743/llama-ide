"""
Advanced Themes Plugin for Llama IDE
Provides additional theme customization options
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class ThemePlugin:
    """Plugin for advanced theme customization"""

    # Predefined custom themes
    THEMES = {
        "midnight": {
            "name": "Midnight",
            "background": "#0a0a0a",
            "foreground": "#e0e0e0",
            "accent": "#6b8dd6",
            "sidebar": "#121212",
            "terminal": "#0c0c0c",
            "comments": "#5a6370",
            "keywords": "#c678dd",
            "strings": "#98c379",
            "functions": "#61afef",
            "variables": "#e06c75",
        },
        "ocean": {
            "name": "Ocean",
            "background": "#1a2634",
            "foreground": "#d4d4d4",
            "accent": "#4fc1ff",
            "sidebar": "#1e2a36",
            "terminal": "#15202b",
            "comments": "#6a9955",
            "keywords": "#569cd6",
            "strings": "#ce9178",
            "functions": "#dcdcaa",
            "variables": "#9cdcfe",
        },
        "monokai_pro": {
            "name": "Monokai Pro",
            "background": "#2d2a2e",
            "foreground": "#fcfcfa",
            "accent": "#ffd866",
            "sidebar": "#363234",
            "terminal": "#221f22",
            "comments": "#727072",
            "keywords": "#ff6188",
            "strings": "#ffd866",
            "functions": "#a9dc76",
            "variables": "#78dce8",
        },
        "dracula": {
            "name": "Dracula",
            "background": "#282a36",
            "foreground": "#f8f8f2",
            "accent": "#bd93f9",
            "sidebar": "#44475a",
            "terminal": "#21222c",
            "comments": "#6272a4",
            "keywords": "#ff79c6",
            "strings": "#f1fa8c",
            "functions": "#50fa7b",
            "variables": "#8be9fd",
        },
        "solarized": {
            "name": "Solarized Dark",
            "background": "#002b36",
            "foreground": "#839496",
            "accent": "#268bd2",
            "sidebar": "#073642",
            "terminal": "#002028",
            "comments": "#586e75",
            "keywords": "#859900",
            "strings": "#2aa198",
            "functions": "#268bd2",
            "variables": "#b58900",
        },
        "gruvbox": {
            "name": "Gruvbox Dark",
            "background": "#282828",
            "foreground": "#ebdbb2",
            "accent": "#d79921",
            "sidebar": "#3c3836",
            "terminal": "#1d2021",
            "comments": "#928374",
            "keywords": "#fb4934",
            "strings": "#b8bb26",
            "functions": "#fabd2f",
            "variables": "#83a598",
        }
    }

    def __init__(self):
        self.active_theme = "midnight"
        self.custom_themes: Dict[str, Dict[str, str]] = {}
        self.data_file = Path("./plugins/advanced-themes/themes.json")
        self.data_file.parent.mkdir(exist_ok=True)
        self.load_custom_themes()

    def initialize(self, context: Any) -> None:
        """Initialize the plugin"""
        print("Advanced Themes plugin initialized")

    def on_theme_change(self, theme_name: str) -> Dict[str, Any]:
        """Handle theme change"""
        if theme_name in self.THEMES:
            self.active_theme = theme_name
            return self.get_theme_css(theme_name)
        elif theme_name in self.custom_themes:
            self.active_theme = theme_name
            return self.get_theme_css(theme_name)
        return {}

    def on_editor_mount(self) -> Dict[str, Any]:
        """Return editor configuration for current theme"""
        return {
            "theme": self.active_theme,
            "colors": self.get_theme_colors(self.active_theme)
        }

    def get_theme_colors(self, theme_name: str) -> Dict[str, str]:
        """Get color scheme for a theme"""
        if theme_name in self.THEMES:
            return self.THEMES[theme_name]
        elif theme_name in self.custom_themes:
            return self.custom_themes[theme_name]
        return self.THEMES["midnight"]

    def get_theme_css(self, theme_name: str) -> str:
        """Generate CSS for a theme"""
        colors = self.get_theme_colors(theme_name)
        return f"""
:root {{
    --theme-bg: {colors['background']};
    --theme-fg: {colors['foreground']};
    --theme-accent: {colors['accent']};
    --theme-sidebar: {colors['sidebar']};
    --theme-terminal: {colors['terminal']};
    --theme-comments: {colors['comments']};
    --theme-keywords: {colors['keywords']};
    --theme-strings: {colors['strings']};
    --theme-functions: {colors['functions']};
    --theme-variables: {colors['variables']};
}}
"""

    def get_all_themes(self) -> List[Dict[str, Any]]:
        """Get list of all available themes"""
        themes = []
        for key, theme in self.THEMES.items():
            themes.append({
                "id": key,
                "name": theme["name"],
                "builtin": True
            })
        for key, theme in self.custom_themes.items():
            themes.append({
                "id": key,
                "name": theme.get("name", key),
                "builtin": False
            })
        return themes

    def create_custom_theme(self, name: str, colors: Dict[str, str]) -> bool:
        """Create a custom theme"""
        theme_id = name.lower().replace(" ", "_")
        self.custom_themes[theme_id] = {
            "name": name,
            **colors
        }
        self.save_custom_themes()
        return True

    def delete_custom_theme(self, theme_id: str) -> bool:
        """Delete a custom theme"""
        if theme_id in self.custom_themes:
            del self.custom_themes[theme_id]
            self.save_custom_themes()
            return True
        return False

    def save_custom_themes(self) -> None:
        """Save custom themes to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.custom_themes, f, indent=2)

    def load_custom_themes(self) -> None:
        """Load custom themes from file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.custom_themes = json.load(f)

    def apply_editor_theme(self, theme_name: str) -> Dict[str, Any]:
        """Get Monaco editor theme configuration"""
        colors = self.get_theme_colors(theme_name)
        return {
            "base": "vs-dark",
            "inherit": True,
            "rules": [
                {"token": "comment", "foreground": colors["comments"].lstrip("#")},
                {"token": "keyword", "foreground": colors["keywords"].lstrip("#")},
                {"token": "string", "foreground": colors["strings"].lstrip("#")},
                {"token": "identifier", "foreground": colors["variables"].lstrip("#")},
                {"token": "function", "foreground": colors["functions"].lstrip("#")},
            ],
            "colors": {
                "editor.background": colors["background"],
                "editor.foreground": colors["foreground"],
            }
        }

    def get_manifest(self) -> Dict[str, Any]:
        """Get plugin manifest"""
        return {
            "name": "Advanced Themes",
            "version": "1.0.0",
            "description": "Advanced theme customization for Llama IDE",
            "themes": self.get_all_themes()
        }
