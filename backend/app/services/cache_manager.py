import asyncio
import time
import threading
from typing import Dict, Any, Optional, Callable, Union
from functools import wraps
import hashlib
import pickle
import os
import shutil
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TTLCache:
    """In-memory TTL cache with LRU eviction"""

    def __init__(self, maxsize: int = 1000, ttl: int = 300):
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: Dict[str, tuple] = {}  # key: (value, expiry_time)
        self._access_times: Dict[str, float] = {}  # key: last_access_time
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired"""
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._access_times[key] = time.time()
                    return value
                else:
                    # Remove expired entry
                    self._remove_key(key)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with optional custom TTL"""
        with self._lock:
            # Evict oldest entries if cache is full
            if len(self._cache) >= self.maxsize and key not in self._cache:
                self._evict_oldest()

            expiry = time.time() + (ttl or self.ttl)
            self._cache[key] = (value, expiry)
            self._access_times[key] = time.time()

    def delete(self, key: str) -> bool:
        """Delete a specific key from cache, returns True if key existed"""
        with self._lock:
            if key in self._cache:
                self._remove_key(key)
                return True
            return False

    def _remove_key(self, key: str) -> None:
        """Remove a key from internal data structures"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)

    def _evict_oldest(self) -> None:
        """Remove the least recently used entry"""
        if self._access_times:
            oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
            self._remove_key(oldest_key)

    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()

    def keys(self) -> list:
        """Return all valid (non-expired) keys"""
        with self._lock:
            current_time = time.time()
            valid_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time < expiry
            ]
            return valid_keys

    def info(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self._cache),
                "maxsize": self.maxsize,
                "ttl": self.ttl,
                "hit_ratio": "N/A"  # Would need hit/miss counters
            }


class DiskCache:
    """Persistent disk-based cache with TTL support"""

    def __init__(self, cache_dir: str = "./cache", default_ttl: int = 3600):
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, key: str) -> Path:
        """Get file path for cache key using hash"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        # Use subdirectories to avoid too many files in one dir
        subdir = key_hash[:2]
        cache_subdir = self.cache_dir / subdir
        cache_subdir.mkdir(exist_ok=True)
        return cache_subdir / f"{key_hash}.cache"

    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache"""
        cache_path = self._get_cache_path(key)
        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)

            # Check if expired (data format: (value, timestamp, ttl))
            if isinstance(data, tuple) and len(data) == 3:
                value, timestamp, ttl = data
                if time.time() - timestamp < ttl:
                    return value
                else:
                    # Remove expired file
                    cache_path.unlink(missing_ok=True)
        except (pickle.PickleError, IOError, OSError) as e:
            logger.warning(f"Error reading disk cache for key {key}: {e}")
            # Remove corrupted cache file
            cache_path.unlink(missing_ok=True)

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in disk cache"""
        cache_path = self._get_cache_path(key)
        try:
            data = (value, time.time(), ttl or self.default_ttl)
            # Write to temp file first, then rename for atomicity
            temp_path = cache_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                pickle.dump(data, f)
            temp_path.rename(cache_path)
            return True
        except (pickle.PickleError, IOError, OSError) as e:
            logger.error(f"Error writing to disk cache for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """Delete a specific key from disk cache"""
        cache_path = self._get_cache_path(key)
        if cache_path.exists():
            cache_path.unlink(missing_ok=True)
            return True
        return False

    def clear(self) -> None:
        """Clear all disk cache entries"""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def cleanup_expired(self) -> int:
        """Remove all expired cache files, returns count removed"""
        removed = 0
        for cache_file in self.cache_dir.rglob("*.cache"):
            try:
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                if isinstance(data, tuple) and len(data) == 3:
                    _, timestamp, ttl = data
                    if time.time() - timestamp >= ttl:
                        cache_file.unlink()
                        removed += 1
            except (pickle.PickleError, IOError, OSError):
                # Remove corrupted files
                cache_file.unlink(missing_ok=True)
                removed += 1
        return removed


class CacheManager:
    """Unified cache manager with memory and disk caching"""

    def __init__(self, memory_maxsize: int = 1000, memory_ttl: int = 300,
                 disk_dir: str = "./cache", disk_ttl: int = 3600):
        self.memory_cache = TTLCache(maxsize=memory_maxsize, ttl=memory_ttl)
        self.disk_cache = DiskCache(disk_dir, disk_ttl)

    async def get_cached_result(
        self,
        key: str,
        compute_func: Callable,
        use_disk_cache: bool = True,
        memory_only: bool = False
    ) -> Any:
        """Get cached result or compute new one"""
        # Try memory cache first
        result = self.memory_cache.get(key)
        if result is not None:
            return result

        # Try disk cache if enabled
        if use_disk_cache and not memory_only:
            result = self.disk_cache.get(key)
            if result is not None:
                # Store in memory cache for faster access next time
                self.memory_cache.set(key, result)
                return result

        # Compute new result
        if asyncio.iscoroutinefunction(compute_func):
            result = await compute_func()
        else:
            result = compute_func()

        # Store in caches
        self.memory_cache.set(key, result)
        if use_disk_cache and not memory_only:
            self.disk_cache.set(key, result)

        return result

    def get(self, key: str, use_disk: bool = True) -> Optional[Any]:
        """Get value from cache (memory first, then disk)"""
        result = self.memory_cache.get(key)
        if result is not None:
            return result
        if use_disk:
            result = self.disk_cache.get(key)
            if result is not None:
                # Promote to memory cache
                self.memory_cache.set(key, result)
                return result
        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        use_disk: bool = True
    ) -> None:
        """Set value in cache"""
        self.memory_cache.set(key, value, ttl)
        if use_disk:
            self.disk_cache.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """Delete from both memory and disk cache"""
        mem_deleted = self.memory_cache.delete(key)
        disk_deleted = self.disk_cache.delete(key)
        return mem_deleted or disk_deleted

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern (substring match)"""
        removed = 0
        for key in self.memory_cache.keys():
            if pattern in key:
                self.memory_cache.delete(key)
                removed += 1
        return removed

    def clear_all(self) -> None:
        """Clear all cache entries from memory and disk"""
        self.memory_cache.clear()
        self.disk_cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "memory": self.memory_cache.info(),
            "disk_dir": str(self.disk_cache.cache_dir)
        }

    def cleanup(self) -> int:
        """Clean up expired disk cache entries"""
        return self.disk_cache.cleanup_expired()


