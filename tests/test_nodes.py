import re

import pytest
import responses

from ujenkins.exceptions import JenkinsError

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

RSS_BUILDS_FAILED_XML = r"""<?xml version="1.0" encoding="UTF-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Jenkins:master (failed builds)</title>
    <link rel="alternate" type="text/html" href="http://localhost:8080/computer/(master)/"></link>
    <updated>2022-06-06T21:14:09Z</updated>
    <author>
        <name>Jenkins Server</name>
    </author>
    <id>urn:uuid:903deee0-7bfa-11db-9fe1-0800200c9a66</id>
    <entry>
        <title>jobbb #15 (broken since this build)</title>
        <link rel="alternate" type="text/html" href="http://localhost:8080/job/jobbb/15/"></link>
        <id>tag:hudson.dev.java.net,2022:jobbb:15</id>
        <published>2022-06-06T21:14:09Z</published>
        <updated>2022-06-06T21:14:09Z</updated>
    </entry>
</feed>
"""

RSS_BUILDS_ALL_XML = r"""<?xml version="1.0" encoding="UTF-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">
    <title>Jenkins:master (all builds)</title>
    <link rel="alternate" type="text/html" href="http://localhost:8080/computer/(master)/"></link>
    <updated>2022-06-06T21:14:09Z</updated>
    <author>
        <name>Jenkins Server</name>
    </author>
    <id>urn:uuid:903deee0-7bfa-11db-9fe1-0800200c9a66</id>
    <entry>
        <title>jobbb #15 (broken since this build)</title>
        <link rel="alternate" type="text/html" href="http://localhost:8080/job/jobbb/15/"></link>
        <id>tag:hudson.dev.java.net,2022:jobbb:15</id>
        <published>2022-06-06T21:14:09Z</published>
        <updated>2022-06-06T21:14:09Z</updated>
    </entry>
    <entry>
        <title>jobbb #14 (stable)</title>
        <link rel="alternate" type="text/html" href="http://localhost:8080/job/jobbb/14/"></link>
        <id>tag:hudson.dev.java.net,2021:jobbb:14</id>
        <published>2021-08-10T21:02:55Z</published>
        <updated>2021-08-10T21:02:55Z</updated>
    </entry>
    <entry>
        <title>jobbb #13 (stable)</title>
        <link rel="alternate" type="text/html" href="http://localhost:8080/job/jobbb/13/"></link>
        <id>tag:hudson.dev.java.net,2021:jobbb:13</id>
        <published>2021-08-10T21:02:06Z</published>
        <updated>2021-08-10T21:02:06Z</updated>
    </entry>
</feed>
"""

NODE_CONFIG_XML = r"""<?xml version="1.1" encoding="UTF-8"?>
<slave>
  <name>buildbot</name>
  <description></description>
  <remoteFS>/home/user/jenkins</remoteFS>
  <numExecutors>2</numExecutors>
  <mode>NORMAL</mode>
  <retentionStrategy class="hudson.slaves.RetentionStrategy$Always"/>
  <launcher class="hudson.slaves.JNLPLauncher">
    <workDirSettings>
      <disabled>false</disabled>
      <internalDir>remoting</internalDir>
      <failIfWorkDirIsMissing>false</failIfWorkDirIsMissing>
    </workDirSettings>
    <webSocket>false</webSocket>
  </launcher>
  <label></label>
  <nodeProperties/>
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODES_JSON,
    )

    response = client.nodes.get()
    assert len(response) == 1


@responses.activate
def test_get_failed_builds(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/rssFailed'),
        content_type='application/atom+xml;charset=UTF-8',
        body=RSS_BUILDS_FAILED_XML,
    )

    response = client.nodes.get_failed_builds('master')
    assert len(response) == 1
    assert response[0]['url'] == 'http://localhost:8080/job/jobbb/15/'
    assert response[0]['job_name'] == 'jobbb'
    assert response[0]['number'] == 15


@responses.activate
def test_get_all_builds(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/rssAll'),
        content_type='application/atom+xml;charset=UTF-8',
        body=RSS_BUILDS_ALL_XML,
    )

    response = client.nodes.get_all_builds('master')
    assert len(response) == 3


@responses.activate
def test_get_info(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODE_INFO_JSON,
    )

    response = client.nodes.get_info('master')
    assert response['numExecutors'] == 2


@responses.activate
def test_get_config(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/config.xml'),
        content_type='application/xml',
        body=NODE_CONFIG_XML,
    )

    response = client.nodes.get_config('buildbot')
    assert '<name>buildbot</name>' in response


@responses.activate
def test_is_exists(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/api/json'),
        status=404,
    )

    client.nodes.is_exists('master')


@responses.activate
def test_create(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODES_JSON,
    )

    responses.add(
        responses.POST,
        re.compile(r'.+/computer/doCreateItem'),
    )

    client.nodes.create('buildbot', {})


@responses.activate
def test_delete(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/computer/.+/doDelete'),
    )

    client.nodes.delete('buildbot')


@responses.activate
def test_reconfigure(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/computer/.+/config.xml'),
    )

    client.nodes.reconfigure('buildbot', NODE_CONFIG_XML)

    with pytest.raises(JenkinsError):
        client.nodes.reconfigure('(master)', NODE_CONFIG_XML)


@pytest.mark.asyncio
async def test_async_enable(aiohttp_mock, async_client):
    aiohttp_mock.get(
        re.compile(r'.+/computer/.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODE_INFO_JSON,
    )

    aiohttp_mock.post(
        re.compile(r'.+/computer/.+/toggleOffline'),
        content_type='text/plain',
        body='',
    )

    await async_client.nodes.enable('master')


@responses.activate
def test_sync_enable(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODE_INFO_JSON,
    )

    responses.add(
        responses.POST,
        re.compile(r'.+/computer/.+/toggleOffline'),
        content_type='text/plain',
        body='',
    )

    client.nodes.enable('master')


@responses.activate
def test_disable(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/computer/.+/api/json'),
        content_type='application/json;charset=utf-8',
        body=NODE_INFO_JSON.replace('"offline" : true,', '"offline" : false,'),
    )

    responses.add(
        responses.POST,
        re.compile(r'.+/computer/.+/toggleOffline'),
        content_type='text/plain',
        body='',
    )

    client.nodes.disable('master')


@responses.activate
def test_update_offline_reason(client):
    responses.add(
        responses.POST,
        re.compile(r'.+/computer/.+/changeOfflineCause'),
    )

    client.nodes.update_offline_reason('buildbot', 'maintenance')
