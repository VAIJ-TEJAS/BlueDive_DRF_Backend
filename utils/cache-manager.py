"""
Simple Cache Manager Utility
Basic caching functionality with TTL support
"""

import time
import json
from typing import Any, Optional, Dict, Union
from datetime import datetime, timedelta


class CacheManager:
    """Simple in-memory cache manager with TTL support."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self._cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Store a value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to store
            ttl: Time to live in seconds (uses default if None)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        expiry_time = time.time() + ttl
        
        self._cache[key] = {
            'value': value,
            'expiry': expiry_time,
            'created': time.time()
        }
    
    def get(self, key: str) -> Any:
        """
        Retrieve a value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
            
        cache_item = self._cache[key]
        
        # Check if expired
        if time.time() > cache_item['expiry']:
            del self._cache[key]
            return None
            
        return cache_item['value']
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key was deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists and is not expired
        """
        return self.get(key) is not None
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Remaining TTL in seconds or None if not found
        """
        if key not in self._cache:
            return None
            
        cache_item = self._cache[key]
        remaining = cache_item['expiry'] - time.time()
        
        if remaining <= 0:
            del self._cache[key]
            return None
            
        return int(remaining)
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """
        Update TTL for an existing key.
        
        Args:
            key: Cache key
            ttl: New TTL in seconds
            
        Returns:
            True if TTL was updated, False if key not found
        """
        if key not in self._cache:
            return False
            
        cache_item = self._cache[key]
        cache_item['expiry'] = time.time() + ttl
        return True
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []
        
        for key, cache_item in self._cache.items():
            if current_time > cache_item['expiry']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """Get number of non-expired cache entries."""
        self.cleanup_expired()
        return len(self._cache)
    
    def keys(self) -> list:
        """Get list of non-expired cache keys."""
        self.cleanup_expired()
        return list(self._cache.keys())
    
    def values(self) -> list:
        """Get list of non-expired cache values."""
        self.cleanup_expired()
        return [item['value'] for item in self._cache.values()]
    
    def items(self) -> list:
        """Get list of non-expired cache key-value pairs."""
        self.cleanup_expired()
        return [(key, item['value']) for key, item in self._cache.items()]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        self.cleanup_expired()
        
        current_time = time.time()
        total_items = len(self._cache)
        
        if total_items == 0:
            return {
                'total_items': 0,
                'memory_usage': 0,
                'oldest_item': None,
                'newest_item': None,
                'average_ttl': 0
            }
        
        # Calculate memory usage (rough estimate)
        memory_usage = len(json.dumps(self._cache).encode('utf-8'))
        
        # Find oldest and newest items
        timestamps = [item['created'] for item in self._cache.values()]
        oldest_time = min(timestamps)
        newest_time = max(timestamps)
        
        # Calculate average TTL
        ttls = [item['expiry'] - current_time for item in self._cache.values()]
        average_ttl = sum(ttls) / len(ttls)
        
        return {
            'total_items': total_items,
            'memory_usage': memory_usage,
            'oldest_item': datetime.fromtimestamp(oldest_time).isoformat(),
            'newest_item': datetime.fromtimestamp(newest_time).isoformat(),
            'average_ttl': int(average_ttl)
        }
    
    def set_many(self, items: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """
        Set multiple key-value pairs.
        
        Args:
            items: Dictionary of key-value pairs
            ttl: Time to live in seconds
        """
        for key, value in items.items():
            self.set(key, value, ttl)
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs for found keys
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def delete_many(self, keys: list) -> int:
        """
        Delete multiple keys.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Number of keys deleted
        """
        deleted_count = 0
        for key in keys:
            if self.delete(key):
                deleted_count += 1
        return deleted_count
    
    def set_with_pattern(self, pattern: str, value: Any, ttl: Optional[int] = None) -> str:
        """
        Set a value with a generated key based on pattern.
        
        Args:
            pattern: Pattern for key generation
            value: Value to store
            ttl: Time to live in seconds
            
        Returns:
            Generated key
        """
        import uuid
        key = f"{pattern}_{uuid.uuid4().hex[:8]}"
        self.set(key, value, ttl)
        return key
    
    def get_by_pattern(self, pattern: str) -> Dict[str, Any]:
        """
        Get all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            Dictionary of matching key-value pairs
        """
        import fnmatch
        
        self.cleanup_expired()
        result = {}
        
        for key, cache_item in self._cache.items():
            if fnmatch.fnmatch(key, pattern):
                result[key] = cache_item['value']
        
        return result
    
    def delete_by_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            Number of keys deleted
        """
        import fnmatch
        
        keys_to_delete = []
        for key in self._cache.keys():
            if fnmatch.fnmatch(key, pattern):
                keys_to_delete.append(key)
        
        return self.delete_many(keys_to_delete)


# Global cache instance
cache_manager = CacheManager()


# Decorator for caching function results
def cache_result(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_parts = [key_prefix, func.__name__]
            
            # Add args to key
            if args:
                key_parts.extend(str(arg) for arg in args)
            
            # Add kwargs to key
            if kwargs:
                sorted_kwargs = sorted(kwargs.items())
                key_parts.extend(f"{k}:{v}" for k, v in sorted_kwargs)
            
            cache_key = "_".join(key_parts)
            
            # Try to get from cache
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Utility functions for common cache operations
def cache_json(key: str, data: Union[Dict, list], ttl: Optional[int] = None) -> None:
    """Cache JSON serializable data."""
    cache_manager.set(key, json.dumps(data), ttl)


def get_cached_json(key: str) -> Optional[Union[Dict, list]]:
    """Get cached JSON data."""
    cached_data = cache_manager.get(key)
    if cached_data is not None:
        try:
            return json.loads(cached_data)
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def cache_query_result(query_key: str, result: Any, ttl: int = 300) -> None:
    """Cache database query result."""
    cache_manager.set(f"query:{query_key}", result, ttl)


def get_cached_query(query_key: str) -> Any:
    """Get cached database query result."""
    return cache_manager.get(f"query:{query_key}")


def invalidate_cache_pattern(pattern: str) -> int:
    """Invalidate cache entries matching pattern."""
    return cache_manager.delete_by_pattern(pattern)
