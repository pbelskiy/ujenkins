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

+--------------------------------------------+
|   Comparison to other packages             |
+-------------------+-------+-------+--------+
| Name              | Sync  | Async | Python |
+===================+=======+=======+========+
| `ujenkins`_       |  YES  |  YES  | 3.6+   |
+-------------------+-------+-------+--------+
| `aiojenkins`_     |  NO   |  YES  | 3.5+   |
+-------------------+-------+-------+--------+
| `python-jenkins`_ |  YES  |  NO   | 3.4+   |
+-------------------+-------+-------+--------+
| `jenkinsapi`_     |  YES  |  NO   | 3.4+   |
+-------------------+-------+-------+--------+

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

Usage
-----

Get Jenkins version using sync client:

.. code:: python

    from ujenkins import JenkinsClient

    def example():
        client = JenkinsClient('http://server', 'user', 'password')
        version = client.system.get_version()
        print(version)

    example()

With async client (be careful ``AsyncJenkinsClient`` must be called inside async function):

.. code:: python

    import asyncio
    from ujenkins import AsyncJenkinsClient

    async def example():
        client = AsyncJenkinsClient('http://server', 'user', 'password')
        version = await client.system.get_version()
        print(version)
        await client.close()

    asyncio.run(example())

Examples
--------

In all code examples below client instance is created by:

.. code:: python

    from ujenkins import JenkinsClient
    client = JenkinsClient('http://server', 'user', 'password')

Get timestamp of latest build
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    client.builds.get_info('job', 'lastBuild')['timestamp']

Get url of started build
~~~~~~~~~~~~~~~~~~~~~~~~

Be careful, ``JenkinsNotFoundError`` could be raise in case build with same arg already enqueued.

.. code:: python

    item_id = client.builds.start('my_job')
    while True:
        time.sleep(5)
        try:
            info = client.queue.get_info(item_id)
            print(info['executable']['url'])
            break
        except (KeyError, TypeError):
            pass  # wait for build will be started

Get all jobs
~~~~~~~~~~~~

Basically ``client.jobs.get()`` returns jobs from root (depth = 0), in case you
want receive all the jobs, there are few approaches for it.

1) Set needed depth, experimentally 10 is enough.

.. code-block:: python

    jobs = client.jobs.get(depth=10)

Output:

.. code-block:: python

    {'folder': {'_class': 'com.cloudbees.hudson.plugins.folder.Folder',
                'jobs': [{'_class': 'hudson.model.FreeStyleProject',
                        'color': 'notbuilt',
                        'name': 'job_in_folder1',
                        'url': 'http://localhost:8080/job/folder/job/job_in_folder1/'},
                        {'_class': 'com.cloudbees.hudson.plugins.folder.Folder',
                        'jobs': [{'_class': 'hudson.model.FreeStyleProject',
                                    'color': 'notbuilt',
                                    'name': 'sub_job_in_subfolder',
                                    'url': 'http://localhost:8080/job/folder/job/subfolder/job/sub_job_in_subfolder/'}],
                        'name': 'subfolder',
                        'url': 'http://localhost:8080/job/folder/job/subfolder/'}],
                'name': 'folder',
                'url': 'http://localhost:8080/job/folder/'},
    'job': {'_class': 'hudson.model.FreeStyleProject',
            'color': 'blue',
            'name': 'job',
            'url': 'http://localhost:8080/job/job/'}}

2) Or just write your code to recursively form it, example is below.

.. code:: python

    def get_all_jobs(url: str = '', parent: str = '') -> Dict[str, dict]:
        jobs = {}

        for name, prop in client.jobs.get(url).items():
            jobs[parent + name] = prop
            if 'Folder' in prop.get('_class', ''):
                jobs.update(get_all_jobs(prop['url'], parent + name + '/'))

        return jobs

    all_jobs = get_all_jobs()

Working with build artifacts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # get content of artifact (bytes)
    content = client.builds.get_artifact('my_job', 31, 'photo.jpg')
    with open('/tmp/photo.jpg', 'wb') as f:
        w.write(content)

    # enumerate artifacts
    artifacts = client.builds.get_list_artifacts('my_job', 31)
    for artifact in artifacts:
        # get content and manually save it
        content = client.builds.get_artifact('my_job', 31, artifact['path'])

        # or absolute url could be used for external download
        print(artifact['url'])
        # >> 'http://server/job/my_job/31/artifact/photo.jpg'

Documentation
-------------

`Read the Docs <https://ujenkins.readthedocs.io/en/latest/>`_

Testing
-------

Prerequisites: ``tox``

Then just run tox, all dependencies and checks will run automatically

::

    tox

Contributing
------------

Any contributions are welcome!