# Global cache manager instance
cache_manager = CacheManager()


def cached(
    ttl: int = 300,
    use_disk: bool = True,
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching function results.

    Args:
        ttl: Time to live in seconds
        use_disk: Whether to use disk cache
        key_func: Optional function to generate custom cache key from arguments
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            cache_key = _generate_cache_key(func, key_func, *args, **kwargs)

            async def compute():
                return await func(*args, **kwargs)

            return await cache_manager.get_cached_result(
                cache_key, compute, use_disk
            )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            cache_key = _generate_cache_key(func, key_func, *args, **kwargs)

            def compute():
                return func(*args, **kwargs)

            # Run sync function through cache manager
            # Note: This creates a new event loop if needed
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If already in async context, can't use get_cached_result
                    # So just call directly without caching
                    return func(*args, **kwargs)
                else:
                    return loop.run_until_complete(
                        cache_manager.get_cached_result(cache_key, compute, use_disk)
                    )
            except RuntimeError:
                # No event loop, create one
                return asyncio.run(
                    cache_manager.get_cached_result(cache_key, compute, use_disk)
                )

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


def _generate_cache_key(
    func: Callable,
    key_func: Optional[Callable],
    *args,
    **kwargs
) -> str:
    """Generate a cache key from function and arguments"""
    if key_func:
        return key_func(*args, **kwargs)

    key_parts = [func.__module__, func.__qualname__]
    key_parts.extend([_hash_arg(arg) for arg in args])
    key_parts.extend([f"{k}={_hash_arg(v)}" for k, v in sorted(kwargs.items())])
    return ":".join(key_parts)


def _hash_arg(arg: Any) -> str:
    """Convert argument to hashable string representation"""
    if isinstance(arg, (str, int, float, bool)):
        return str(arg)
    try:
        # Try to hash the object directly
        return hashlib.sha256(str(arg).encode()).hexdigest()[:16]
    except Exception:
        return hashlib.sha256(pickle.dumps(arg)).hexdigest()[:16]


class AsyncCacheContext:
    """Async context manager for temporary cache operations"""

    def __init__(self, manager: CacheManager, temp_ttl: int = 60):
        self.manager = manager
        self.temp_ttl = temp_ttl

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def compute_and_cache(self, key: str, func: Callable) -> Any:
        """Compute and cache a result with the context's TTL"""
        return await self.manager.get_cached_result(
            key, func, use_disk_cache=False
        )
