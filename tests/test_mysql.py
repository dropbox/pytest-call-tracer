from __future__ import absolute_import

import MySQLdb

from unittest import TestCase


class MySQLdbSampleTest(TestCase):
    def setUp(self):
        self.client = MySQLdb.connect()

    def test_simple(self):
        self.client.query('select 1')
        r = self.client.use_result()
        assert r.fetch_row() == ((1,), )
