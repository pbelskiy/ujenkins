from typing import NamedTuple

from ujenkins.exceptions import JenkinsError

JenkinsVersion = NamedTuple(
    'JenkinsVersion', [('major', int), ('minor', int), ('patch', int)]
)


class System:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    def get_version(self) -> JenkinsVersion:
        """
        Get server version.

        Returns:
            JenkinsVersion: named tuple with minor, major, patch version.
        """
        def callback(response):
            header = response.headers.get('X-Jenkins')
            if not header:
                raise JenkinsError('Header `X-Jenkins` isn`t found in response')

            return JenkinsVersion(*map(int, header.split('.')))

        return self.jenkins._request('GET', '/', callback=callback)
