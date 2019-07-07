import redis
import ast

from django.conf import settings


class Redis(redis.StrictRedis):

    def __init__(self):
        super(Redis, self).__init__()
        self.redis = self.connect()

    def connect(self):
        connection = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        return connection

    def get_value_from_key_as_str(self, key):
        data = self.redis.get(key)
        if data:
            data = ast.literal_eval(data.decode("utf-8"))
            return data
        return None

    def set_value(self, key, value):
        if type(value) == dict:
            value = str(value).encode("utf-8")
        self.redis.set(key, value)
