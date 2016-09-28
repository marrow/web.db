# encoding: utf-8

from __future__ import unicode_literals

import pytest

from web.core.context import Context
from web.db.me import MongoEngineConnection
from web.ext.db import DatabaseExtension

from mongoengine import Document, StringField



class Sample(Document):
	name = StringField()



@pytest.fixture
def db():
	"""Get the mid-request context.db object."""
	
	ctx = Context()
	db = DatabaseExtension(MongoEngineConnection('mongodb://localhost/test'))
	db.start(ctx)
	db.prepare(ctx)
	
	yield ctx.db.default
	
	db.stop(ctx)



class TestMongoEngineConnection(object):
	def test_connection_lifecycle(self, db):
		assert db._connection


