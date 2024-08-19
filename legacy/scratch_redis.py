import redis

if __name__ == '__main__':
    r = redis.StrictRedis()
    r.set("foo", "bar")
    val = r.get("*")
    # print(val)

    # Delete all values
    r.flushall()

    # Get all keys
    keys = r.keys("*")
    print(keys)

    r.shutdown()
