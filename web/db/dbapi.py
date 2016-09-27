# encoding: utf-8

import re

from marrow.package.loader import load


log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class _DBAPIConnection(object):
	"""WebCore DBExtension interface for projects utilizing DB-API database engines."""
	
	api = None  # Must be defined in subclasses.
	uri_safety = True  # Go to some effort to hide connection passwords from logs.
	thread_safe = True  # When False, create a connection for the duration of the request only.
	
	def __init__(self, uri, alias=None, **kw):
		"""Prepare configuration options."""
		
		self.uri = uri
		self._alias = alias
		self._config = kw
		self._connector = load(self.api, 'db_api_connect')
		
		if __debug__ and not self.api:
			raise NotImplementedError("Use subclasses of _DBAPIConnection, not the class itself.")
		
		if self.thread_safe:
			self.start = self._connect
			self.stop = self._disconnect
		else:
			self.prepare = self._connect
			self.done = self._disconnect
	
	def _connect(self, context):
		"""Initialize the database connection."""
		
		# Only after passing to the DatabaseExtension intializer do we have a __name__...
		name = self.name = self._alias or self.__name__
		
		if self.thread_safe or __debug__:
			log.info("Connecting " + self.api.partition(':')[0] + " database layer.", extra=dict(
					uri = _safe_uri_replace.sub(r'\1://\2@', self.uri) if self.uri_safety else self.uri,
					config = self._config,
					name = name,
				))
		
		self.connection = context.db[name] = self._connector(self.uri, **self._config)
	
	def _disconnect(self, context):
		"""Close the connection and clean up references."""
		
		self.connection.close()
		del self.connection


class SQLite3Connection(_DBAPIConnection):
	api = 'sqlite3:connect'
	uri_safety = False
	thread_safe = False

