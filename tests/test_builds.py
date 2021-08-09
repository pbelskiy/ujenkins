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
