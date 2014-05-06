from __future__ import absolute_import

import time
from pytest_call_tracer.wrappers.base import Wrapper


class RedisPipelineWrapper(Wrapper):
    name = 'redis'

    def __call__(self, func, pipeline, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        command_stack = pipeline.command_stack[:]

        start = time.time()
        try:
            return func(pipeline, *args, **kwargs)
        finally:
            end = time.time()

            data = {
                'name': 'pipeline',
                'args': repr(command_stack),
                'kwargs': repr({}),
                'start': start,
                'end': end,
            }

            self.record(data)


class RedisWrapper(Wrapper):
    name = 'redis'

    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        start = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time.time()

            data = {
                'name': args[1],
                'args': repr(args[2:]),
                'kwargs': repr(kwargs),
                'start': start,
                'end': end,
            }
            self.record(data)
