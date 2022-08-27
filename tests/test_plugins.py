import re

import responses

JENKINS_PLUGINS_JSON = """
{
    "_class": "hudson.LocalPluginManager",
    "plugins": [
        {
            "active": true,
            "backupVersion": null,
            "bundled": false,
            "deleted": false,
            "dependencies": [
                {
                    "optional": true,
                    "shortName": "javax-activation-api",
                    "version": "1.2.0-2"
                },
                {
                    "optional": true,
                    "shortName": "javax-mail-api",
                    "version": "1.6.2-5"
                },
                {
                    "optional": true,
                    "shortName": "instance-identity",
                    "version": "3.1"
                }
            ],
            "detached": true,
            "downgradable": false,
            "enabled": true,
            "hasUpdate": true,
            "longName": "PAM Authentication plugin",
            "pinned": false,
            "requiredCoreVersion": "2.303.3",
            "shortName": "pam-auth",
            "supportsDynamicLoad": "MAYBE",
            "url": "https://plugins.jenkins.io/pam-auth",
            "version": "1.8"
        }
    ]
}
"""


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.*/pluginManager/api/json'),
        content_type='application/json;charset=utf-8',
        body=JENKINS_PLUGINS_JSON,
    )

    response = client.plugins.get()
    assert len(response) == 1
    assert 'pam-auth' in response
