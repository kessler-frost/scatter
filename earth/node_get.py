from diskcache import FanoutCache
from earth.function_enc_dec import decoder

CACHE_NAME = "disk_cache"

NUM = 100_000
# NUM = 1

if __name__ == "__main__":

    # Using FanoutCache so that it can be accessed from multiple processes
    cache = FanoutCache(CACHE_NAME)

    a = 1
    b = 2

    for i in range(NUM):
        key = f"my_node_{i}"
        encoded_node = cache.get(key)
        node = decoder.decode(encoded_node)
        # print(node.node_func)

    # print(node["node_func"](a, b))

    # Remove the cache
    cache.clear()
