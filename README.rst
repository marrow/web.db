======
web.db
======

    © 2009-2016 Alice Bevan-McGregor and contributors.

..

    https://github.com/marrow/web.db

..

    |latestversion| |ghtag| |masterstatus| |mastercover| |masterreq| |ghwatch| |ghstar|



Introduction
============

Database access is often central to any web application or service. To offer the maximum flexibility, the `WebCore web
framework <https://github.com/marrow/WebCore/>`__ uses a light-weight yet highly modular and fully dependency graphed
extension system. The database connection layer passes through the full capability of this extension system down to an
organized and named collection of database interfaces.

This extension is available with the name ``db`` in the ``web.ext`` plugin namespace.

This extension adds a ``db`` server and request **context attribute**.

This extension provides the ``sqlalchemy``, ``mongoengine``, ``dbapi``, and ``sqlite3`` plugins in the ``web.db``
plugin namespace.


Installation
============

Installing ``web.db`` is easy, just execute the following in a terminal::

    pip install web.db

**Note:** We *strongly* recommend always using a container, virtualization, or sandboxing environment of some kind when
developing using Python; installing things system-wide is yucky (for a variety of reasons) nine times out of ten.  We
prefer light-weight `virtualenv <https://virtualenv.pypa.io/en/latest/virtualenv.html>`__, others prefer solutions as
robust as `Vagrant <http://www.vagrantup.com>`__.

If you add ``web.db`` to the ``install_requires`` argument of the call to ``setup()`` in your
application's ``setup.py`` file, this extension will be automatically installed and made available when your own
application or library is installed.  We recommend using "less than" version numbers to ensure there are no
unintentional side-effects when updating.  Use ``web.db<2.1` to get all bugfixes for the current release,
and ``web.db<3.0`` to get bugfixes and feature updates while ensuring that large breaking changes are not
installed.

There are a few "extras" you can require (by adding a comma separated list of these tags within square brackets after
the dependency name, e.g.: ``web.db[foo,bar]``

* **development** - installs all testing requirements and optional components
* **sql** - installs `SQLAlchemy <http://sqlalchemy.org>`__
* **mongoengine** - installs `MongoEngine <http://mongoengine.org>`__ (**Note:** this engine is not yet production quality.)


Development Version
-------------------

    |developstatus| |developcover| |ghsince| |issuecount| |ghfork|

Development takes place on `GitHub <https://github.com/>`__ in the 
`web.db <https://github.com/marrow/web.db/>`__ project.  Issue tracking, documentation, and
downloads are provided there.

Installing the current development version requires `Git <http://git-scm.com/>`__, a distributed source code management
system.  If you have Git you can run the following to download and *link* the development version into your Python
runtime::

    git clone https://github.com/marrow/web.db.git
    pip install -e 'web.db[development]'

You can then upgrade to the latest version at any time::

    (cd web.db; git pull; pip install -U -e '.[development]')

If you would like to make changes and contribute them back to the project, fork the GitHub project, make your changes,
and submit a pull request.  This process is beyond the scope of this documentation; for more information see
`GitHub's documentation <http://help.github.com/>`__.


Usage
=====

The ``web.db`` extension (providing the ``db`` feature flag for extension dependency graphing and plugin with that
name in the ``web.ext`` namespace) is utilized in a few different contexts.


Configuration
-------------

This happens before the web application has "started" and is ready to service requests. You enable the extension by
including an instance of it in the ``extensions`` argument to the instantiation of a ``web.core:Application`` object::

    from web.ext.db import DatabaseExtension
    
    app = Application("Hi.", extensions=[
            DatabaseExtension(),
        ])

The initializer for the database extension uses the arguments provided to declare named database interfaces, which you
instantiate and pass in by name. Additionally, the name ``default`` has special meaning, and may be passed as the
first (and only) positional parameter.


Application
-----------

At the application context, that is, in extension callbacks where the ``context`` is an ApplicationContext object,
outside of the request cycle, a ``db`` attribute is added to contain any contributions made by database adapters.

Please refer to the documentation for individual adapters as to what values they assign for themselves and when.


Adapters
========

There is a limited set of adapters provided built-in.


Native DB API 2.0
-----------------

Many SQL or SQL-like database adapters in Python are available which expose a `PEP 249 DB API
2.0 <https://www.python.org/dev/peps/pep-0249/>`__-compliant interface. These can be utilized directly once a few
properties of the adapter are known.

First, you need to know the location of the adapter's ``connect`` function. Pass this as the first positional
argument to the ``DBAPIConnection`` constructor as a string in dot-colon notation. The second positional argument
is the URI to pass through as the target to connect the engine to. Behaviour may vary from adapter to adapter.

As an example, Python often ships with an adapter for SQLite. You might utilize it by initializing your application
with this extension arrangement::

    from web.ext.db import DatabaseExtension
    from web.db.dbapi import DBAPIConnection
    
    app = Application("Hi.", extensions=[
            DatabaseExtension(DBAPIConnection(
                    'sqlite3:connect',  # A dot-colon path, module:name.
                    ':memory:',  # Use the in-memory temporary store.
                ))
        ])

