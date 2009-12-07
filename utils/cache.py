import time
import logging

from models import Cache

class CacheManager(object):
    def get(self, key, check_expire=False):
        logging.warning("Getting cache: %s" % key)
        spec = {'key': key}
        if check_expire:
            spec.update({'expire':{'$gt': time.time()}})
        ob = Cache.one(spec)
        if ob:
            logging.warning("Cache HIT")
            return ob.value
        logging.warning("Cache MISSED")
        return None
    
    def set(self, key, value, expire_offset=None):
        logging.warning("Setting cache: %s" % key)
        expire = expire_offset + time.time() if expire_offset else None
        ob = Cache({'key': key, 'value': value, 'expire': expire})
        ob.save() 