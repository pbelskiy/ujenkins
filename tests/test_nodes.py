import re

import responses

NODES_JSON = """{
  "_class" : "hudson.model.ComputerSet",
  "busyExecutors" : 0,
  "computer" : [
    {
      "_class" : "hudson.model.Hudson$MasterComputer",
      "actions" : [

      ],
      "assignedLabels" : [
        {
          "name" : "master"
        }
      ],
      "description" : "the master Jenkins node",
      "displayName" : "master",
      "executors" : [
        {

        },
        {

        }
      ],
      "icon" : "computer-x.png",
      "iconClassName" : "icon-computer-x",
      "idle" : true,
      "jnlpAgent" : false,
      "launchSupported" : true,
      "loadStatistics" : {
        "_class" : "hudson.model.Label$1"
      },
      "manualLaunchAllowed" : true,
      "monitorData" : {
        "hudson.node_monitors.SwapSpaceMonitor" : {
          "_class" : "hudson.node_monitors.SwapSpaceMonitor$MemoryUsage2",
          "availablePhysicalMemory" : 78348288,
          "availableSwapSpace" : 1013350400,
          "totalPhysicalMemory" : 2082197504,
          "totalSwapSpace" : 1073737728
        },
        "hudson.node_monitors.TemporarySpaceMonitor" : {
          "_class" : "hudson.node_monitors.DiskSpaceMonitorDescriptor$DiskSpace",
          "timestamp" : 1632064529510,
          "path" : "/tmp",
          "size" : 502632448
        },
        "hudson.node_monitors.DiskSpaceMonitor" : {
          "_class" : "hudson.node_monitors.DiskSpaceMonitorDescriptor$DiskSpace",
          "timestamp" : 1632064529508,
          "path" : "/var/jenkins_home",
          "size" : 502632448
        },
        "hudson.node_monitors.ArchitectureMonitor" : "Linux (amd64)",
        "hudson.node_monitors.ResponseTimeMonitor" : {
          "_class" : "hudson.node_monitors.ResponseTimeMonitor$Data",
          "timestamp" : 1632064529535,
          "average" : 0
        },
        "hudson.node_monitors.ClockMonitor" : {
          "_class" : "hudson.util.ClockDifference",
          "diff" : 0
        }
      },
      "numExecutors" : 2,
      "offline" : true,
      "offlineCause" : {
        "_class" : "hudson.node_monitors.DiskSpaceMonitorDescriptor$DiskSpace"
      },
      "offlineCauseReason" : "Disk space is too low. Only 0.479GB left on /var/jenkins_home.",
      "oneOffExecutors" : [

      ],
      "temporarilyOffline" : true
    }
  ],
  "displayName" : "Nodes",
  "totalExecutors" : 0
}
"""

NODE_INFO_JSON = """{
  "_class" : "hudson.model.Hudson$MasterComputer",
  "actions" : [

  ],
  "assignedLabels" : [
    {
      "name" : "master"
    }
  ],
  "description" : "the master Jenkins node",
  "displayName" : "master",
  "executors" : [
    {

    },
    {

    }
  ],
  "icon" : "computer-x.png",
  "iconClassName" : "icon-computer-x",
  "idle" : true,
  "jnlpAgent" : false,
  "launchSupported" : true,
  "loadStatistics" : {
    "_class" : "hudson.model.Label$1"
  },
  "manualLaunchAllowed" : true,
  "monitorData" : {
    "hudson.node_monitors.SwapSpaceMonitor" : {
      "_class" : "hudson.node_monitors.SwapSpaceMonitor$MemoryUsage2",
      "availablePhysicalMemory" : 77758464,
      "availableSwapSpace" : 957181952,
      "totalPhysicalMemory" : 2082197504,
      "totalSwapSpace" : 1073737728
    },
    "hudson.node_monitors.TemporarySpaceMonitor" : {
      "_class" : "hudson.node_monitors.DiskSpaceMonitorDescriptor$DiskSpace",
      "timestamp" : 1632068934040,
      "path" : "/tmp",
      "size" : 502603776
    },
    "hudson.node_monitors.DiskSpaceMonitor" : {
      "_class" : "hudson.node_monitors.DiskSpaceMonitorDescriptor$DiskSpace",
      "timestamp" : 1632068934037,
      "path" : "/var/jenkins_home",
      "size" : 502603776
    },
    "hudson.node_monitors.ArchitectureMonitor" : "Linux (amd64)",
    "hudson.node_monitors.ResponseTimeMonitor" : {
      "_class" : "hudson.node_monitors.ResponseTimeMonitor$Data",
      "timestamp" : 1632068934043,
      "average" : 0
    },
    "hudson.node_monitors.ClockMonitor" : {
      "_class" : "hudson.util.ClockDifference",
      "diff" : 0
    }
  },
  "numExecutors" : 2,
  "offline" : true,
  "offlineCause" : {
    "_class" : "hudson.node_monitors.DiskSpaceMonitorDescriptor$DiskSpace"
  },
  "offlineCauseReason" : "Disk space is too low. Only 0.479GB left on /var/jenkins_home.",
  "oneOffExecutors" : [

  ],
  "temporarilyOffline" : true
}
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/computer/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODES_JSON,
    )

    response = client.nodes.get()
    assert len(response) == 1


@responses.activate
def test_get_info(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/computer/.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODE_INFO_JSON,
    )

    response = client.nodes.get_info('master')
    assert response['numExecutors'] == 2
