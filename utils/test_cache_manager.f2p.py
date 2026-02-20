"""
F2P tests for cache manager utility.
These tests would fail on the base branch and pass after the fixes.
"""

import time
import pytest
from utils.cache_manager import (
    CacheManager,
    cache_manager,
    cache_result,
    cache_json,
    get_cached_json,
    cache_query_result,
    get_cached_query,
    invalidate_cache_pattern
)


class TestCacheManager:
    """Test CacheManager class functionality."""

    def test_cache_manager_initialization(self):
        """Test cache manager initialization."""
        cache = CacheManager()
        assert cache.default_ttl == 300
        assert cache.size() == 0

    def test_cache_manager_custom_ttl(self):
        """Test cache manager with custom TTL."""
        cache = CacheManager(default_ttl=600)
        assert cache.default_ttl == 600

    def test_set_and_get_value(self):
        """Test setting and getting values."""
        cache = CacheManager()
        
        cache.set('test_key', 'test_value')
        assert cache.get('test_key') == 'test_value'
        assert cache.size() == 1

    def test_get_nonexistent_key(self):
        """Test getting non-existent key."""
        cache = CacheManager()
        
        assert cache.get('nonexistent') is None

    def test_set_with_custom_ttl(self):
        """Test setting value with custom TTL."""
        cache = CacheManager()
        
        cache.set('test_key', 'test_value', ttl=1)
        assert cache.get('test_key') == 'test_value'
        
        # Wait for expiration
        time.sleep(1.1)
        assert cache.get('test_key') is None

    def test_delete_key(self):
        """Test deleting keys."""
        cache = CacheManager()
        
        cache.set('test_key', 'test_value')
        assert cache.delete('test_key') is True
        assert cache.get('test_key') is None
        assert cache.delete('test_key') is False

    def test_clear_cache(self):
        """Test clearing cache."""
        cache = CacheManager()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        assert cache.size() == 2
        
        cache.clear()
        assert cache.size() == 0

    def test_exists_method(self):
        """Test exists method."""
        cache = CacheManager()
        
        assert cache.exists('test_key') is False
        
        cache.set('test_key', 'test_value')
        assert cache.exists('test_key') is True
        
        # Test with expired key
        cache.set('expire_key', 'value', ttl=1)
        time.sleep(1.1)
        assert cache.exists('expire_key') is False

    def test_get_ttl(self):
        """Test getting TTL for keys."""
        cache = CacheManager()
        
        cache.set('test_key', 'test_value', ttl=10)
        ttl = cache.get_ttl('test_key')
        assert ttl is not None
        assert 0 < ttl <= 10
        
        assert cache.get_ttl('nonexistent') is None

    def test_set_ttl(self):
        """Test updating TTL for existing keys."""
        cache = CacheManager()
        
        cache.set('test_key', 'test_value', ttl=1)
        assert cache.set_ttl('test_key', 10) is True
        
        ttl = cache.get_ttl('test_key')
        assert ttl is not None
        assert 0 < ttl <= 10
        
        assert cache.set_ttl('nonexistent', 10) is False

    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = CacheManager()
        
        cache.set('valid_key', 'value', ttl=10)
        cache.set('expire_key', 'value', ttl=1)
        
        time.sleep(1.1)
        
        removed = cache.cleanup_expired()
        assert removed == 1
        assert cache.size() == 1
        assert cache.get('valid_key') == 'value'
        assert cache.get('expire_key') is None

    def test_keys_values_items(self):
        """Test getting keys, values, and items."""
        cache = CacheManager()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        keys = cache.keys()
        values = cache.values()
        items = cache.items()
        
        assert set(keys) == {'key1', 'key2', 'key3'}
        assert set(values) == {'value1', 'value2', 'value3'}
        assert set(items) == {('key1', 'value1'), ('key2', 'value2'), ('key3', 'value3')}

    def test_get_stats(self):
        """Test cache statistics."""
        cache = CacheManager()
        
        # Empty cache stats
        stats = cache.get_stats()
        assert stats['total_items'] == 0
        assert stats['memory_usage'] == 0
        assert stats['oldest_item'] is None
        assert stats['newest_item'] is None
        assert stats['average_ttl'] == 0
        
        # Non-empty cache stats
        cache.set('key1', 'value1', ttl=10)
        cache.set('key2', 'value2', ttl=20)
        
        stats = cache.get_stats()
        assert stats['total_items'] == 2
        assert stats['memory_usage'] > 0
        assert stats['oldest_item'] is not None
        assert stats['newest_item'] is not None
        assert stats['average_ttl'] > 0

    def test_set_many(self):
        """Test setting multiple key-value pairs."""
        cache = CacheManager()
        
        items = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
        cache.set_many(items)
        
        assert cache.size() == 3
        assert cache.get('key1') == 'value1'
        assert cache.get('key2') == 'value2'
        assert cache.get('key3') == 'value3'

    def test_get_many(self):
        """Test getting multiple values."""
        cache = CacheManager()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        result = cache.get_many(['key1', 'key3', 'nonexistent'])
        assert result == {'key1': 'value1', 'key3': 'value3'}

    def test_delete_many(self):
        """Test deleting multiple keys."""
        cache = CacheManager()
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')
        
        deleted = cache.delete_many(['key1', 'key3', 'nonexistent'])
        assert deleted == 2
        assert cache.size() == 1
        assert cache.get('key2') == 'value2'

    def test_set_with_pattern(self):
        """Test setting value with generated key pattern."""
        cache = CacheManager()
        
        key = cache.set_with_pattern('test', 'value')
        assert key.startswith('test_')
        assert len(key) > len('test_')
        assert cache.get(key) == 'value'

    def test_get_by_pattern(self):
        """Test getting keys matching pattern."""
        cache = CacheManager()
        
        cache.set('test_key1', 'value1')
        cache.set('test_key2', 'value2')
        cache.set('other_key', 'value3')
        
        result = cache.get_by_pattern('test_*')
        assert result == {'test_key1': 'value1', 'test_key2': 'value2'}
        
        result = cache.get_by_pattern('*_key1')
        assert result == {'test_key1': 'value1'}

    def test_delete_by_pattern(self):
        """Test deleting keys matching pattern."""
        cache = CacheManager()
        
        cache.set('test_key1', 'value1')
        cache.set('test_key2', 'value2')
        cache.set('other_key', 'value3')
        
        deleted = cache.delete_by_pattern('test_*')
        assert deleted == 2
        assert cache.size() == 1
        assert cache.get('other_key') == 'value3'

    def test_complex_data_types(self):
        """Test caching complex data types."""
        cache = CacheManager()
        
        # Test dict
        test_dict = {'key': 'value', 'number': 123}
        cache.set('dict_key', test_dict)
        assert cache.get('dict_key') == test_dict
        
        # Test list
        test_list = [1, 2, 3, 'string']
        cache.set('list_key', test_list)
        assert cache.get('list_key') == test_list
        
        # Test tuple (converted to list by JSON)
        test_tuple = (1, 2, 3)
        cache.set('tuple_key', test_tuple)
        result = cache.get('tuple_key')
        assert result == [1, 2, 3]  # Tuple becomes list

    def test_unicode_handling(self):
        """Test Unicode string handling."""
        cache = CacheManager()
        
        unicode_text = '测试中文 🎉'
        cache.set('unicode_key', unicode_text)
        assert cache.get('unicode_key') == unicode_text

    def test_large_values(self):
        """Test caching large values."""
        cache = CacheManager()
        
        large_string = 'x' * 10000
        cache.set('large_key', large_string)
        assert cache.get('large_key') == large_string

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        cache = CacheManager()
        
        # Test empty key
        cache.set('', 'value')
        assert cache.get('') == 'value'
        
        # Test None value
        cache.set('none_key', None)
        assert cache.get('none_key') is None
        
        # Test zero TTL
        cache.set('zero_ttl', 'value', ttl=0)
        time.sleep(0.1)
        assert cache.get('zero_ttl') is None


