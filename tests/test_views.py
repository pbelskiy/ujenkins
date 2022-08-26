import re

import responses

from tests import JENKINS_INFO_JSON

JENKINS_VIEW_CONFIG_XML = """
<?xml version="1.1" encoding="UTF-8"?>
<hudson.model.ListView>
  <name>my_view</name>
  <filterExecutors>false</filterExecutors>
  <filterQueue>false</filterQueue>
  <properties class="hudson.model.View$PropertyList"/>
  <jobNames>
    <comparator class="java.lang.String$CaseInsensitiveComparator"/>
  </jobNames>
  <jobFilters/>
  <columns>
    <hudson.views.StatusColumn/>
    <hudson.views.WeatherColumn/>
    <hudson.views.JobColumn/>
    <hudson.views.LastSuccessColumn/>
    <hudson.views.LastFailureColumn/>
    <hudson.views.LastDurationColumn/>
    <hudson.views.BuildButtonColumn/>
  </columns>
  <recurse>false</recurse>
</hudson.model.ListView>
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=JENKINS_INFO_JSON,
    )

    response = client.views.get()
    assert len(response) == 3
    assert 'my_view' in response


@responses.activate
def test_is_exists(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=JENKINS_INFO_JSON,
    )

    assert client.views.is_exists('extra') is False


@responses.activate
def test_get_config(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/view/.+/config.xml'),
        content_type='application/xml',
        body=JENKINS_VIEW_CONFIG_XML,
    )

    config = client.views.get_config('buildbot')
    assert '<name>my_view</name>' in config


@responses.activate
def test_create(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/api/json'),
        body=JENKINS_INFO_JSON,
    )

    responses.add(
        responses.POST,
        re.compile(r'.*/createView'),
    )

    assert client.views.create('new_view', JENKINS_VIEW_CONFIG_XML) is None
    assert len(responses.calls) == 2


@responses.activate
def test_reconfigure(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/view/.+/config.xml'),
    )

    assert client.views.reconfigure('new_view', JENKINS_VIEW_CONFIG_XML) is None


@responses.activate
def test_delete(client):
    responses.add(
        responses.POST,
        re.compile(r'.*/view/.+/doDelete'),
    )

    assert client.views.delete('new_view') is None
