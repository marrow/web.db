# encoding: utf-8

import re

try:
	from sqlalchemy import create_engine
	from sqlalchemy.orm import scoped_session, sessionmaker
except ImportError:  # pragma: no cover
	raise ImportError('Unable to import sqlalchemy; pip install sqlalchemy to fix this.')


log = __import__('logging').getLogger(__name__)

_safe_uri_replace = re.compile(r'(\w+)://(\w+):(?P<password>[^@]+)@')


class SQLAlchemyConnection(object):
	"""SQLAlchemy database engine support for WebCore's DatabaseExtension."""
	
	__slots__ = ('name', 'uri', 'alias', 'config', 'engine', 'Session')
	
	def __init__(self, uri, alias=None, **config):
		"""Prepare SQLAlchemy configuration."""
		# def __init__(self, uri, session=None, metadata=None, session_opts=None, alias=None, **kw):
		
		config.setdefault('pool_recycle', 3600)
		
		self.uri = uri
		self.name = self.alias = alias
		self.config = config
		self.engine = None
		self.Session = None
	
	def __repr__(self):
		luri = _safe_uri_replace.sub(r'\1://\2@', self.uri) if '@' in self.uri and self.protect else self.uri
		return '{self.__class__.__name__}({self.name}, "{uri}")'.format(
				self = self,
				uri = luri,
			)
	
	def start(self, context):
		"""Construct the SQLAlchemy engine and session factory."""
		
		name = self.name = self.alias or self.__name__
		
		if __debug__:
			luri = _safe_uri_replace.sub(r'\1://\2@', self.uri) if '@' in self.uri and self.protect else self.uri
			log.info("Connecting SQLAlchemy database layer.", extra=dict(
					uri = luri,
					config = self.config,
					alias = name,
				))
		
		# Construct the engine.
		engine = self.engine = create_engine(self.uri, **self.config)
		
		# Construct the session factory.
		self.Session = scoped_session(sessionmaker(bind=engine))
		
		# Test the connection.
		engine.connect().close()
		
		# Assign the engine to our database alias.
		context.db[name] = engine
	
	def prepare(self, context):
		"""Prepare a sqlalchemy session on the WebCore context"""
		
		# Assign the session factory to our database alias.
		context.db[self.name] = self.Session
	
	def done(self, context):
		"""Close and clean up the request local session, if any."""
		
		context.db[self.name].remove()
	
	def stop(self, context):
		"""Disconnect any hanging connections in the pool."""
		
		self.engine.dispose()

