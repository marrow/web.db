#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import os
import sys
import codecs


try:
	from setuptools.core import setup, find_packages
except ImportError:
	from setuptools import setup, find_packages

from setuptools.command.test import test as TestCommand


if sys.version_info < (2, 7):
	raise SystemExit("Python 2.7 or later is required.")
elif sys.version_info > (3, 0) and sys.version_info < (3, 3):
	raise SystemExit("Python 3.3 or later is required.")

version = description = url = author = author_email = ""  # Silence linter warnings.
exec(open(os.path.join("web", "db", "release.py")).read())


class PyTest(TestCommand):
	def finalize_options(self):
		TestCommand.finalize_options(self)
		
		self.test_args = []
		self.test_suite = True
	
	def run_tests(self):
		import pytest
		sys.exit(pytest.main(self.test_args))


here = os.path.abspath(os.path.dirname(__file__))

tests_require = [
		'pytest',  # test collector and extensible runner
		'pytest-cov',  # coverage reporting
		'pytest-flakes',  # syntax validation
		'pytest-cagoule',  # intelligent test execution
		'pytest-spec',  # output formatting
	]


setup(
	name = "web.db",
	version = version,
	description = description,
	long_description = codecs.open(os.path.join(here, 'README.rst'), 'r', 'utf8').read(),
	url = url,
	download_url = 'https://github.com/marrow/web.db/releases',
	author = author.name,
	author_email = author.email,
	license = 'MIT',
	keywords = ['marrow', 'web.ext', 'web.db'],
	classifiers = [
			"Development Status :: 5 - Production/Stable",
			"Environment :: Console",
			"Environment :: Web Environment",
			"Intended Audience :: Developers",
			"License :: OSI Approved :: MIT License",
			"Operating System :: OS Independent",
			"Programming Language :: Python",
			"Programming Language :: Python :: 2",
			"Programming Language :: Python :: 2.7",
			"Programming Language :: Python :: 3",
			"Programming Language :: Python :: 3.2",
			"Programming Language :: Python :: 3.3",
			"Programming Language :: Python :: 3.4",
			"Programming Language :: Python :: 3.5",
			"Programming Language :: Python :: Implementation :: CPython",
			"Programming Language :: Python :: Implementation :: PyPy",
			"Topic :: Software Development :: Libraries",
			"Topic :: Software Development :: Libraries :: Python Modules",
		],
	
	packages = find_packages(exclude=['bench', 'doc', 'example', 'test']),
	include_package_data = True,
	namespace_packages = [
			'web',  # primary namespace
			'web.db',  # database adapter namespace
			'web.ext',  # extension namespace
		],
	zip_safe = True,
	cmdclass = dict(
			test = PyTest,
		),
	
	entry_points = {
		'web.extension': [  # WebCore Framework Extensions
				'db = web.ext.db:DatabaseExtension',
			],
		
		'web.db': [  # Database Connectors
				'sqlalchemy = web.db.sa:SQLAlchemyDBConnection',
				'mongoengine = web.db.me:MongoEngineDBConnection',
				'sqlite3 = web.db.dbapi:SQLite3Connection',
			],
		},
	
	install_requires = [
			'marrow.package<2.0',  # dynamic execution and plugin management
			'WebOb',  # HTTP request and response objects, and HTTP status code exceptions
		],
	tests_require = tests_require,
	
	extras_require = dict(
			development = tests_require,
		),
)