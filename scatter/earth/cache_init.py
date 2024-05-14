import redis
from scatter.constants import REDIS_HOST, REDIS_PORT, REDIS_DB
from redis_cache import RedisCache

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
cache = RedisCache(redis_client=redis_client)
