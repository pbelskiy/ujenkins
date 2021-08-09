import json

from typing import List, Optional


class Builds:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    def get(self, name: str) -> List[dict]:
        """
        Get list of builds for specified job.

        Args:
            name (str): job name or path (if in folder).

        Returns:
            List: list of build for specified job.
            builds = [
              {'number': 1, 'url': 'http://localhost/job/test/1/'},
              {'number': 2, 'url': 'http://localhost/job/test/2/'}
            ]
        """
        def callback(response) -> List[dict]:
            return json.loads(response.body)['allBuilds']

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            '/{}/job/{}/api/json?tree=allBuilds[number,url]'.format(
                folder_name,
                job_name
            ),
            callback=callback,
        )
