from http import HTTPStatus

import aiohttp
import pytest
import responses

from ujenkins import AsyncJenkinsClient, JenkinsClient, JenkinsError


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