class TestCacheDecorator:
    """Test cache result decorator."""

    def test_cache_decorator_basic(self):
        """Test basic cache decorator functionality."""
        call_count = 0
        
        @cache_result(ttl=10)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call should execute function
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call should use cache
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Should not increment
        
        # Different arguments should execute function
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2

    def test_cache_decorator_with_kwargs(self):
        """Test cache decorator with keyword arguments."""
        call_count = 0
        
        @cache_result(ttl=10)
        def function_with_kwargs(a, b=1, c=2):
            nonlocal call_count
            call_count += 1
            return a + b + c
        
        result1 = function_with_kwargs(1, b=3, c=4)
        assert result1 == 8
        assert call_count == 1
        
        # Same arguments should use cache
        result2 = function_with_kwargs(1, b=3, c=4)
        assert result2 == 8
        assert call_count == 1
        
        # Different kwargs should execute function
        result3 = function_with_kwargs(1, b=5, c=4)
        assert result3 == 10
        assert call_count == 2

    def test_cache_decorator_with_prefix(self):
        """Test cache decorator with key prefix."""
        call_count = 0
        
        @cache_result(ttl=10, key_prefix="test_")
        def prefixed_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        result = prefixed_function(5)
        assert result == 10
        assert call_count == 1
        
        # Check that cache key exists with prefix
        keys = cache_manager.keys()
        prefixed_keys = [k for k in keys if k.startswith('test_')]
        assert len(prefixed_keys) == 1


