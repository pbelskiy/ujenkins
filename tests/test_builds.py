import json
import re

import pytest
import responses

BUILDS_ALL_JSON = """{
    "_class": "hudson.model.FreeStyleProject",
    "allBuilds": [
        {
            "_class": "hudson.model.FreeStyleBuild",
            "number": 1,
            "url": "http://localhost:8080/job/jobbb/1/"
        }
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
    {
      "displayPath" : "photo.jpg",
      "fileName" : "photo.jpg",
      "relativePath" : "photo.jpg"
    }
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
def test_get_artifact(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/job/.+/artifact/file.bin'),
        content_type='application/octet-stream',
        body=b'\x01\x02\x03',
    )

    response = client.builds.get_artifact('job', 14, 'file.bin')
    assert isinstance(response, bytes)
    assert len(response) == 3


@pytest.mark.asyncio
async def test_async_get_artifact(aiohttp_mock, async_client):
    aiohttp_mock.get(
        re.compile(r'.*/job/.+/artifact/file.bin'),
        content_type='application/octet-stream',
        body=b'\x01\x02\x03',
    )

    response = await async_client.builds.get_artifact('job', 14, 'file.bin')
    assert isinstance(response, bytes)
    assert len(response) == 3


@responses.activate
def test_get_list_artifacts(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        content_type='application/json;charset=utf-8',
        body=BUILD_INFO_JSON,
    )

    artifacts = client.builds.get_list_artifacts('jobbb', 14)

    assert len(artifacts) == 1
    assert artifacts[0]['name'] == 'photo.jpg'
    assert artifacts[0]['path'] == 'photo.jpg'
    assert artifacts[0]['url'] == 'http://server//job/jobbb/14/artifact/photo.jpg'


@responses.activate
def test_start(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/build'),
        headers={'Location': 'http://localhost:8080/queue/item/424/'}
    )

    response = client.builds.start('job')
    assert response == 424


@responses.activate
def test_start_no_queue_id(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/build'),
        headers={'Location': 'some strange header'}
    )

    response = client.builds.start('job')
    assert response is None


@responses.activate
def test_start_with_parameters(client):
    data = {
        'json': json.dumps({
            'parameter': {'name': 'a', 'value': '1'},
            'statusCode': '303',
            'redirectTo': '.'
        }),
        'a': '1'
    }

    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/buildWithParameters'),
        headers={'Location': 'http://localhost:8080/queue/item/777/'},
        match=[responses.matchers.urlencoded_params_matcher(data)],
    )

    response = client.builds.start('job', {'a': 1})
    assert response == 777


@responses.activate
def test_start_with_parameters_as_kwargs(client):
    data = {
        'json': json.dumps({
            'parameter': {'name': 'a', 'value': '1'},
            'statusCode': '303',
            'redirectTo': '.'
        }),
        'a': '1'
    }

    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/buildWithParameters'),
        headers={'Location': 'http://localhost:8080/queue/item/123/'},
        match=[responses.matchers.urlencoded_params_matcher(data)],
    )

    response = client.builds.start('test', a=1)
    assert response == 123


@responses.activate
def test_start_with_parameters_overwrite(client):
    data = {
        'json': json.dumps({
            'parameter': {'name': 'parameters', 'value': '1'},
            'statusCode': '303',
            'redirectTo': '.'
        }),
        'parameters': '1'
    }

    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/buildWithParameters'),
        headers={'Location': 'http://localhost:8080/queue/item/123/'},
        match=[responses.matchers.urlencoded_params_matcher(data)],
    )

    response = client.builds.start('test', parameters=1)
    assert response == 123


@responses.activate
def test_start_with_mixed_parameters(client):
    data = {
        'json': json.dumps({
            'parameter': [{'name': 'a', 'value': '1'}, {'name': 'b', 'value': '2'}],
            'statusCode': '303',
            'redirectTo': '.'
        }),
        'a': '1',
        'b': '2',
    }

    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/buildWithParameters'),
        headers={'Location': 'http://localhost:8080/queue/item/123/'},
        match=[responses.matchers.urlencoded_params_matcher(data)],
    )

    response = client.builds.start('test', parameters={'a': 1, 'b': 2})
    assert response == 123


@responses.activate
def test_stop(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/stop'),
    )

    assert client.builds.stop('job', 424) is None


@responses.activate
def test_delete(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/job/.+/doDelete'),
    )

    assert client.builds.delete('job', 424) is None
