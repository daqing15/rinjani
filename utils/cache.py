import time
import logging

from models import Cache
import redis

default_ttl = 600

class MongoCacheManager(object):
    def get(self, key):
        spec = {'_id': key, 'expire':{'$gt': time.time()}}
        ob = Cache.one(spec)
        if ob:
            return ob.value
        return None
    
    def set(self, key, value, ttl=None):
        expire = time.time()
        expire += ttl if ttl else default_ttl 
        ob = Cache({'_id': key, 'value': value, 'expire': expire})
        ob.save() 

class RedisCacheManager(object):
    def __init__(self):
        self.redis = redis.Redis()
    
    def get(self, key):
        return self.redis.get(key)
    
    def set(self, key, value, ttl=None):
        ttl = ttl if ttl else default_ttl
        self.redis.set(key, value, ttl)
                
cachemanager = RedisCacheManager()