class TestUtilityFunctions:
    """Test utility functions."""

    def test_cache_json_functions(self):
        """Test JSON caching functions."""
        test_data = {'key': 'value', 'number': 123}
        
        cache_json('json_key', test_data, ttl=10)
        result = get_cached_json('json_key')
        
        assert result == test_data
        
        # Test non-existent key
        assert get_cached_json('nonexistent') is None
        
        # Test invalid JSON
        cache_manager.set('invalid_json', 'invalid json string')
        assert get_cached_json('invalid_json') is None

    def test_cache_query_functions(self):
        """Test query caching functions."""
        query_result = {'id': 1, 'name': 'test'}
        
        cache_query_result('user_query', query_result, ttl=10)
        result = get_cached_query('user_query')
        
        assert result == query_result
        
        # Test non-existent query
        assert get_cached_query('nonexistent_query') is None

    def test_invalidate_cache_pattern(self):
        """Test cache pattern invalidation."""
        cache_manager.set('test_key1', 'value1')
        cache_manager.set('test_key2', 'value2')
        cache_manager.set('other_key', 'value3')
        
        invalidated = invalidate_cache_pattern('test_*')
        assert invalidated == 2
        assert cache_manager.size() == 1
        assert cache_manager.get('other_key') == 'value3'


class TestPerformanceAndEdgeCases:
    """Test performance and edge cases."""

    def test_high_volume_operations(self):
        """Test high volume cache operations."""
        cache = CacheManager()
        
        # Test setting many items
        start_time = time.time()
        for i in range(1000):
            cache.set(f'key_{i}', f'value_{i}')
        set_time = time.time() - start_time
        
        # Test getting many items
        start_time = time.time()
        for i in range(1000):
            cache.get(f'key_{i}')
        get_time = time.time() - start_time
        
        # Should complete within reasonable time
        assert set_time < 1.0  # 1 second
        assert get_time < 1.0  # 1 second
        assert cache.size() == 1000

    def test_concurrent_access_simulation(self):
        """Test simulated concurrent access."""
        cache = CacheManager()
        
        # Simulate concurrent access by rapid operations
        for i in range(100):
            cache.set(f'concurrent_key_{i}', f'value_{i}')
            cache.get(f'concurrent_key_{i}')
            cache.delete(f'concurrent_key_{i}')
        
        # Cache should be empty after all deletions
        assert cache.size() == 0

    def test_memory_efficiency(self):
        """Test memory efficiency with large cache."""
        cache = CacheManager()
        
        # Add large items
        for i in range(100):
            large_value = 'x' * 1000
            cache.set(f'large_key_{i}', large_value)
        
        stats = cache.get_stats()
        assert stats['total_items'] == 100
        assert stats['memory_usage'] > 0
        
        # Clear and check memory is freed
        cache.clear()
        stats = cache.get_stats()
        assert stats['total_items'] == 0
        assert stats['memory_usage'] == 0

    def test_ttl_precision(self):
        """Test TTL precision and edge cases."""
        cache = CacheManager()
        
        # Test very short TTL
        cache.set('short_ttl', 'value', ttl=0.1)
        assert cache.get('short_ttl') == 'value'
        
        time.sleep(0.2)
        assert cache.get('short_ttl') is None
        
        # Test very long TTL
        cache.set('long_ttl', 'value', ttl=3600)  # 1 hour
        ttl = cache.get_ttl('long_ttl')
        assert ttl is not None
        assert 3500 < ttl <= 3600

    def test_key_collision_prevention(self):
        """Test that different functions don't collide in cache."""
        call_count1 = 0
        call_count2 = 0
        
        @cache_result(ttl=10, key_prefix="func1_")
        def function1(x):
            nonlocal call_count1
            call_count1 += 1
            return x * 2
        
        @cache_result(ttl=10, key_prefix="func2_")
        def function2(x):
            nonlocal call_count2
            call_count2 += 1
            return x * 3
        
        result1 = function1(5)
        result2 = function2(5)
        
        assert result1 == 10
        assert result2 == 15
        assert call_count1 == 1
        assert call_count2 == 1
        
        # Second calls should use cache
        result1_again = function1(5)
        result2_again = function2(5)
        
        assert result1_again == 10
        assert result2_again == 15
        assert call_count1 == 1  # Should not increment
        assert call_count2 == 1  # Should not increment
