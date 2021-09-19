import re

import responses

BUILDS_ALL_JSON = """{
    "_class": "hudson.model.FreeStyleProject",
    "allBuilds": [
        {"_class": "hudson.model.FreeStyleBuild", "number": 1, "url": "http://localhost:8080/job/jobbb/1/"}
    ]
}
"""

BUILD_INFO_JSON = """{
  "_class" : "hudson.model.FreeStyleBuild",
  "actions" : [
    {
      "_class" : "hudson.model.CauseAction",
      "causes" : [
        {
          "_class" : "hudson.model.Cause$UserIdCause",
          "shortDescription" : "Started by user admin",
          "userId" : "admin",
          "userName" : "admin"
        }
      ]
    }
  ],
  "artifacts" : [

  ],
  "building" : false,
  "description" : null,
  "displayName" : "#14",
  "duration" : 6,
  "estimatedDuration" : 4,
  "executor" : null,
  "fullDisplayName" : "jobbb #14",
  "id" : "14",
  "keepLog" : false,
  "number" : 14,
  "queueId" : 429,
  "result" : "SUCCESS",
  "timestamp" : 1628629375963,
  "url" : "http://localhost:8080/job/jobbb/14/",
  "builtOn" : "",
  "changeSet" : {
    "_class" : "hudson.scm.EmptyChangeLogSet",
    "items" : [

    ],
    "kind" : null
  },
  "culprits" : [

  ]
}
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=BUILDS_ALL_JSON,
    )

    response = client.builds.get('job')
    assert len(response) == 1
    assert response[0]['number'] == 1


@responses.activate
def test_get_info(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        content_type='application/json;charset=utf-8',
        body=BUILD_INFO_JSON,
    )

    response = client.builds.get_info('jobbb', 14)
    assert response['duration'] == 6


@responses.activate
def test_get_output(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/job/.+/consoleText'),
        content_type='text/plain;charset=utf-8',
        body='Started by user admin\nRunning as SYSTEM',
    )

    response = client.builds.get_output('job', 14)
    assert 'Started' in response


@responses.activate
def test_start(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/build.+'),
        headers={'Location': 'http://localhost:8080/queue/item/424/'}
    )

    response = client.builds.start('job')
    assert response == 424


@responses.activate
def test_stop(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/stop'),
    )

    client.builds.stop('job', 424)


@responses.activate
def test_delete(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/doDelete'),
    )

    client.builds.delete('job', 424)
