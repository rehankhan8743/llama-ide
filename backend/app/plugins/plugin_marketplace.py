import requests
import json
import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Any, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import hashlib

logger = logging.getLogger(__name__)


class PluginRating(BaseModel):
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    review: str
    timestamp: datetime


class PluginDownloadStats(BaseModel):
    total_downloads: int = 0
    weekly_downloads: int = 0
    monthly_downloads: int = 0
    last_updated: Optional[datetime] = None


class MarketplacePlugin(BaseModel):
    id: str
    name: str
    version: str
    description: str
    author: str
    homepage: Optional[str] = None
    license: str = "MIT"
    tags: List[str] = []
    dependencies: List[str] = []
    rating: float = Field(default=0.0, ge=0, le=5)
    ratings_count: int = 0
    downloads: PluginDownloadStats = Field(default_factory=PluginDownloadStats)
    compatibility: Dict[str, List[str]] = {}  # version -> list of compatible versions
    last_updated: Optional[datetime] = None
    size: int = 0  # in bytes


class PluginCache:
    """Thread-safe cache for plugin data with TTL"""

    def __init__(self, cache_dir: str = "./plugin_cache", ttl_hours: int = 1):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self._memory_cache: Dict[str, tuple] = {}  # key: (data, timestamp)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get cached data if not expired"""
        # Check memory cache first
        if key in self._memory_cache:
            data, timestamp = self._memory_cache[key]
            if datetime.now() - timestamp < self.ttl:
                return data
            del self._memory_cache[key]

        # Check disk cache
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
            if datetime.now() - cache_time < self.ttl:
                try:
                    with open(cache_path, 'r') as f:
                        data = json.load(f)
                    self._memory_cache[key] = (data, datetime.now())
                    return data
                except json.JSONDecodeError:
                    cache_path.unlink(missing_ok=True)
        return None

    def set(self, key: str, data: Any) -> None:
        """Cache data in memory and disk"""
        self._memory_cache[key] = (data, datetime.now())
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, 'w') as f:
                json.dump(data, f, default=str)
        except Exception as e:
            logger.warning(f"Failed to write cache: {e}")

    def invalidate(self, key: str) -> None:
        """Invalidate a specific cache entry"""
        if key in self._memory_cache:
            del self._memory_cache[key]
        cache_path = self._get_cache_path(key)
        cache_path.unlink(missing_ok=True)

    def clear(self) -> None:
        """Clear all cache"""
        self._memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink(missing_ok=True)


