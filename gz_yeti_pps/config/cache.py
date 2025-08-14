"""
Module for the configuration of the various caches used in the application/library.

Author:
    Taylor-Jayde Blackstone (t.blackstone@inspyre.tech)

Since:
    v1.0.0

Exports:
    - CacheConfig
    - GetCacheConfig
    - StateCacheConfig
    - CONN_CHECK_CACHE_SPEC
    - GET_CACHE_SPEC
    - STATE_CACHE_SPEC
"""
from .spec import CONFIG_SPECS


CONN_CHECK_CACHE_SPEC = CONFIG_SPECS['conn_check_cache']
GET_CACHE_SPEC        = CONFIG_SPECS['get_cache']
STATE_CACHE_SPEC      = CONFIG_SPECS['state_cache']


CACHE_CONFIG_SPECS = {
    'conn_check': CONN_CHECK_CACHE_SPEC,
    'get': GET_CACHE_SPEC,
    'state': STATE_CACHE_SPEC,
}
