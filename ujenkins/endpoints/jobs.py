import json

from functools import partial
from typing import Any, Dict, Optional

from ujenkins.exceptions import JenkinsNotFoundError


class Jobs:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    def get(self, url: str = '', depth: Optional[int] = None) -> Dict[str, dict]:
        """
        Get jobs in selected folder, by default root is used.

        Args:
            url (str):
                URL from job property, by default root is used.

            depth (Optional[int]):
                Get jobs recursively including folders from selected URL using
                depth value, default is None which means no recursion.

        Example:

        .. code-block:: python

            {'folder': {'_class': 'com.cloudbees.hudson.plugins.folder.Folder',
                        'name': 'folder',
                        'url': 'http://localhost/job/folder/'},
             'project': {'_class': 'hudson.model.FreeStyleProject',
                         'color': 'blue',
                         'name': 'project',
                         'url': 'http://localhost/job/project/'}}

        Returns:
            Dict[str, dict]: full name and job properties.
        """
        def callback(response):
            all_jobs = {}
            jobs = json.loads(response.text)['jobs']
            for job in jobs:
                all_jobs[job['name']] = job

            return all_jobs

        params = None

        if depth:
            tree = ',jobs[name,url,color'*depth + ']'*depth
            params = {'tree': tree.lstrip(',')}

        return self.jenkins._request(
            'GET',
            url + '/api/json',
            params=params,
            _callback=callback,
        )

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
            f'/{folder_name}/job/{job_name}/config.xml',
            _callback=self.jenkins._return_text,
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

    def create(self, name: str, config: str) -> None:
        """
        Create new jenkins job.

        Args:
            name (str):
                Job name.

            config (str):
                XML config of new job. It`s convenient way to use `get_config()`
                to get existing job config and change it on your taste, or to
                use `construct_config()` method.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        headers = {'Content-Type': 'text/xml'}
        params = {'name': job_name}

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/createItem',
            params=params,
            data=config,
            headers=headers
        )

    def reconfigure(self, name: str, config: str) -> None:
        """
        Reconfigure specified job name.

        Args:
            name (str):
                Job name or path (within folder).

            config (str):
                XML config of new job. It`s convenient way to use `get_config()`
                to get existing job config and change it on your taste, or to
                use `construct_config()` method.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/config.xml',
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    def delete(self, name: str) -> None:
        """
        Delete existed jenkins job.

        Args:
            name (str):
                Job name. For job in folder just use `/`.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/doDelete'
        )

    def copy(self, name: str, new_name: str) -> None:
        """
        Copy specified job.

        Args:
            name (str):
                Job name or path (within folder).

            new_name (str):
                New job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        params = {
            'mode': 'copy',
            'from': job_name,
            'name': new_name,
        }

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/createItem',
            params=params
        )

    def rename(self, name: str, new_name: str) -> None:
        """
        Rename specified job name.

        Args:
            name (str):
                Job name or path (within folder).

            new_name (str):
                New job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        params = {
            'newName': new_name
        }

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/doRename',
            params=params
        )

    def enable(self, name: str) -> None:
        """
        Enable specified job.

        Args:
            name (str):
                Job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/enable'
        )

    def disable(self, name: str) -> None:
        """
        Disable specified job.

        Args:
            name (str):
                Job name.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/disable'
        )
