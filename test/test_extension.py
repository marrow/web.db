# encoding: utf-8

import warnings

from web.core.context import Context
from web.ext.db import DatabaseExtension, DBExtension


class CustomConnection(object):
	def __init__(self):
		self.running = False
	
	def start(self, context):
		self.running = True
	
	def stop(self, context):
		self.running = False


class TestDatabaseExtension(object):
	def test_deprecation(self):
		with warnings.catch_warnings(record=True) as w:
			warnings.simplefilter("always")
			
			DBExtension()
			
			assert len(w) == 1
			assert issubclass(w[-1].category, DeprecationWarning)
			assert "DatabaseExtension" in str(w[-1].message)
	
	def test_construction(self):
		bare = DatabaseExtension()
		
		assert bare.engines == {}
		assert bare.uses == set()
		assert bare.needs == set()
		assert bare.provides == {'db'}
	
	def test_construction_engine_updates(self):
		class Connection(object):
			__slots__ = ('__name__', )
			uses = {'i-use-this'}
			needs = {'i-need-this'}
			provides = {'i-provide-this'}
		
		db = DatabaseExtension(Connection())
		
		assert db.engines
		assert 'default' in db.engines
		assert isinstance(db.engines['default'], Connection)
		assert db.uses == {'i-use-this'}
		assert db.needs == {'i-need-this'}
		assert db.provides == {'db', 'i-provide-this'}
	
	def test_start(self):
		db = DatabaseExtension(CustomConnection())
		ctx = Context()
		
		db.start(ctx)
		
		assert isinstance(ctx.db.default, CustomConnection)
		assert ctx.db.default.running

