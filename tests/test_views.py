import re

import responses

from tests import JENKINS_INFO_JSON


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=JENKINS_INFO_JSON,
    )

    response = client.views.get()
    assert len(response) == 3
    assert 'my_view' in response


@responses.activate
def test_is_exists(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=JENKINS_INFO_JSON,
    )

    assert client.views.is_exists('extra') is False
