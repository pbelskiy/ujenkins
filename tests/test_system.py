import re

import responses

STATUS_JSON = """{
  "_class" : "hudson.model.Hudson",
  "assignedLabels" : [
    {
      "name" : "master"
    }
  ],
  "mode" : "NORMAL",
  "nodeDescription" : "the master Jenkins node",
  "nodeName" : "",
  "numExecutors" : 2,
  "description" : null,
  "jobs" : [
    {
      "_class" : "hudson.model.FreeStyleProject",
      "name" : "jobbb",
      "url" : "http://localhost:8080/job/jobbb/",
      "color" : "blue"
    },
    {
      "_class" : "com.cloudbees.hudson.plugins.folder.Folder",
      "name" : "teest_folder",
      "url" : "http://localhost:8080/job/teest_folder/"
    }
  ],
  "overallLoad" : {

  },
  "primaryView" : {
    "_class" : "hudson.model.AllView",
    "name" : "all",
    "url" : "http://localhost:8080/"
  },
  "quietDownReason" : null,
  "quietingDown" : false,
  "slaveAgentPort" : 50000,
  "unlabeledLoad" : {
    "_class" : "jenkins.model.UnlabeledLoadStatistics"
  },
  "url" : "http://localhost:8080/",
  "useCrumbs" : true,
  "useSecurity" : true,
  "views" : [
    {
      "_class" : "hudson.model.AllView",
      "name" : "all",
      "url" : "http://localhost:8080/"
    },
    {
      "_class" : "hudson.model.ListView",
      "name" : "test2",
      "url" : "http://localhost:8080/view/test2/"
    }
  ]
}
"""

TOKEN_JSON = """
  {
    "status": "ok",
    "data": {
        "tokenName": "test",
        "tokenUuid": "a8f93d3d-e431-4c88-ad6f-f71dd50e774f",
        "tokenValue":"11064db87a080c7dc478fedfd8cd9d4265"
    }
  }
"""


@responses.activate
def test_get_status(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=STATUS_JSON
    )

    status = client.system.get_status()
    assert status['quietingDown'] is False


@responses.activate
def test_get_version(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/'),
        headers={'X-Jenkins': '2.0.129'}
    )

    version = client.system.get_version()
    assert version.major == 2
    assert version.minor == 0
    assert version.patch == 129


@responses.activate
def test_is_ready(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=STATUS_JSON
    )

    ready = client.system.is_ready()
    assert ready is True


@responses.activate
def test_quiet_down(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/quietDown'),
    )

    client.system.quiet_down()


@responses.activate
def test_cancel_quiet_down(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/cancelQuietDown'),
    )

    client.system.cancel_quiet_down()


@responses.activate
def test_restart(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/restart'),
    )

    client.system.restart()


@responses.activate
def test_safe_restart(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/safeRestart'),
    )

    client.system.safe_restart()


@responses.activate
def test_generate_token(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/me/descriptorByName/jenkins.security.ApiTokenProperty/generateNewToken'),
        content_type='application/json;charset=utf-8',
        body=TOKEN_JSON,
    )

    value, uuid = client.system.generate_token('test')
    assert uuid == 'a8f93d3d-e431-4c88-ad6f-f71dd50e774f'
    assert value == '11064db87a080c7dc478fedfd8cd9d4265'


@responses.activate
def test_revoke_token(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/me/descriptorByName/jenkins.security.ApiTokenProperty/revoke'),
    )

    client.system.revoke_token('a8f93d3d-e431-4c88-ad6f-f71dd50e774f')


@responses.activate
def test_run_groovy_script(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/scriptText'),
        body='test'
    )

    response = client.system.run_groovy_script('print("test")')
    assert response == 'test'
