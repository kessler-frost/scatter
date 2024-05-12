from diskcache import FanoutCache
from pathlib import Path


cache_dir = str(Path(__file__).parent / "disk_cache")
index_name = "versions_index"

cache = FanoutCache(cache_dir)
index = cache.index(index_name)
