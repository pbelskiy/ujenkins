import pytest

from aioresponses import aioresponses

from ujenkins import JenkinsClient


@pytest.fixture
def aiohttp_mock():
    with aioresponses() as mock:
        yield mock


@pytest.fixture
def client():
    yield JenkinsClient('http://server')
