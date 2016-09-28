# encoding: utf-8

try:
	from sqlalchemy import create_engine, orm, MetaData
except ImportError:
	raise ImportError('Unable to import sqlalchemy; pip install sqlalchemy to fix this.')

log = __import__('logging').getLogger(__name__)


class SQLAlchemyConnection(object):
	"""WebCore DBExtension interface for sqlalchemy based projects.
	
	Creates a connection at startup then adds a sqlalchemy session to the WebCore context on each request, for seamless
	ORM and relational DB support.
	"""
	def __init__(self, uri, session=None, metadata=None, session_opts={}, alias=None, **kw):
		if session is not None and not isinstance(session, orm.scoping.ScopedSession):
			raise TypeError('The "session" option needs to be a reference to a ScopedSession instance')
		if metadata is not None and not isinstance(metadata, MetaData):
			raise TypeError('The "metadata" option needs to be a reference to a MetaData instance')
		if not isinstance(session_opts, dict):
			raise TypeError('The "session_opts" option needs to be a dictionary')
		
		self.uri = uri
		self._engine = create_engine(uri, **kw)
		self._config = kw
		self._alias = alias
		self._metadata = metadata
		self._session = session
		self._session_opts = session_opts
	
	def start(self, context):
		"""Setup database connection and Session base class"""
		
		name = self.name = self._alias or self.__name__
		
		log.info("Connecting SQLAlchemy engine.", extra=dict(config=self._config,))
		self._engine.connect().close()
		
		if self._session is None:
			self._session = orm.scoped_session(orm.sessionmaker(**self._session_opts))
		
		self._session.configure(bind=self._engine)
		
		if self._metadata is not None:
			self._metadata.bind = self._engine
		
		if self._config.get('connect', True):
			pass  # Log extra details about the connection here.
		
		# context.db[name] = engine if engine is not None
	
	def prepare(self, context):
		"""Prepare a sqlalchemy session on the WebCore context"""
		
		context.db[self.name] = self._session()
	
	def done(self, context, exc=None):
		"""Commit the session transaction for the request"""
		
		# TODO: I don't believe exc is an actual value that WebCore gives us...
		try:
			if context.db[self.name].is_active:
				if exc is None or isinstance(exc, HTTPException):
					context.db[self.name].commit()
				else:
					context.db[self.name].rollback()
		finally:
			context.db[self.name].close()
	
	def stop(self, context):
		self._engine.dispose()
