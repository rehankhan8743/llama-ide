from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib
import asyncio


class CacheEntry:
    def __init__(self, value: Any, ttl: int = 300):
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl

    def is_expired(self) -> bool:
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl)


class TTLCache:
    """In-memory cache with TTL support"""

    def __init__(self, maxsize: int = 1000, default_ttl: int = 300):
        self.maxsize = maxsize
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if not entry.is_expired():
                # Move to end (most recently used)
                if key in self.access_order:
                    self.access_order.remove(key)
                self.access_order.append(key)
                return entry.value
            else:
                # Remove expired entry
                del self.cache[key]
                if key in self.access_order:
                    self.access_order.remove(key)
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        if ttl is None:
            ttl = self.default_ttl

        # Evict oldest if at capacity
        if len(self.cache) >= self.maxsize and key not in self.cache:
            oldest = self.access_order.pop(0)
            del self.cache[oldest]

        self.cache[key] = CacheEntry(value, ttl)

        if key in self.access_order:
            self.access_order.remove(key)
        self.access_order.append(key)

    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return True
        return False

    def clear(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()
        self.access_order.clear()

    def size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

    def keys(self) -> List[str]:
        """Get all cache keys"""
        return list(self.cache.keys())


class DiskCache:
    """Disk-based cache for larger data"""

    def __init__(self, cache_dir: str = "./cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.cache_dir / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        """Load cache index from disk"""
        if self.index_path.exists():
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)
        else:
            self.index: Dict[str, Dict[str, Any]] = {}

    def _save_index(self) -> None:
        """Save cache index to disk"""
        with open(self.index_path, 'w') as f:
            json.dump(self.index, f)

    def _get_cache_path(self, key: str) -> Path:
        """Get path for cache file"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        if key not in self.index:
            return None

        entry = self.index[key]
        cache_path = self._get_cache_path(key)

        # Check if expired
        if datetime.now() > datetime.fromisoformat(entry["expires_at"]):
            self.delete(key)
            return None

        if cache_path.exists():
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None

    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in disk cache"""
        cache_path = self._get_cache_path(key)

        with open(cache_path, 'w') as f:
            json.dump(value, f)

        self.index[key] = {
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(seconds=ttl)).isoformat(),
            "size": cache_path.stat().st_size if cache_path.exists() else 0
        }
        self._save_index()

    def delete(self, key: str) -> bool:
        """Delete value from disk cache"""
        if key not in self.index:
            return False

        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink()

        del self.index[key]
        self._save_index()
        return True

    def clear(self) -> None:
        """Clear all disk cache entries"""
        for key in list(self.index.keys()):
            self.delete(key)

    def size(self) -> int:
        """Get number of cached items"""
        return len(self.index)


class CacheManager:
    """Multi-level cache manager combining memory and disk caches"""

    def __init__(self, memory_maxsize: int = 1000, memory_ttl: int = 300,
                 disk_cache_dir: str = "./cache"):
        self.memory_cache = TTLCache(maxsize=memory_maxsize, default_ttl=memory_ttl)
        self.disk_cache = DiskCache(cache_dir=disk_cache_dir)

    async def get_cached(self, key: str, compute_func: Optional[Callable] = None) -> Any:
        """Get cached result or compute new one"""
        # Try memory cache first
        result = self.memory_cache.get(key)
        if result is not None:
            return result

        # Try disk cache
        result = self.disk_cache.get(key)
        if result is not None:
            # Promote to memory cache
            self.memory_cache.set(key, result)
            return result

        # Compute if function provided
        if compute_func is not None:
            if asyncio.iscoroutinefunction(compute_func):
                result = await compute_func()
            else:
                result = compute_func()

            # Store in both caches
            self.memory_cache.set(key, result)
            self.disk_cache.set(key, result)
            return result

        return None

    def get(self, key: str) -> Any:
        """Get value from cache (no computation)"""
        result = self.memory_cache.get(key)
        if result is not None:
            return result
        return self.disk_cache.get(key)

    def set(self, key: str, value: Any, memory_ttl: Optional[int] = None,
            disk_ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        self.memory_cache.set(key, value, memory_ttl)
        self.disk_cache.set(key, value, disk_ttl or 3600)

    def invalidate(self, key: str) -> None:
        """Invalidate a cache entry"""
        self.memory_cache.delete(key)
        self.disk_cache.delete(key)

    def clear(self) -> None:
        """Clear all caches"""
        self.memory_cache.clear()
        self.disk_cache.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "memory_size": self.memory_cache.size(),
            "memory_maxsize": self.memory_cache.maxsize,
            "disk_size": self.disk_cache.size(),
            "keys": {
                "memory": self.memory_cache.keys(),
                "disk": list(self.disk_cache.index.keys())
            }
        }


# Global cache manager instance
cache_manager = CacheManager()
