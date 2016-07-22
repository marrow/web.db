from sqlalchemy import create_engine, orm

log = __import__('logging').getLogger(__name__)


class SQLAlchemyDBConnection(object):
	"""WebCore DBExtension interface for sqlalchemy based projects.

	Creates a connection at startup then adds a sqlalchemy session to the WebCore context on each request, for seamless
	 ORM and relational DB support.
	"""
	def __init__(self, uri, alias=None, **kw):
		self.uri = uri
		self.engine = None
		self.config = kw
		self.alias = alias

	def start(self, context):
		"""Setup database connection and Session base class"""

		name = self.name = self.alias or self.__name__

		log.info("Connecting SQLAlchemy engine.", extra=dict(config=self.config,))

		engine = self.engine = create_engine(self.uri, **self.config)
		self.Session = orm.scoped_session(orm.sessionmaker(bind=engine))

		if self.config.get('connect', True):
			pass  # Log extra details about the connection here.

		# context.db[name] = engine if engine is not None

	def prepare(self, context):
		"""Prepare a sqlalchemy session on the WebCore context"""

		context.db[self.name] = self.Session()

	def done(self, context):
		"""Commit the session transaction for the request"""

		context.db[self.name].commit()
		context.db[self.name].close()


	def stop(self, context):
		self.engine.dispose()
