import redis
import ast

from django.conf import settings


class RedisSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(RedisSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Redis(metaclass=RedisSingleton):

    connection = None

    def __init__(self):
        self.connect = self.connect()

    def connect(self):
        if self.connection is None:
            self.connection = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)
        return self.connection

    def get_value_from_key_as_str(self, key):
        data = self.connect.get(key)
        if data:
            data = ast.literal_eval(data.decode("utf-8"))
            return data
        return None

    def set_value(self, key, value):
        if type(value) == dict:
            value = str(value).encode("utf-8")
        self.connect.set(key, value)
