import re
import sys

from http import HTTPStatus

import aiohttp
import pytest
import responses

from ujenkins import AsyncJenkinsClient, JenkinsClient, JenkinsError

CRUMB_JSON = """
{
  "_class": "hudson.security.csrf.DefaultCrumbIssuer",
  "crumb": "9c427004e7ed327a230436ee3103856d8df1eec7f2964a87d3d95e850974c4cd",
  "crumbRequestField": "Jenkins-Crumb"
}
"""


@responses.activate
def test_sync_client_retry():
    # responses library does`t support Retry mock
    # https://github.com/getsentry/responses/issues/135
    # so, just cover code of retry constructor
    statuses = [HTTPStatus.BAD_REQUEST, HTTPStatus.INTERNAL_SERVER_ERROR]

    client = JenkinsClient(
        'http://server',
        'login',
        'password',
        retry=dict(
            total=10,
            factor=1,
            statuses=statuses,
        )
    )

    assert client.session.adapters['http://'].max_retries.status_forcelist == statuses


@pytest.mark.asyncio
async def test_async_client_retry(aiohttp_mock):
    client = AsyncJenkinsClient(
        'http://server',
        'login',
        'password',
        retry=dict(
            total=10,
            statuses=[HTTPStatus.INTERNAL_SERVER_ERROR],
        )
    )
    client.crumb = False

    aiohttp_mock.get(
        'http://server/',
        content_type='text/plain',
        body='Server error',
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )

    aiohttp_mock.get(
        'http://server/',
        content_type='text/plain',
        headers={'X-Jenkins': '2.0.129'},
        status=HTTPStatus.OK,
    )

    version = await client.system.get_version()
    assert version.major == 2
    assert version.minor == 0
    assert version.patch == 129
    await client.close()


@pytest.mark.asyncio
async def test_async_client_retry_exception(aiohttp_mock):
    client = AsyncJenkinsClient(
        'http://server',
        'login',
        'password',
        retry=dict(
            total=2,
            statuses=[HTTPStatus.INTERNAL_SERVER_ERROR],
        )
    )

    aiohttp_mock.get(
        'http://server/rest/version',
        exception=aiohttp.ClientError()
    )

    aiohttp_mock.get(
        'http://server/rest/version',
        exception=aiohttp.ClientError()
    )

    with pytest.raises(JenkinsError):
        await client.system.get_version()

    await client.close()


def test_retry_argument_validation():
    with pytest.raises(JenkinsError):
        JenkinsClient('http://server', retry=dict(total=1, strange_argument=1))

    with pytest.raises(JenkinsError):
        AsyncJenkinsClient('http://server', retry=dict(total=0))


@responses.activate
def test_sync_crumb():
    responses.add(
        responses.GET,
        re.compile(r'.+/crumbIssuer/api/json'),
        content_type='application/json;charset=utf-8',
        body=CRUMB_JSON
    )

    responses.add(
        responses.GET,
        re.compile(r'.+/'),
        headers={'X-Jenkins': '2.0.129'}
    )

    client = JenkinsClient('http://server')
    version = client.system.get_version()

    assert client.crumb['Jenkins-Crumb'] == \
        '9c427004e7ed327a230436ee3103856d8df1eec7f2964a87d3d95e850974c4cd'
    assert version.major == 2


@responses.activate
def test_sync_crumb_disabled():
    responses.add(
        responses.GET,
        re.compile(r'.+/crumbIssuer/api/json'),
        status=HTTPStatus.NOT_FOUND
    )

    responses.add(
        responses.GET,
        re.compile(r'.+/'),
        headers={'X-Jenkins': '2.0.129'}
    )

    client = JenkinsClient('http://server')
    version = client.system.get_version()

    assert client.crumb is False
    assert version.major == 2


@pytest.mark.skipif(sys.version_info < (3, 6), reason='aiohttp mock problem')
@pytest.mark.asyncio
async def test_async_crumb(aiohttp_mock, async_client):
    aiohttp_mock.get(
        re.compile(r'.+/crumbIssuer/api/json'),
        content_type='application/json;charset=utf-8',
        body=CRUMB_JSON
    )

    aiohttp_mock.get(
        re.compile(r'.+/'),
        headers={'X-Jenkins': '2.0.129'}
    )

    async_client.crumb = None
    version = await async_client.system.get_version()

    assert async_client.crumb['Jenkins-Crumb'] == \
        '9c427004e7ed327a230436ee3103856d8df1eec7f2964a87d3d95e850974c4cd'
    assert version.major == 2
