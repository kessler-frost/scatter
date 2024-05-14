import redis

if __name__ == '__main__':
    r = redis.Redis()
    r.set('foo', 'bar')
    print(r.get('foo'))
