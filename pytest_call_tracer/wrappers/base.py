from __future__ import absolute_import

from time import time


class Wrapper(object):
    """Wraps methods and logs the results """
    name = None

    def __init__(self, data, name=None):
        self.data = data
        if name is not None:
            self.name = name

    def record(self, data):
        if 'type' not in data:
            data['type'] = self.name
        self.data.append(data)


class FunctionWrapper(Wrapper):
    def __call__(self, func, *args, **kwargs):
        __traceback_hide__ = True  # NOQA

        start = time()
        try:
            return func(*args, **kwargs)
        finally:
            end = time()

            if getattr(func, 'im_class', None):
                arg_str = repr(args[1:])
            else:
                arg_str = repr(args)

            data = {
                'type': self.name or func.__name__,
                'name': func.__name__,
                'args': arg_str,
                'kwargs': repr(kwargs),
                'start': start,
                'end': end,
            }

            self.record(data)
