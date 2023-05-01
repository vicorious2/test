from rediscluster import RedisCluster
import os
from app.constant import Constant
from .loggerFactory import LoggerFactory


logger = LoggerFactory.get_logger(__name__)
env = os.getenv("PA_ENV", "dev")

ttl = 60 * 60 * 6


class RedisClusterConnection:
    instance = None

    class __OnlyOne:
        _redis_connection = None
        _result = {}
        _ttl = 60 * 60 * 6

        def __init__(self):
            self._redis_connection = redis()

        def __str__(self):
            return repr(self)

        def execute_function(self, key, function):
            if self._redis_connection.get(key):
                self._result = self._redis_connection.get(key)
            else:
                self._result = function()
            self._redis_connection.set(key, self._result, self._ttl)

    def __init__(self):
        if not RedisClusterConnection.instance:
            RedisClusterConnection.instance = RedisClusterConnection.__OnlyOne()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def clear_cache(key: str):
        RedisClusterConnection.instance._redis_connection.delete(key)

    def clear_all_cache():
        for key in RedisClusterConnection.instance._redis_connection.scan_iter(
            f"{Constant.REDIS_KEY_PREFIX}*"
        ):
            RedisClusterConnection.instance._redis_connection.delete(key)

    def print_object_address():
        print(RedisClusterConnection.instance)

    def get_instance(self):
        return RedisClusterConnection.instance


def redis():
    # endpoint can be an environment variable for prod, dev,test
    end_point = ""
    if env == "dev":
        end_point = (
            "sensing-application-cache.d9apv4.clustercfg.usw2.cache.amazonaws.com"
        )
    elif env == "test":
        end_point = (
            "sensing-application-cache-test.d9apv4.clustercfg.usw2.cache.amazonaws.com"
        )
    elif env == "staging":
        end_point = (
            "sensing-application-cache-stg.d9apv4.clustercfg.usw2.cache.amazonaws.com"
        )
    elif env == "rts":
        end_point = (
            "sensing-application-cache-prd.d9apv4.clustercfg.usw2.cache.amazonaws.com"
        )

    redis = RedisCluster(
        startup_nodes=[{"host": end_point, "port": 6379}],
        decode_responses=True,
        skip_full_coverage_check=True,
    )
    return redis
