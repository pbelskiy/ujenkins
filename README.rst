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

Python client for Jenkins which supports both sync and async syntax with same interface.

+----------------------------------------------------+
|   Comparison to other packages                     |
+-------------------+-------+-------+----------------+
| Name              | Sync  | Async | Python version |
+===================+=======+=======+================+
| `ujenkins`_       |  YES  |  YES  | 3.6+           |
+-------------------+-------+-------+----------------+
| `aiojenkins`_     |  NO   |  YES  | 3.5+           |
+-------------------+-------+-------+----------------+
| `python-jenkins`_ |  YES  |  NO   | 3.4+           |
+-------------------+-------+-------+----------------+
| `jenkinsapi`_     |  YES  |  NO   | 3.4+           |
+-------------------+-------+-------+----------------+

.. _ujenkins: https://github.com/pbelskiy/ujenkins
.. _aiojenkins: https://github.com/pbelskiy/aiojenkins
.. _python-jenkins: https://opendev.org/jjb/python-jenkins
.. _jenkinsapi: https://github.com/pycontribs/jenkinsapi

Installation
------------

Latest release from PyPI

.. code:: shell

    pip3 install ujenkins

Or latest developing version

.. code:: shell

    pip3 install git+https://github.com/pbelskiy/ujenkins

Sync and async usage
--------------------

Get Jenkins version using sync client:

.. code:: python

    from ujenkins import JenkinsClient

    def example():
        client = JenkinsClient('http://server', 'user', 'password')
        version = client.system.get_version()
        print(version)

    example()

With async client:

.. code:: python

    import asyncio
    from ujenkins import AsyncJenkinsClient

    async def example():
        client = AsyncJenkinsClient('http://server', 'user', 'password')
        version = await client.system.get_version()
        print(version)

    asyncio.run(example())

Examples
--------

Get timestamp of latest build of speciefic job.

Build number or some of standard tags could be used here:

- lastBuild
- lastCompletedBuild
- lastFailedBuild
- lastStableBuild
- lastSuccessfulBuild
- lastUnstableBuild
- lastUnsuccessfulBuild

.. code:: python

    from ujenkins import JenkinsClient
    client = JenkinsClient('http://server', 'user', 'password')
    client.builds.get_info('job', 'lastBuild')['timestamp']

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
