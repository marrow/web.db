# encoding: utf-8

from web.ext.db import DatabaseExtension


class TestDatabaseExtension(object):
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