class PluginRegistry:
    """Plugin marketplace registry with async support"""

    def __init__(self, registry_url: str = "https://plugins.llama-ide.com"):
        self.registry_url = registry_url.rstrip('/')
        self.cache = PluginCache()
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session

    async def search_plugins(
        self,
        query: str = "",
        category: str = "all",
        sort_by: str = "rating",
        limit: int = 20
    ) -> List[MarketplacePlugin]:
        """Search for plugins in the marketplace"""
        cache_key = f"search_{query}_{category}_{sort_by}_{limit}"

        # Check cache
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return [MarketplacePlugin(**plugin) for plugin in cached_data]

        try:
            session = await self._get_session()
            params = {
                "query": query,
                "category": category,
                "sort_by": sort_by,
                "limit": limit
            }

            async with session.get(
                f"{self.registry_url}/api/plugins/search",
                params=params
            ) as response:
                response.raise_for_status()
                plugins_data = await response.json()

                # Cache results
                self.cache.set(cache_key, plugins_data)

                return [MarketplacePlugin(**plugin) for plugin in plugins_data]

        except aiohttp.ClientError as e:
            logger.error(f"Network error searching plugins: {e}")
            return []
        except Exception as e:
            logger.error(f"Error searching plugins: {e}")
            return []

    async def get_plugin_details(self, plugin_id: str) -> Optional[MarketplacePlugin]:
        """Get detailed information about a specific plugin"""
        cache_key = f"plugin_{plugin_id}"

        cached_data = self.cache.get(cache_key)
        if cached_data:
            return MarketplacePlugin(**cached_data)

        try:
            session = await self._get_session()
            async with session.get(
                f"{self.registry_url}/api/plugins/{plugin_id}"
            ) as response:
                response.raise_for_status()
                plugin_data = await response.json()

                self.cache.set(cache_key, plugin_data)
                return MarketplacePlugin(**plugin_data)

        except aiohttp.ClientError as e:
            logger.error(f"Network error getting plugin details: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting plugin details: {e}")
            return None

    async def download_plugin(
        self,
        plugin_id: str,
        version: str = "latest",
        progress_callback: Optional[callable] = None
    ) -> str:
        """Download plugin archive and return local path"""
        try:
            session = await self._get_session()
            params = {"version": version}

            plugin_file = self.cache.cache_dir / f"{plugin_id}_{version}.zip"

            async with session.get(
                f"{self.registry_url}/api/plugins/{plugin_id}/download",
                params=params
            ) as response:
                response.raise_for_status()

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                async with aiofiles.open(plugin_file, 'wb') as f:
                    async for chunk in response.content.iter_chunked(8192):
                        await f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size:
                            progress_callback(downloaded, total_size)

            return str(plugin_file)

        except aiohttp.ClientError as e:
            logger.error(f"Network error downloading plugin: {e}")
            raise Exception(f"Failed to download plugin {plugin_id}: {str(e)}")
        except Exception as e:
            logger.error(f"Error downloading plugin: {e}")
            raise

    async def submit_plugin(
        self,
        plugin_data: Dict[str, Any],
        plugin_file: str,
        api_token: str
    ) -> Dict[str, Any]:
        """Submit a new plugin to the marketplace"""
        try:
            session = await self._get_session()

            data = aiohttp.FormData()
            for key, value in plugin_data.items():
                data.add_field(key, value)

            async with aiofiles.open(plugin_file, 'rb') as f:
                file_content = await f.read()
                data.add_field(
                    'plugin',
                    file_content,
                    filename=Path(plugin_file).name,
                    content_type='application/zip'
                )

                async with session.post(
                    f"{self.registry_url}/api/plugins/submit",
                    data=data,
                    headers={"Authorization": f"Bearer {api_token}"}
                ) as response:
                    response.raise_for_status()
                    return await response.json()

        except aiohttp.ClientError as e:
            logger.error(f"Network error submitting plugin: {e}")
            raise Exception(f"Failed to submit plugin: {str(e)}")

    async def get_categories(self) -> List[str]:
        """Get available plugin categories"""
        cache_key = "categories"

        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            session = await self._get_session()
            async with session.get(
                f"{self.registry_url}/api/plugins/categories"
            ) as response:
                response.raise_for_status()
                categories = await response.json()
                self.cache.set(cache_key, categories)
                return categories

        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return [
                "development",
                "utility",
                "theme",
                "language",
                "debugging",
                "testing",
                "productivity"
            ]

    async def get_featured_plugins(self) -> List[MarketplacePlugin]:
        """Get featured/trending plugins"""
        return await self.search_plugins(sort_by="featured", limit=10)

    async def rate_plugin(
        self,
        plugin_id: str,
        user_id: str,
        rating: int,
        review: str = "",
        api_token: str = ""
    ) -> bool:
        """Submit a rating for a plugin"""
        try:
            session = await self._get_session()
            data = {
                "user_id": user_id,
                "rating": rating,
                "review": review
            }

            async with session.post(
                f"{self.registry_url}/api/plugins/{plugin_id}/rate",
                json=data,
                headers={"Authorization": f"Bearer {api_token}"}
            ) as response:
                response.raise_for_status()
                # Invalidate cached plugin data
                self.cache.invalidate(f"plugin_{plugin_id}")
                return True

        except Exception as e:
            logger.error(f"Error rating plugin: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()


class PluginCompatibilityChecker:
    """Check plugin compatibility with the IDE and system"""

    def __init__(self):
        self.compatibility_matrix = self._load_compatibility_matrix()

    def _load_compatibility_matrix(self) -> Dict[str, List[str]]:
        """Load compatibility matrix for plugins"""
        return {
            "llama-ide": ["1.0.0", "1.1.0", "1.2.0", "2.0.0"],
            "python": ["3.8", "3.9", "3.10", "3.11", "3.12"],
            "node": ["16", "18", "20"]
        }

    def check_compatibility(
        self,
        plugin: MarketplacePlugin,
        ide_version: str,
        system_info: Dict[str, str]
    ) -> Dict[str, Any]:
        """Check if plugin is compatible with current environment"""
        compatibility_report = {
            "compatible": True,
            "issues": [],
            "warnings": [],
            "details": {}
        }

        # Check IDE version compatibility
        if "llama-ide" in plugin.compatibility:
            required_versions = plugin.compatibility["llama-ide"]
            if ide_version not in required_versions:
                compatibility_report["compatible"] = False
                compatibility_report["issues"].append(
                    f"Plugin requires llama-ide {required_versions}, "
                    f"but you have {ide_version}"
                )
            else:
                compatibility_report["details"]["llama-ide"] = "compatible"

        # Check system compatibility
        for system_component, required_versions in plugin.compatibility.items():
            if system_component == "llama-ide":
                continue

            if system_component in system_info:
                current_version = system_info[system_component]
                if current_version not in required_versions:
                    compatibility_report["warnings"].append(
                        f"{system_component} version {current_version} "
                        f"may not be fully compatible (requires: {required_versions})"
                    )
                else:
                    compatibility_report["details"][system_component] = "compatible"

        return compatibility_report

    def check_dependencies(
        self,
        plugin: MarketplacePlugin,
        installed_plugins: Dict[str, str]
    ) -> Dict[str, Any]:
        """Check if plugin dependencies are satisfied"""
        result = {
            "satisfied": True,
            "missing": [],
            "outdated": []
        }

        for dep in plugin.dependencies:
            # Parse dependency string (e.g., "plugin-name>=1.0.0")
            dep_name = dep.split(">=")[0].split("==")[0].strip()
            dep_version = None
            if ">=" in dep:
                dep_version = dep.split(">=")[1].strip()

            if dep_name not in installed_plugins:
                result["satisfied"] = False
                result["missing"].append(dep)
            elif dep_version:
                installed_version = installed_plugins[dep_name]
                if installed_version < dep_version:
                    result["satisfied"] = False
                    result["outdated"].append({
                        "plugin": dep_name,
                        "required": dep_version,
                        "installed": installed_version
                    })

        return result


class PluginAnalytics:
    """Track plugin usage and popularity"""

    def __init__(self, analytics_file: str = "./plugin_analytics.json"):
        self.analytics_file = Path(analytics_file)
        self.usage_data = self._load_analytics()

    def _load_analytics(self) -> Dict[str, Any]:
        """Load plugin usage analytics"""
        try:
            if self.analytics_file.exists():
                with open(self.analytics_file, 'r') as f:
                    data = json.load(f)
                    # Convert lists back to sets for active_users
                    for plugin_data in data.get("plugins", {}).values():
                        if "active_users" in plugin_data:
                            plugin_data["active_users"] = set(plugin_data["active_users"])
                    return data
            return {"plugins": {}, "users": {}}
        except Exception as e:
            logger.warning(f"Failed to load analytics: {e}")
            return {"plugins": {}, "users": {}}

    def record_plugin_install(self, plugin_id: str, user_id: str) -> None:
        """Record plugin installation"""
        if plugin_id not in self.usage_data["plugins"]:
            self.usage_data["plugins"][plugin_id] = {
                "installs": 0,
                "active_users": set(),
                "usage_count": 0,
                "features_used": {},
                "last_installed": None
            }

        plugin_data = self.usage_data["plugins"][plugin_id]
        plugin_data["installs"] += 1
        plugin_data["active_users"].add(user_id)
        plugin_data["last_installed"] = datetime.now().isoformat()

        self._save_analytics()

    def record_plugin_uninstall(self, plugin_id: str, user_id: str) -> None:
        """Record plugin uninstallation"""
        if plugin_id in self.usage_data["plugins"]:
            plugin_data = self.usage_data["plugins"][plugin_id]
            plugin_data["active_users"].discard(user_id)
            plugin_data["last_uninstalled"] = datetime.now().isoformat()
            self._save_analytics()

    def record_plugin_usage(
        self,
        plugin_id: str,
        user_id: str,
        feature_used: Optional[str] = None
    ) -> None:
        """Record plugin usage"""
        if plugin_id not in self.usage_data["plugins"]:
            self.usage_data["plugins"][plugin_id] = {
                "installs": 0,
                "active_users": set(),
                "usage_count": 0,
                "features_used": {}
            }

        plugin_data = self.usage_data["plugins"][plugin_id]
        plugin_data["usage_count"] = plugin_data.get("usage_count", 0) + 1
        plugin_data["active_users"].add(user_id)

        if feature_used:
            features = plugin_data.setdefault("features_used", {})
            features[feature_used] = features.get(feature_used, 0) + 1

        self._save_analytics()

    def _save_analytics(self) -> None:
        """Save analytics data to file"""
        try:
            # Convert sets to lists for JSON serialization
            serializable_data = {
                "plugins": {},
                "last_saved": datetime.now().isoformat()
            }
            for plugin_id, plugin_data in self.usage_data["plugins"].items():
                serializable_data["plugins"][plugin_id] = {
                    **plugin_data,
                    "active_users": list(plugin_data["active_users"])
                }

            with open(self.analytics_file, 'w') as f:
                json.dump(serializable_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analytics: {e}")

    def get_popular_plugins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular plugins based on installations and usage"""
        plugin_scores = []
        for plugin_id, data in self.usage_data["plugins"].items():
            score = data.get("installs", 0) * 0.7 + data.get("usage_count", 0) * 0.3
            plugin_scores.append({
                "plugin_id": plugin_id,
                "score": round(score, 2),
                "installs": data.get("installs", 0),
                "usage_count": data.get("usage_count", 0),
                "active_users": len(data.get("active_users", set()))
            })

        return sorted(plugin_scores, key=lambda x: x["score"], reverse=True)[:limit]

    def get_plugin_stats(self, plugin_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a specific plugin"""
        data = self.usage_data["plugins"].get(plugin_id)
        if data:
            return {
                **data,
                "active_users_count": len(data.get("active_users", set())),
                "active_users": list(data.get("active_users", set()))[:10]  # Sample
            }
        return None


# Initialize marketplace services
plugin_registry = PluginRegistry()
compatibility_checker = PluginCompatibilityChecker()
plugin_analytics = PluginAnalytics()
