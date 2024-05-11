from diskcache import FanoutCache
from scatter.earth.function_enc_dec import encoder
from scatter.earth.node_struct import Node


CACHE_NAME = "disk_cache"

NUM = 100_000
# NUM = 1


if __name__ == "__main__":

    cache = FanoutCache(CACHE_NAME)

    def my_func(a: int, b: int) -> int:
        return a + b

    for i in range(NUM):
        node_info = Node(node_key=f"my_node_{i}", node_func=my_func)
        # print(node_info)
        cache[node_info.node_key] = encoder.encode(node_info)
