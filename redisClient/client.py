import redis
from django.conf import settings
import pickle
from datetime import timedelta
class RedisClient:
    def __init__(self,hostname=settings.REDIS_HOST,port=settings.REDIS_PORT,db=settings.REDIS_DB,password=settings.REDIS_PASSWORD):
        client = redis.Redis(hostname,port,db,password)
        self.client=client

    def setkey(self,key,value,ttl=timedelta(days=7)):
        value_bin = pickle.dumps(value)
        res = self.client.setex(key,ttl,value_bin)
        return res
    def getkey(self,key):
        value_bin = self.client.get(key)
        if value_bin:
            return pickle.loads(value_bin)
        return None
        