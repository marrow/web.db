# encoding: utf-8

from __future__ import unicode_literals

from web.core import Application
from web.ext.db import DatabaseExtension
from web.db.dbapi import SQLite3Connection


class TestSQLite3Connection(object):
	def test_repr(self):
		con = SQLite3Connection(':memory:', 'test')
		assert repr(con) == 'SQLite3Connection(test, "sqlite3:connect", ":memory:")'
	
	def test_lifecycle(self):
		Application("Hi.", extensions=[DatabaseExtension(default=SQLite3Connection(':memory:'))])

