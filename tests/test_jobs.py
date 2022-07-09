import re

from http import HTTPStatus

import responses

JOBS_ALL_JSON = """{
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
      "name" : "test",
      "url" : "http://localhost:8080/job/test/",
      "color" : "red"
    },
    {
      "_class" : "com.cloudbees.hudson.plugins.folder.Folder",
      "name" : "test_folder",
      "url" : "http://localhost:8080/job/test_folder/"
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
        body=JOBS_ALL_JSON,
    )

    response = client.jobs.get()
    assert len(response) == 2
    assert 'test' in response
    # assert response[0]['name'] == 'test'


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
