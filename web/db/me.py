# encoding: utf-8

import re

try:
	from mongoengine import connect, disconnect
except ImportError:
	raise ImportError('Unable to import mongoengine; pip install mongoengine to fix this.')


log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class MongoEngineDBConnection(object):
	"""WebCore DBExtension interface for projects utilizing MongoEngine.
	
	URI-style connection strings should always be utilized. Provide a `replicaSet` query string argument to enable
	replica set functionality. The alias name is preserved through to MongoEngine to allow use of database switching
	mechanisms, such as the `switch_db` context manager, and multiple instances may be used to populate the
	`DatabaseExtension` connections.
	
	Any additional keyword arguments used are passed through to `mongoengine.connect`, which in turn passes the values
	along to `mongoengine.connection.register_connection` for further processing.
	"""
	
	def __init__(self, uri, alias=None, **kw):
		"""Prepare configuration options."""
		
		kw['host'] = uri
		
		self._alias = alias
		self._config = kw
	
	def start(self, context):
		"""Initialize the database connection."""
		
		# Only after passing to the DatabaseExtension intializer do we have a __name__...
		name = self.name = self._alias or self.__name__
		self._config['alias'] = name
		
		log.info("Connecting MongoEngine database layer.", extra=dict(
				uri = _safe_uri_replace.sub(r'\1://\2@', self.uri),
				config = self._config,
			))
		
		self.connection = connect(**self._config)
	
	def prepare(self, context):
		"""Attach this connection's default database to the context using our alias."""
		
		context.db[self.name] = self.connection.get_default_database()
	
	def stop(self, context):
		"""Close the connection pool and clean up references in MongoEngine."""
		
		disconnect(self.name)
		del self.connection

