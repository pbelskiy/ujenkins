import re

import responses


@responses.activate
def test_get(client):
    responses.add(
        responses.GET,
        re.compile(r'.+/'),
        headers={'X-Jenkins': '2.0.129'}
    )

    version = client.system.get_version()
    assert version.major == 2
    assert version.minor == 0
    assert version.patch == 129
