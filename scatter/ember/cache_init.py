import redis
from redis_cache import RedisCache

from scatter.ember.constants import REDIS_DB, REDIS_HOST, REDIS_PORT

redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
cache = RedisCache(redis_client=redis_client)
