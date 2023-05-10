#!/usr/bin/env python3
"""
Writing strings to Redis
"""
import redis
from uuid import uuid4
from typing import Union, Callable, Any
from functools import wraps


def count_call(method: Callable) -> Callable:
    """
    Keeps record of the number of calls mad to a method in Cache class
    """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """Invokes the given method after incrementing its call counter.
        """
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    """
    Tracks the call details of a method in a Cache class.
    """
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """
        Returns the method's output after storing its inputs and output.
        """
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    """
    Displays the call history of a Cache class' method.
    """
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = '{}:inputs'.format(fxn_name)
    out_key = '{}:outputs'.format(fxn_name)
    fxn_call_count = 0
    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        print('{}(*{}) -> {}'.format(
            fxn_name,
            fxn_input.decode("utf-8"),
            fxn_output,
        ))


class Cache:
    """
    Initialize a class instance
    """
    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_call
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        generate a random key (e.g. using uuid),store the
        input data in Redis using the random key
        and return the key.
        """
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self,
            key: str,
            fn: Callable = None) -> Union[str, bytes, int, float]:
        """
        Get value from Redis DB using key
        """
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """
        Get string value from Redis DB
        """
        return self._redis.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: int) -> int:
        """
        Get integer value from Redis DB
        """
        return self._redis.get(key, lambda x: int(x))
