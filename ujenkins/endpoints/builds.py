import json

from typing import Any, List, Optional


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

            .. code-block:: python

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
            f'/{folder_name}/job/{job_name}/api/json?tree=allBuilds[number,url]',
            callback=callback,
        )

    def get_info(self, name: str, build_id: int) -> dict:
        """
        Get detailed information about specified build number of job.

        Args:
            name (str): job name or path (if in folder).
            build_id (int): build identifier.

        Returns:
            dict: information about build.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/api/json'
        )

    def get_output(self, name: str, build_id: int) -> str:
        """
        Get console output of specified build.

        Args:
            name (str): job name or path (if in folder).
            build_id (int): build identifier.

        Returns:
            str: build output.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/consoleText'
        )

    def start(self,
              name: str,
              parameters: Optional[dict] = None,
              delay: Optional[int] = 0
              ) -> Optional[int]:
        """
        Enqueue new build with delay (default is 0 seconds, means immediately)

        Note about delay (quiet-period):
        https://www.jenkins.io/blog/2010/08/11/quiet-period-feature/

        Args:
            name (str): job name or path (if in folder).
            parameters (int): parameters of triggering build.
            delay (int): delay before start.

        Returns:
            Optional[int]: queue item id.
        """
        def callback(response) -> Optional[int]:
            # FIXME: on Jenkins 1.554 there is problem, no queue id returned
            queue_item_url = response.headers['location']
            try:
                queue_id = queue_item_url.rstrip('/').split('/')[-1]
                return int(queue_id)
            except ValueError:
                return None

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        path = f'/{folder_name}/job/{job_name}'

        data = None

        if parameters:
            formatted_parameters = [
                {'name': k, 'value': str(v)} for k, v in parameters.items()
            ]  # type: Any

            if len(formatted_parameters) == 1:
                formatted_parameters = formatted_parameters[0]

            data = {
                'json': json.dumps({
                    'parameter': formatted_parameters,
                    'statusCode': '303',
                    'redirectTo': '.',
                }),
                **parameters,
            }
            path += '/buildWithParameters'
        else:
            path += '/build'

        return self.jenkins._request(
            'POST',
            path,
            callback=callback,
            params={'delay': delay},
            data=data,
        )

    def stop(self, name: str, build_id: int) -> None:
        """
        Stop specified build.

        Args:
            name (str): job name or path (if in folder).
            build_id (int): build identifier.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/{build_id}/stop'
        )

    def delete(self, name: str, build_id: int) -> None:
        """
        Delete specified build.

        Args:
            name (str): job name or path (if in folder).
            build_id (int): build identifier.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/{build_id}/doDelete'
        )
