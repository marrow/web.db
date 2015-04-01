# encoding: utf-8

import re
from mongoengine import connect

from marrow.package.loader import load
from web.core.compat import native, items


log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class MongoEngineExtension:
	__slots__ = ('uri', 'db', 'connection', 'cb')
	
	provides = ['db']
	
	def __init__(self, uri, **config):
		log.info("Connecting MongoEngine to '%s'.", _safe_uri_replace.sub(r'\1://\2@', uri))
		
		self.uri = uri
		self.cb = config.pop('ready', None)
		self.connection = dict(config, host=uri, tz_aware=True)
		
		_, _, self.db = uri.rpartition('/')
	
	def start(self, context):
		db, connection = self.db, self.connection
		
		context.mongoengine = connect(db, **connection)
		
		cb = self.cb
		if cb is not None:
			cb = load(cb) if isinstance(cb, native) else cb
			
			if hasattr(cb, '__call__'):
				cb()
