from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import hashlib
import uuid


class PluginRating(BaseModel):
    plugin_id: str
    user_id: str
    rating: int  # 1-5
    review: Optional[str] = None
    created_at: str


class PluginStats(BaseModel):
    plugin_id: str
    downloads: int
    rating_avg: float
    rating_count: int


class MarketplacePlugin(BaseModel):
    id: str
    name: str
    description: str
    version: str
    author: str
    author_id: str
    homepage: Optional[str] = None
    tags: List[str]
    downloads: int
    rating_avg: float
    rating_count: int
    is_featured: bool = False
    is_premium: bool = False
    installed: bool = False
    created_at: str
    updated_at: str


class PluginMarketplaceService:
    def __init__(self):
        self.plugins: Dict[str, MarketplacePlugin] = {}
        self.ratings: Dict[str, List[PluginRating]] = {}
        self.user_installed: Dict[str, List[str]] = {}  # user_id -> list of plugin_ids
        self._load_sample_plugins()

    def _load_sample_plugins(self) -> None:
        """Load sample marketplace plugins"""
        sample_plugins = [
            MarketplacePlugin(
                id="python-debugger",
                name="Python Debugger",
                description="Advanced debugging tools for Python development with breakpoints, watch expressions, and call stack visualization",
                version="2.1.0",
                author="DevTools Inc",
                author_id="devtools-inc",
                tags=["debugging", "python", "development"],
                downloads=15420,
                rating_avg=4.8,
                rating_count=312,
                is_featured=True,
                created_at="2024-01-15T10:00:00Z",
                updated_at="2024-03-20T15:30:00Z"
            ),
            MarketplacePlugin(
                id="theme-pack-pro",
                name="Theme Pack Pro",
                description="Professional themes collection with 50+ color schemes for enhanced coding experience",
                version="1.3.2",
                author="Design Studio",
                author_id="design-studio",
                tags=["theme", "customization", "appearance"],
                downloads=8920,
                rating_avg=4.6,
                rating_count=156,
                is_featured=True,
                created_at="2024-02-01T09:00:00Z",
                updated_at="2024-03-15T12:00:00Z"
            ),
            MarketplacePlugin(
                id="git-integration-plus",
                name="Git Integration Plus",
                description="Enhanced Git features with visual commit graphs, branch management, and merge conflict resolution",
                version="3.0.1",
                author="VCS Team",
                author_id="vcs-team",
                tags=["git", "version-control", "collaboration"],
                downloads=22150,
                rating_avg=4.9,
                rating_count=489,
                is_featured=True,
                created_at="2023-11-20T14:00:00Z",
                updated_at="2024-03-25T09:15:00Z"
            ),
            MarketplacePlugin(
                id="docker-manager",
                name="Docker Manager",
                description="Manage Docker containers, images, volumes, and networks from within the IDE",
                version="1.5.0",
                author="Container Solutions",
                author_id="container-solutions",
                tags=["docker", "devops", "containers"],
                downloads=12300,
                rating_avg=4.7,
                rating_count=234,
                created_at="2024-01-05T11:00:00Z",
                updated_at="2024-03-18T16:45:00Z"
            ),
            MarketplacePlugin(
                id="api-tester",
                name="API Tester",
                description="Test and debug REST and GraphQL APIs with request builder and response viewer",
                version="2.2.0",
                author="API Tools Co",
                author_id="api-tools",
                tags=["api", "testing", "development"],
                downloads=18700,
                rating_avg=4.5,
                rating_count=378,
                created_at="2023-12-10T08:00:00Z",
                updated_at="2024-03-22T11:30:00Z"
            ),
            MarketplacePlugin(
                id="database-client",
                name="Database Client",
                description="Connect to PostgreSQL, MySQL, MongoDB, and other databases with visual query builder",
                version="1.8.3",
                author="Data Tools Inc",
                author_id="data-tools",
                tags=["database", "sql", "mongodb"],
                downloads=9500,
                rating_avg=4.4,
                rating_count=189,
                created_at="2024-02-15T10:30:00Z",
                updated_at="2024-03-19T14:00:00Z"
            )
        ]

        for plugin in sample_plugins:
            self.plugins[plugin.id] = plugin

    def get_plugins(self, category: Optional[str] = None, search: Optional[str] = None,
                   sort_by: str = "downloads", featured_only: bool = False) -> List[Dict[str, Any]]:
        """Get marketplace plugins with filtering"""
        results = list(self.plugins.values())

        # Filter by category
        if category and category != "all":
            results = [p for p in results if category.lower() in [t.lower() for t in p.tags]]

        # Filter by search
        if search:
            search_lower = search.lower()
            results = [p for p in results if
                      search_lower in p.name.lower() or
                      search_lower in p.description.lower() or
                      any(search_lower in tag.lower() for tag in p.tags)]

        # Filter featured
        if featured_only:
            results = [p for p in results if p.is_featured]

        # Sort
        if sort_by == "downloads":
            results.sort(key=lambda x: x.downloads, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda x: (x.rating_avg, x.rating_count), reverse=True)
        elif sort_by == "recent":
            results.sort(key=lambda x: x.updated_at, reverse=True)
        elif sort_by == "name":
            results.sort(key=lambda x: x.name.lower())

        return [p.model_dump() for p in results]

    def get_plugin(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific plugin by ID"""
        plugin = self.plugins.get(plugin_id)
        return plugin.model_dump() if plugin else None

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all available categories with counts"""
        categories: Dict[str, int] = {}
        for plugin in self.plugins.values():
            for tag in plugin.tags:
                categories[tag] = categories.get(tag, 0) + 1

        return [
            {"name": tag, "count": count}
            for tag, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)
        ]

    def get_featured(self) -> List[Dict[str, Any]]:
        """Get featured plugins"""
        return [p.model_dump() for p in self.plugins.values() if p.is_featured]

    def rate_plugin(self, plugin_id: str, user_id: str, rating: int,
                   review: Optional[str] = None) -> Dict[str, Any]:
        """Rate a plugin"""
        if plugin_id not in self.plugins:
            return {"error": "Plugin not found"}

        if rating < 1 or rating > 5:
            return {"error": "Rating must be between 1 and 5"}

        plugin_rating = PluginRating(
            plugin_id=plugin_id,
            user_id=user_id,
            rating=rating,
            review=review
        )

        if plugin_id not in self.ratings:
            self.ratings[plugin_id] = []

        # Update existing rating or add new
        for i, r in enumerate(self.ratings[plugin_id]):
            if r.user_id == user_id:
                self.ratings[plugin_id][i] = plugin_rating
                break
        else:
            self.ratings[plugin_id].append(plugin_rating)

        # Update plugin average
        ratings = self.ratings[plugin_id]
        avg = sum(r.rating for r in ratings) / len(ratings)
        self.plugins[plugin_id].rating_avg = round(avg, 1)
        self.plugins[plugin_id].rating_count = len(ratings)

        return {"message": "Rating submitted", "new_average": avg}

    def get_reviews(self, plugin_id: str) -> List[Dict[str, Any]]:
        """Get reviews for a plugin"""
        if plugin_id not in self.ratings:
            return []
        return [r.model_dump() for r in self.ratings[plugin_id]]

    def install_plugin(self, user_id: str, plugin_id: str) -> Dict[str, Any]:
        """Mark plugin as installed for user"""
        if plugin_id not in self.plugins:
            return {"error": "Plugin not found"}

        if user_id not in self.user_installed:
            self.user_installed[user_id] = []

        if plugin_id not in self.user_installed[user_id]:
            self.user_installed[user_id].append(plugin_id)
            self.plugins[plugin_id].downloads += 1
            self.plugins[plugin_id].installed = True

        return {"message": "Plugin installed", "plugin_id": plugin_id}

    def uninstall_plugin(self, user_id: str, plugin_id: str) -> Dict[str, Any]:
        """Mark plugin as uninstalled for user"""
        if user_id not in self.user_installed:
            return {"error": "User has no installed plugins"}

        if plugin_id in self.user_installed[user_id]:
            self.user_installed[user_id].remove(plugin_id)

        return {"message": "Plugin uninstalled", "plugin_id": plugin_id}

    def get_installed(self, user_id: str) -> List[Dict[str, Any]]:
        """Get installed plugins for a user"""
        if user_id not in self.user_installed:
            return []
        return [self.plugins[pid].model_dump()
                for pid in self.user_installed[user_id]
                if pid in self.plugins]

    def recommend_plugins(self, user_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Recommend plugins based on user's installed plugins"""
        if user_id not in self.user_installed or not self.user_installed[user_id]:
            # Return top rated if no history
            return sorted(
                [p.model_dump() for p in self.plugins.values()],
                key=lambda x: (x["rating_avg"], x["downloads"]),
                reverse=True
            )[:limit]

        # Get tags from user's installed plugins
        user_tags = set()
        for plugin_id in self.user_installed[user_id]:
            if plugin_id in self.plugins:
                user_tags.update(self.plugins[plugin_id].tags)

        # Find plugins with matching tags that aren't installed
        recommendations = []
        for plugin_id, plugin in self.plugins.items():
            if plugin_id not in self.user_installed[user_id]:
                matching_tags = len(user_tags.intersection(plugin.tags))
                score = matching_tags + plugin.rating_avg * 0.1
                recommendations.append((score, plugin))

        # Sort by score and return top N
        recommendations.sort(key=lambda x: x[0], reverse=True)
        return [p.model_dump() for _, p in recommendations[:limit]]


# Global marketplace service instance
plugin_marketplace = PluginMarketplaceService()
