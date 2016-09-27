# encoding: utf-8

try:
	from sqlalchemy import create_engine, orm, MetaData
except ImportError:
	raise ImportError('Unable to import sqlalchemy; pip install sqlalchemy to fix this.')


log = __import__('logging').getLogger(__name__)


class SQLAlchemyDBConnection(object):
	"""WebCore DBExtension interface for sqlalchemy based projects.
	
	Creates a connection at startup then adds a sqlalchemy session to the WebCore context on each request, for seamless
	ORM and relational DB support.
	"""
	
	__slots__ = ('uri', 'engine', 'config', 'alias', 'metadata', 'session', 'session_opts')
	
	def __init__(self, uri, session=None, metadata=None, session_opts=None, alias=None, **kw):
		if session is not None and not isinstance(session, orm.scoping.ScopedSession):
			raise TypeError('The "session" option needs to be a reference to a ScopedSession instance')
		
		if metadata is not None and not isinstance(metadata, MetaData):
			raise TypeError('The "metadata" option needs to be a reference to a MetaData instance')
		
		self.uri = uri
		self.engine = create_engine(uri, **kw)
		self.config = kw
		self.alias = alias
		self.metadata = metadata
		self.session = session
		self.session_opts = session_opts or {}
	
	def start(self, context):
		"""Setup database connection and Session base class"""
		
		name = self.name = self._alias or self.__name__
		
		# TODO: More diagnostic information.
		log.info("Connecting SQLAlchemy engine.", extra=dict(name=name, config=self._config))
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
	
	def done(self, context):
		"""Commit the session transaction for the request."""
		
		# TODO: TransactionExtension support.
		
		try:
			if context.db[self.name].is_active:
				if context.response.status_int < 500:
					context.db[self.name].commit()
				else:
					context.db[self.name].rollback()
		finally:
			context.db[self.name].close()  # Not sure about this. -- Alice
	
	def stop(self, context):
		self._engine.dispose()
