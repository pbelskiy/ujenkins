import json

from functools import partial
from typing import Any, List, Optional, Union, Dict, cast

from ujenkins.exceptions import JenkinsError


class Builds:
    """
    List of Jenkins tags which can be used insted of build_id number.

    - lastBuild
    - lastCompletedBuild
    - lastFailedBuild
    - lastStableBuild
    - lastSuccessfulBuild
    - lastUnstableBuild
    - lastUnsuccessfulBuild
    """
    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    def get(self,
            name: str,
            *,
            fields: Optional[List[str]] = None,
            start: Optional[int] = None,
            end: Optional[int] = None
            ) -> List[dict]:
        """
        Get list of builds for specified job.

        Available fields in jenkins:
            - _class
            - actions
            - artifacts
            - building
            - description
            - displayName
            - duration
            - estimatedDuration
            - executor
            - fingerprint
            - fullDisplayName
            - id
            - keepLog
            - number
            - queueId
            - result
            - timestamp
            - url
            - changeSets
            - culprits
            - inProgress
            - nextBuild
            - previousBuild

        Use * inside the list to get all fields.
        Example:

        .. code-block:: python

            builds = [
                {'number': 1, 'url': 'http://localhost/job/test/1/'},
                {'number': 2, 'url': 'http://localhost/job/test/2/'}
            ]

        Args:
            name (str):
                Job name or path (if in folder).

            fields (Optional[List]):
                List of fields to return.
                Possible values are mentioned in the available fields.
                If empty, default fields will be returned.

            start (Optional[int]):
                The start index of the builds to retrieve.
                Used with the 'end' parameter to specify a range.
                Defaults to None.

            end (Optional[int]):
                The end index of the builds to retrieve.
                Used with the 'start' parameter to specify a range.
                Defaults to None.

        Returns:
            List[dict]: list of builds for specified job.
        """

        def callback(response) -> List[dict]:
            return json.loads(response.text)['allBuilds']

        pagination = ''
        if end is not None or start is not None:
            start_str = start if start is not None else ''
            end_str = end if end is not None else ''
            pagination = f'{{{start_str},{end_str}}}'

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/api/json?tree=allBuilds[number,url]',
            _callback=callback,
        )

    def get_build_ids(self, job_name: str, axis: str) -> List[int]:
        """
        Get list of build ids for specified job.

        Args:
            name (str):
                Job name or path (if in folder).

        Returns:
            List[int]: list of build ids for specified job.
        """

        def callback(response) -> List[int]:
            # TODO: handle empty matrix
            return [d["number"] for d in json.loads(response.text)['allBuilds']]

        return self.jenkins._request(
            'GET',
            f'/job/{job_name}/{axis}/api/json?tree=allBuilds[number]',
            _callback=callback,
        )

    def get_matrix_axis_names(self, job_name: str) -> List[str]:
        def callback(response) -> List[str]:
            # TODO: handle empty matrix
            return [d["name"] for d in json.loads(response.text)['activeConfigurations']]

        return self.jenkins._request(
            'GET',
            f'/job/{job_name}/api/json?tree=activeConfigurations[name]',
            _callback=callback,
        )

    def get_info(self, name: str, build_id: Union[int, str]) -> dict:
        """
        Get detailed information about specified build number of job.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            dict: information about build.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/api/json'
        )

    def get_matrix_info(self, job_name: str, axis: str, build_id: Union[int, str]) -> dict:
        """
        Get detailed information about specified build number of job.

        Args:
            job_name (str):
                Job name.

            axis (str):
                Axis value

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            dict: information about build.
        """

        return self.jenkins._request(
            'GET',
            f'/job/{job_name}/{axis}/{build_id}/api/json'
        )
    
    def get_matrix_test_report(
        self,
        job_name: str,
        axis: str,
        build_id: Union[int, str],
    ) -> Dict[str, Any]:
        """
        Get test report for specified build number of job.

        Args:
            job_name (str):
                Job name.

            axis (str):
                Axis value

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            dict: test report.
        """

        return cast(
            Dict[str, Any],
            self.jenkins._request(
                'GET',
                f'/job/{job_name}/{axis}/{build_id}/testReport/api/json'
            )
        )

    def get_output(self, name: str, build_id: Union[int, str]) -> str:
        """
        Get console output of specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            str: build output.
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/consoleText',
            _callback=self.jenkins._return_text,
        )

    def get_artifact(self, name: str, build_id: Union[int, str], path: str) -> bytes:
        """
        Get artifact content of specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

            path (str):
                Relative path to build artifact, could be used from ``get_info()``
                or ``get_list_artifacts()``, or just well known name.

        Returns:
            bytes: artifact content.
        """
        def callback(response) -> bytes:
            return response.content

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'GET',
            f'/{folder_name}/job/{job_name}/{build_id}/artifact/{path}',
            _raw_content=True,
            _callback=callback,
        )

    def get_list_artifacts(self, name: str, build_id: Union[int, str]) -> List[dict]:
        """
        Get list of build artifacts.

        Example:

            .. code-block:: python

                [
                    {
                        'name': 'photo.jpg',
                        'path': 'photo.jpg',
                        'url': 'http://server/job/my_job/31/artifact/photo.jpg'
                    }
                ]

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            List[dict]: list of build artifacts.
        """
        def callback1(_) -> Any:
            return partial(self.get_info, name, build_id)

        def callback2(response: Any):
            if isinstance(response, JenkinsError):
                raise response

            artifacts = []

            for artifact in response['artifacts']:
                artifacts.append({
                    'name': artifact['fileName'],
                    'path': artifact['relativePath'],
                    'url': root_url + artifact['relativePath'],
                })

            return artifacts

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        root_url = (
            self.jenkins.host +
            f'/{folder_name}/job/{job_name}/{build_id}/artifact/'
        )

        return self.jenkins._chain([callback1, callback2])
    
    def get_matrix_list_artifacts(self, job_name: str, axis: str, build_id: Union[int, str]) -> List[dict]:
        """
        Get list of build artifacts.

        Example:

            .. code-block:: python

                [
                    {
                        'name': 'photo.jpg',
                        'path': 'photo.jpg',
                        'url': 'http://server/job/my_job/31/artifact/photo.jpg'
                    }
                ]

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            List[dict]: list of build artifacts.
        """
        def callback1(_) -> Any:
            return partial(self.get_matrix_info, job_name, axis, build_id)

        def callback2(response: Any):
            if isinstance(response, JenkinsError):
                raise response

            artifacts = []

            for artifact in response['artifacts']:
                artifacts.append({
                    'name': artifact['fileName'],
                    'path': artifact['relativePath'],
                    'url': root_url + artifact['relativePath'],
                })

            return artifacts

        root_url = (
            self.jenkins.host +
            f'/job/{job_name}/{axis}/{build_id}/artifact/'
        )

        return self.jenkins._chain([callback1, callback2])

    def start(self,
              name: str,
              parameters: Optional[Any] = None,
              delay: int = 0,
              **kwargs: Any
              ) -> Optional[int]:
        """
        Enqueue new build with delay (default is 0 seconds, means immediately)

        Note about delay (quiet-period):
        https://www.jenkins.io/blog/2010/08/11/quiet-period-feature/

        Args:
            name (str):
                Job name or path (if in folder).

            parameters (Optional[Any]):
                Parameters of triggering build as dict or argument, also
                parameters can be passed as kwargs.

                Examples:

                .. code-block:: python

                    start(..., parameters=dict(a=1, b='string'))
                    start(..., a=1, b='string')
                    start(..., parameters=1)
                    start(..., parameters(a=1, b='string'), c=3)

            delay (int):
                Delay before start, default is 0, no delay.

        Returns:
            Optional[int]: queue item id.

        Raises:
            JenkinsNotFoundError: in case build with same arg already enqueued.
        """
        def callback(response) -> Optional[int]:
            queue_item_url = response.headers['location']
            try:
                queue_id = queue_item_url.rstrip('/').split('/')[-1]
                return int(queue_id)
            except ValueError:
                # no queue id returned on Jenkins 1.554
                return None

        def format_data(parameters: Optional[dict], kwargs: Any) -> Optional[dict]:
            if not (parameters or kwargs):
                return None

            # backward compatibility
            if isinstance(parameters, dict):
                parameters.update(**kwargs)
            elif parameters is None:
                parameters = kwargs
            else:
                parameters = {'parameters': parameters}
                parameters.update(**kwargs)

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

            return data

        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)
        path = f'/{folder_name}/job/{job_name}'

        data = format_data(parameters, kwargs)
        if data:
            path += '/buildWithParameters'
        else:
            path += '/build'

        return self.jenkins._request(
            'POST',
            path,
            params={'delay': f'{delay}sec'},
            data=data,
            _callback=callback,
        )

    def stop(self, name: str, build_id: Union[int, str]) -> None:
        """
        Stop specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/{build_id}/stop'
        )

    def delete(self, name: str, build_id: Union[int, str]) -> None:
        """
        Delete specified build.

        Args:
            name (str):
                Job name or path (if in folder).

            build_id (int):
                Build number or some of standard tags like `lastBuild`.

        Returns:
            None
        """
        folder_name, job_name = self.jenkins._get_folder_and_job_name(name)

        return self.jenkins._request(
            'POST',
            f'/{folder_name}/job/{job_name}/{build_id}/doDelete'
        )
