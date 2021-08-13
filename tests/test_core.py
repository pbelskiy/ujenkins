from http import HTTPStatus

import responses

from ujenkins import JenkinsClient


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
