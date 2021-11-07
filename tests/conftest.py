import pytest

from aioresponses import aioresponses

from ujenkins import AsyncJenkinsClient, JenkinsClient


@pytest.fixture
def aiohttp_mock():
    with aioresponses() as mock:
        yield mock


@pytest.fixture
def client():
    j = JenkinsClient('http://server')
    # disable crumb wrapper for simplify testing
    j.crumb = False
    yield j
    j.close()


@pytest.fixture
async def async_client():
    j = AsyncJenkinsClient('http://server')
    # disable crumb wrapper for simplify testing
    j.crumb = False
    yield j
    await j.close()
