import re

import responses

from tests import JENKINS_INFO_JSON

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
        body=JENKINS_INFO_JSON
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

    responses.add(
        responses.GET,
        re.compile(r'.+/'),
        headers={'X-Jenkins': '2.123'}
    )

    version = client.system.get_version()
    assert version.major == 2
    assert version.minor == 123
    assert version.patch == 0


@responses.activate
def test_is_ready(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=JENKINS_INFO_JSON
    )

    assert client.system.is_ready() is True


@responses.activate
def test_quiet_down(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/quietDown'),
    )

    assert client.system.quiet_down() is None


@responses.activate
def test_cancel_quiet_down(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/cancelQuietDown'),
    )

    assert client.system.cancel_quiet_down() is None


@responses.activate
def test_restart(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/restart'),
    )

    assert client.system.restart() is None


@responses.activate
def test_safe_restart(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/safeRestart'),
    )

    assert client.system.safe_restart() is None


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

    assert client.system.revoke_token('a8f93d3d-e431-4c88-ad6f-f71dd50e774f') is None


@responses.activate
def test_run_groovy_script(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/scriptText'),
        body='test'
    )

    response = client.system.run_groovy_script('print("test")')
    assert response == 'test'
