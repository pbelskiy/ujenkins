import re

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