Because this engine is built-in and common, a shortcut is provided by way of the ``SQLite3Connection`` subclass::

    from web.ext.db import DatabaseExtension
    from web.db.dbapi import SQLite3Connection
    
    app = Application("Hi.", extensions=[
            DatabaseExtension(SQLite3Connection(':memory:'))
        ])

Either way, additional keyword arguments are passed along through to the underlying ``connect`` function. For the
generic adapter, two additional arguments have a significant impact on when the interface performs actions.

If ``safe`` is truthy (the default) then the adapter is treated as thread safe. It is "connected" on application start
and "disconnected" on application shutdown. Otherwise the interface is "connected" at the beginning of a request and
"disconnected" at the end of the request, after all content has been returned to the user.


SQLAlchemy
----------

During startup, you can utilize the SQLAlchemy engine object contained within the context to perform global-level
operations such as DDL manipulation. One such example with an SQLAlchemy adapter configured as the defualt interface
would be::

    class ApplicationExtension:
        needs = {'db'}
        
        def start(self, context):
            SomeDeclarativeBase.metadata.create_all(context.db.default)

Within the context of a request, the interface exposed via the context is a request-local scoped session. You can use
this to prepare and commit transactions, issue queries, etc.

Currently no transactional behaviour, auto-commit, etc. are supported.


Extending
=========

Writing new adapters is nearly identical to writing WebCore extensions. All of the same rules apply: must be a class,
offers callback registration through the use of named methods, can register ``needs`` and ``uses`` and ``provides``,
etc. Please see the `WebCore <https://github.com/marrow/WebCore/>`__ documentation and examples.

The only major difference is that the database interface is expected to populate an attribute or mapping item with a
name defined by an ``alias`` attribute.  Several examples are provided in the source, and are documented so as to
provide examples.


Version History
===============

Version 2.0.1
-------------

* Updated the ``README`` and metaproject layout to current Marrow standards.
* Removed extraneous imports and slots where unhelpful or causing issues, such as in the SQLAlchemy adapter. (Thanks
  bmillham!)
* Migrated ``MongoDBConnection`` from `marrow.mongo <https://github.com/marrow/mongo>`__.

Version 2.0
-----------

* Extract of the database mechanism from WebCore.

Version 1.x
-----------

* Process fully integrated in the WebCore web framework.


License
=======

web.db has been released under the MIT Open Source license.

The MIT License
---------------

Copyright © 2009-2016 Alice Bevan-McGregor and contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the “Software”), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NON-INFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


.. |ghwatch| image:: https://img.shields.io/github/watchers/marrow/web.db.svg?style=social&label=Watch
    :target: https://github.com/marrow/web.db/subscription
    :alt: Subscribe to project activity on Github.

.. |ghstar| image:: https://img.shields.io/github/stars/marrow/web.db.svg?style=social&label=Star
    :target: https://github.com/marrow/web.db/subscription
    :alt: Star this project on Github.

.. |ghfork| image:: https://img.shields.io/github/forks/marrow/web.db.svg?style=social&label=Fork
    :target: https://github.com/marrow/web.db/fork
    :alt: Fork this project on Github.

.. |masterstatus| image:: http://img.shields.io/travis/marrow/web.db/master.svg?style=flat
    :target: https://travis-ci.org/marrow/web.db/branches
    :alt: Release build status.

.. |mastercover| image:: http://img.shields.io/codecov/c/github/marrow/web.db/master.svg?style=flat
    :target: https://codecov.io/github/marrow/web.db?branch=master
    :alt: Release test coverage.

.. |masterreq| image:: https://img.shields.io/requires/github/marrow/web.db.svg
    :target: https://requires.io/github/marrow/web.db/requirements/?branch=master
    :alt: Status of release dependencies.

.. |developstatus| image:: http://img.shields.io/travis/marrow/web.db/develop.svg?style=flat
    :target: https://travis-ci.org/marrow/web.db/branches
    :alt: Development build status.

.. |developcover| image:: http://img.shields.io/codecov/c/github/marrow/web.db/develop.svg?style=flat
    :target: https://codecov.io/github/marrow/web.db?branch=develop
    :alt: Development test coverage.

.. |developreq| image:: https://img.shields.io/requires/github/marrow/web.db.svg
    :target: https://requires.io/github/marrow/web.db/requirements/?branch=develop
    :alt: Status of development dependencies.

.. |issuecount| image:: http://img.shields.io/github/issues-raw/marrow/web.db.svg?style=flat
    :target: https://github.com/marrow/web.db/issues
    :alt: Github Issues

.. |ghsince| image:: https://img.shields.io/github/commits-since/marrow/web.db/2.0.1.svg
    :target: https://github.com/marrow/web.db/commits/develop
    :alt: Changes since last release.

.. |ghtag| image:: https://img.shields.io/github/tag/marrow/web.db.svg
    :target: https://github.com/marrow/web.db/tree/2.0.1
    :alt: Latest Github tagged release.

.. |latestversion| image:: http://img.shields.io/pypi/v/web.db.svg?style=flat
    :target: https://pypi.python.org/pypi/web.db
    :alt: Latest released version.

.. |downloads| image:: http://img.shields.io/pypi/dw/web.db.svg?style=flat
    :target: https://pypi.python.org/pypi/web.db
    :alt: Downloads per week.

.. |cake| image:: http://img.shields.io/badge/cake-lie-1b87fb.svg?style=flat

