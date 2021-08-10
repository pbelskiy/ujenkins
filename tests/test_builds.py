import re

import responses

BUILDS = """{
    "_class": "hudson.model.FreeStyleProject",
    "allBuilds": [
        {"_class": "hudson.model.FreeStyleBuild", "number": 1, "url": "http://localhost:8080/job/jobbb/1/"}
    ]
}
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=BUILDS,
    )

    response = client.builds.get('job')
    assert len(response) == 1
    assert response[0]['number'] == 1


@responses.activate
def test_start(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/build.+'),
        headers={'Location': 'http://localhost:8080/queue/item/424/'}
    )

    response = client.builds.start('job')
    assert response == 424
