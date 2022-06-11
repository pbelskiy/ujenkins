Universal Python client for `Jenkins <http://jenkins.io>`_
==========================================================

|Build status|
|Docs status|
|Coverage status|
|Version status|
|Downloads status|

.. |Build status|
   image:: https://github.com/pbelskiy/ujenkins/workflows/Tests/badge.svg
.. |Docs status|
   image:: https://readthedocs.org/projects/ujenkins/badge/?version=latest
.. |Coverage status|
   image:: https://img.shields.io/coveralls/github/pbelskiy/ujenkins?label=Coverage
.. |Version status|
   image:: https://img.shields.io/pypi/pyversions/ujenkins?label=Python
.. |Downloads status|
   image:: https://img.shields.io/pypi/dm/ujenkins?color=1&label=Downloads

----

Python client for jenkins which supports both synс and async syntax with same API interfaces.

+-----------------------------------+
|   Comparison to other packages    |
+-------------------+-------+-------+
| Name              | sync  | async |
+===================+=======+=======+
| `ujenkins`_       |  YES  |  YES  |
+-------------------+-------+-------+
| `aiojenkins`_     |  NO   |  YES  |
+-------------------+-------+-------+
| `python-jenkins`_ |  YES  |  NO   |
+-------------------+-------+-------+
| `jenkinsapi`_     |  YES  |  NO   |
+-------------------+-------+-------+

.. _ujenkins: https://github.com/pbelskiy/ujenkins
.. _aiojenkins: https://github.com/pbelskiy/aiojenkins
.. _python-jenkins: https://github.com/pycontribs/jenkinsapi
.. _jenkinsapi: https://opendev.org/jjb/python-jenkins

Installation
------------

Latest release from PyPI

.. code:: shell

    pip3 install ujenkins

Or latest developing version

.. code:: shell

    pip3 install git+https://github.com/pbelskiy/ujenkins

Usage
-----

Main advantage of this package is that same API interfaces used for sync
and async syntax.

Get Jenkins version using sync client:

.. code:: python

    from ujenkins import JenkinsClient

    def example():
        client = JenkinsClient('http://server', 'login', 'password')
        version = client.system.get_version()
        print(version)

    example()

With async client:

.. code:: python

    import asyncio
    from ujenkins import AsyncJenkinsClient

    async def example():
        client = AsyncJenkinsClient('http://server', 'login', 'password')
        version = await client.system.get_version()
        print(version)

    asyncio.run(example())

`Please look at tests directory for more examples. <https://github.com/pbelskiy/ujenkins/tree/master/tests>`_

Documentation
-------------

`Read the Docs <https://ujenkins.readthedocs.io/en/latest/>`_

Testing
-------

Prerequisites: `tox`

Then just run tox, all dependencies and checks will run automatically

::

    tox

Contributing
------------

Any contributions are welcome!
