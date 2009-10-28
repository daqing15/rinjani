from settings import app_settings
from beaker.cache import CacheManager
from beaker.util import parse_cache_config_options

cache = CacheManager(**parse_cache_config_options(app_settings['cache_opts']))
