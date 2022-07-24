JENKINS_INFO_JSON = """
{
    "_class": "hudson.model.Hudson",
    "assignedLabels": [
        {
            "name": "built-in"
        }
    ],
    "description": null,
    "jobs": [
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
    "mode": "NORMAL",
    "nodeDescription": "the Jenkins controller's built-in node",
    "nodeName": "",
    "numExecutors": 2,
    "overallLoad": {},
    "primaryView": {
        "_class": "hudson.model.AllView",
        "name": "all",
        "url": "http://localhost:8080/"
    },
    "quietDownReason": null,
    "quietingDown": false,
    "slaveAgentPort": 50000,
    "unlabeledLoad": {
        "_class": "jenkins.model.UnlabeledLoadStatistics"
    },
    "url": "http://localhost:8080/",
    "useCrumbs": true,
    "useSecurity": true,
    "views": [
        {
            "_class": "hudson.model.AllView",
            "name": "all",
            "url": "http://localhost:8080/"
        },
        {
            "_class": "hudson.model.MyView",
            "name": "another",
            "url": "http://localhost:8080/view/another/"
        },
        {
            "_class": "hudson.model.ListView",
            "name": "my_view",
            "url": "http://localhost:8080/view/my_view/"
        }
    ]
}
"""
