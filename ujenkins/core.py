import json

from collections import namedtuple
from http import HTTPStatus
from typing import Any, Callable, Optional, Tuple

from ujenkins.endpoints import Builds, Nodes, System
from ujenkins.exceptions import JenkinsError, JenkinsNotFoundError

Response = namedtuple('Response', ['status', 'headers', 'body'])


class Jenkins:

    def __init__(self):
        self.builds = Builds(self)
        self.nodes = Nodes(self)
        self.system = System(self)

    @staticmethod
    def _process(response: Response, callback: Optional[Callable] = None) -> Any:

        if response.status == HTTPStatus.NOT_FOUND:
            raise JenkinsNotFoundError(response.body)

        if response.status >= HTTPStatus.BAD_REQUEST:
            if response.status in (
                    HTTPStatus.UNAUTHORIZED,
                    HTTPStatus.FORBIDDEN,
                    HTTPStatus.INTERNAL_SERVER_ERROR):
                details = 'probably authentication problem:\n' + response.body
            else:
                details = '\n' + response.body

            raise JenkinsError(
                f'Request error [{response.status}], {details}',
                status=response.status,
            )

        # TODO: add response type annotations, parse json for callback
        if callback:
            return callback(response)

        if 'application/json' in response.headers.get('Content-Type', ''):
            return json.loads(response.body)

        return response.body

    @staticmethod
    def _get_folder_and_job_name(name: str) -> Tuple[str, str]:
        parts = name.split('/')

        job_name = parts[-1]
        folder_name = ''

        for folder in parts[:-1]:
            folder_name += f'job/{folder}/'

        return folder_name, job_name

    @staticmethod
    def _validate_retry_argument(retry: dict) -> None:
        for key in retry:
            if key not in ('total', 'factor', 'statuses'):
                raise JenkinsError('Unknown key in retry argument: ' + key)

        if retry.get('total', 0) <= 0:
            raise JenkinsError('Invalid `total` in retry argument must be > 0')
