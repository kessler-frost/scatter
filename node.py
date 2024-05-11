from diskcache import FanoutCache
import msgspec
import cloudpickle as pickle

if __name__ == "__main__":

    def my_func(a: int, b: int) -> int:
        return a + b

    class Node(msgspec.Struct):
        node_key: str
        node_func: str

    encoder = msgspec.msgpack.Encoder()

    cache = FanoutCache("disk_cache")

    for i in range(100_000):
        node_info = Node(node_key=f"my_node_{i}", node_func=pickle.dumps(my_func))
        cache[node_info.node_key] = encoder.encode(node_info)
