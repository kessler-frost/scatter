from diskcache import FanoutCache
import msgspec
import cloudpickle as pickle


if __name__ == "__main__":

    cache = FanoutCache("disk_cache")

    decoder = msgspec.msgpack.Decoder()

    a = 1
    b = 2

    for i in range(100_000):
        key = f"my_node_{i}"
        encoded_node = cache.get(key)
        node = decoder.decode(encoded_node)
        node["node_func"] = pickle.loads(node["node_func"])

    # print(node["node_func"](a, b))
