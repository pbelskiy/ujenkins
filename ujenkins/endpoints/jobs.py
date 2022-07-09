import json

from functools import partial
from typing import Any, Dict

from ujenkins.exceptions import JenkinsNotFoundError


class Jobs:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    def _get_all_jobs(self, url: str, parent: str) -> Dict[str, dict]:

        def callback(response):
            all_jobs = {}

            jobs = json.loads(response.body)['jobs']
            for job in jobs:
                all_jobs[parent + job['name']] = job

            return all_jobs

        return self.jenkins._request(
            'GET',
            url + '/api/json',
            params=dict(tree='jobs'),
            callback=callback,
        )

    def get(self) -> Dict[str, dict]:
        """
        Get dict of all existed jobs in system, including jobs in folder.

        Example:

        .. code-block:: python

            {
                'test': {
                    'name': 'test',
                    'url': 'http://localhost/job/test/'
                },
                'folder/foo': {
                    'name': 'folder/job',
                    'url': 'http://localhost/job/folder/job/foo/'
                }
            }

        Returns:
            Dict[str, dict]: name and job properties.
        """
        return self._get_all_jobs('', '')

    def get_info(self, name: str) -> dict:
        """
        Get detailed information of specified job.

        Args:
            name (str):
                Job name.

        Returns:
            dict: job information.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/api/json'
        )

    def get_config(self, name: str) -> str:
        """
        Get XML config of a specified job.

        Args:
            name (str):
                Job name.

        Returns:
            str: XML config
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/config.xml'
        )

    def is_exists(self, name: str) -> bool:
        """
        Checks if the job exists.

        Args:
            name (str):
                Job name.

        Returns:
            bool: job exists.
        """
        if name == '':
            return False

        def callback1(_) -> Any:
            return partial(self.get_info, name)

        def callback2(response: Any) -> bool:
            if isinstance(response, JenkinsNotFoundError):
                return False

            return True

        return self.jenkins._chain([callback1, callback2])
