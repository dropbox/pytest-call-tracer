from __future__ import absolute_import

import py
import json

from time import time

from pytest_call_tracer.util import PatchContext
from pytest_call_tracer.wrappers.base import FunctionWrapper


def pytest_addoption(parser):
    group = parser.getgroup("call tracing")
    group.addoption(
        '--tracing', action="store_true", dest="tracing", default=False)
    group.addoption(
        '--trace-output', action="store", dest="trace_output")


def pytest_configure(config):
    if not config.option.tracing:
        return
    config._tracer = TracingPlugin(config.option.trace_output)
    config.pluginmanager.register(config._tracer)


def pytest_unconfigure(config):
    tracer = getattr(config, '_tracer', None)
    if not tracer:
        return
    del config._tracer
    config.pluginmanager.unregister(tracer)


class TracingPlugin(object):
    def __init__(self, logfile=None):
        self.logfile = logfile
        self.tests = []
        self.context_stack = []

    def pytest_runtest_setup(self, item):
        self.begin_tracing(item)

    def pytest_runtest_teardown(self, item):
        self.end_tracing(item)

    def pytest_sessionstart(self):
        self.suite_start_time = time()

    def pytest_sessionfinish(self):
        if not self.logfile:
            return

        if py.std.sys.version_info[0] < 3:
            logfile = py.std.codecs.open(self.logfile, 'w', encoding='utf-8')
        else:
            logfile = open(self.logfile, 'w', encoding='utf-8')

        logfile.write(json.dumps(self.tests, indent=2))
        logfile.close()

    def pytest_terminal_summary(self, terminalreporter):
        if self.logfile:
            terminalreporter.write_sep("-", "generated tracing report file: %s" % (self.logfile))
            return

        def trim(string, length):
            s_len = len(string)
            if s_len < length:
                return string
            return '...' + string[s_len - length:]

        print
        print 'Highest call counts'
        print '-' * 80
        for test in sorted(self.tests, key=lambda x: len(x['calls']), reverse=True)[:25]:
            print '%-74s %d' % (trim(test['id'], 70), len(test['calls']))


    def patch_interfaces(self):
        self._calls = []

        try:
            __import__('redis')
        except ImportError:
            pass
        else:
            self.patch_redis_interfaces()

        try:
            __import__('MySQLdb')
        except ImportError:
            pass
        else:
            self.patch_mysqldb_interfaces()

        try:
            __import__('kazoo')
        except ImportError:
            pass
        else:
            self.patch_kazoo_interfaces()

    def patch_redis_interfaces(self):
        from pytest_call_tracer.wrappers.redis import RedisWrapper, RedisPipelineWrapper

        self.add_context(PatchContext('redis.client.StrictRedis.execute_command', RedisWrapper(self._calls)))
        self.add_context(PatchContext('redis.client.BasePipeline.execute', RedisPipelineWrapper(self._calls)))

    def patch_mysqldb_interfaces(self):
        self.add_context(PatchContext('MySQLdb.connections.Connection.query', FunctionWrapper(self._calls, 'mysql')))

    def patch_kazoo_interfaces(self):
        self.add_context(PatchContext('kazoo.client.KazooClient._call', FunctionWrapper(self._calls, 'kazoo')))

    def add_context(self, ctx):
        ctx.__enter__()
        self.context_stack.append(ctx)

    def clear_context(self):
        while self.context_stack:
            self.context_stack.pop().__exit__(None, None, None)

    def begin_tracing(self, item):
        self.patch_interfaces()

    def end_tracing(self, item):
        self.clear_context()

        data = {
            'id': item.nodeid,
            'calls': self._calls,
        }

        self.tests.append(data)
