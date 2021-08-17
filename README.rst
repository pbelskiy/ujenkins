Universal Python client for `Jenkins <http://jenkins.io>`_
==========================================================

Python client for jenkins which supports both synс and async syntax with same API interfaces.

Status
------

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

Documentation
-------------

`Read the Docs <https://ujenkins.readthedocs.io/en/latest/>`_

Installation
------------

::

    pip3 install -U ujenkins

Comparison to other libraries
-----------------------------

+-------------------+-------+-------+
| Name              | sync  | async |
+===================+=======+=======+
| `ujenkins`_       |  YES  |  YES  |
+-------------------+-------+-------+
| `aiojenkins`_     |  NO   |  YES  |
+-------------------+-------+-------+
| `python-jenkins`_ |  OK   |   NO  |
+-------------------+-------+-------+
| `jenkinsapi`_     |  OK   |   NO  |
+-------------------+-------+-------+

.. _ujenkins: https://pypi.org/project/ujenkins/
.. _aiojenkins: https://pypi.org/project/aiojenkins/
.. _python-jenkins: https://pypi.org/project/python-jenkins/
.. _jenkinsapi: https://pypi.org/project/jenkinsapi/
