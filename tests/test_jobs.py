import re

from http import HTTPStatus

import responses

from tests import JENKINS_INFO_JSON

JOB_INFO_JSON = """
{
  "_class" : "hudson.model.FreeStyleProject",
  "actions" : [
    {

    },
    {

    }
  ],
  "description" : "",
  "displayName" : "test",
  "displayNameOrNull" : null,
  "fullDisplayName" : "test",
  "fullName" : "test",
  "name" : "test",
  "url" : "http://localhost:8080/job/test/",
  "buildable" : true,
  "builds" : [
    {
      "_class" : "hudson.model.FreeStyleBuild",
      "number" : 15,
      "url" : "http://localhost:8080/job/test/15/"
    },
    {
      "_class" : "hudson.model.FreeStyleBuild",
      "number" : 14,
      "url" : "http://localhost:8080/job/test/14/"
    },
    {
      "_class" : "hudson.model.FreeStyleBuild",
      "number" : 13,
      "url" : "http://localhost:8080/job/test/13/"
    },
    {
      "_class" : "hudson.model.FreeStyleBuild",
      "number" : 12,
      "url" : "http://localhost:8080/job/test/12/"
    }
  ],
  "color" : "red",
  "firstBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 1,
    "url" : "http://localhost:8080/job/test/1/"
  },
  "healthReport" : [
    {
      "description" : "Build stability: 1 out of the last 5 builds failed.",
      "iconClassName" : "icon-health-60to79",
      "iconUrl" : "health-60to79.png",
      "score" : 80
    }
  ],
  "inQueue" : false,
  "keepDependencies" : false,
  "lastBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 15,
    "url" : "http://localhost:8080/job/test/15/"
  },
  "lastCompletedBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 15,
    "url" : "http://localhost:8080/job/test/15/"
  },
  "lastFailedBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 15,
    "url" : "http://localhost:8080/job/test/15/"
  },
  "lastStableBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 14,
    "url" : "http://localhost:8080/job/test/14/"
  },
  "lastSuccessfulBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 14,
    "url" : "http://localhost:8080/job/test/14/"
  },
  "lastUnstableBuild" : null,
  "lastUnsuccessfulBuild" : {
    "_class" : "hudson.model.FreeStyleBuild",
    "number" : 15,
    "url" : "http://localhost:8080/job/test/15/"
  },
  "nextBuildNumber" : 16,
  "property" : [

  ],
  "queueItem" : null,
  "concurrentBuild" : false,
  "disabled" : false,
  "downstreamProjects" : [

  ],
  "labelExpression" : null,
  "scm" : {
    "_class" : "hudson.scm.NullSCM"
  },
  "upstreamProjects" : [

  ]
}
"""

JOB_CONFIG_XML = """
<?xml version='1.1' encoding='UTF-8'?>
<project>
  <description></description>
  <keepDependencies>false</keepDependencies>
  <properties/>
  <scm class="hudson.scm.NullSCM"/>
  <canRoam>true</canRoam>
  <disabled>false</disabled>
  <blockBuildWhenDownstreamBuilding>false</blockBuildWhenDownstreamBuilding>
  <blockBuildWhenUpstreamBuilding>false</blockBuildWhenUpstreamBuilding>
  <triggers/>
  <concurrentBuild>false</concurrentBuild>
  <builders/>
  <publishers/>
  <buildWrappers/>
</project>
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=JENKINS_INFO_JSON,
    )

    response = client.jobs.get()
    assert len(response) == 2
    assert 'test' in response


@responses.activate
def test_get_info(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/test/api/json'),
        content_type='application/json;charset=utf-8',
        body=JOB_INFO_JSON,
    )

    response = client.jobs.get_info('test')
    assert len(response['builds']) == 4
    assert response['buildable'] is True


@responses.activate
def test_get_config(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/test/config.xml'),
        content_type='application/xml',
        body=JOB_CONFIG_XML,
    )

    response = client.jobs.get_config('test')
    assert '<description></description>' in response


@responses.activate
def test_is_exists(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/test/api/json'),
        content_type='application/json;charset=utf-8',
        body=JOB_INFO_JSON,
    )

    responses.add(
        responses.GET,
        re.compile(r'.*/another_job/api/json'),
        status=HTTPStatus.NOT_FOUND,
    )

    assert client.jobs.is_exists('test') is True
    assert client.jobs.is_exists('another_job') is False


@responses.activate
def test_create(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/createItem'),
    )

    assert client.jobs.create('some_job', JOB_CONFIG_XML) is None


@responses.activate
def test_reconfigure(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/some_job/config.xml'),
    )

    assert client.jobs.reconfigure('some_job', JOB_CONFIG_XML) is None


@responses.activate
def test_delete(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/job/.+/doDelete'),
    )

    assert client.jobs.delete('useless_job') is None


@responses.activate
def test_copy(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/createItem'),
        match=[responses.matchers.query_param_matcher({
            'mode': 'copy',
            'from': 'job_old',
            'name': 'job_new',
        })],
    )

    assert client.jobs.copy('job_old', 'job_new') is None


@responses.activate
def test_rename(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/doRename'),
        match=[responses.matchers.query_param_matcher({
            'newName': 'job_new',
        })],
    )

    assert client.jobs.rename('job_old', 'job_new') is None


@responses.activate
def test_enable(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/enable'),
    )

    assert client.jobs.enable('job') is None


@responses.activate
def test_disable(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/disable'),
    )

    assert client.jobs.disable('job') is None
