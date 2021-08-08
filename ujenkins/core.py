from collections import namedtuple
from http import HTTPStatus
from typing import Any, Callable, Optional

from ujenkins.exceptions import JenkinsError

Response = namedtuple('Response', ['status', 'headers', 'body'])


class Jenkins:

    def __init__(self):
        ...

    @staticmethod
    def _process(response: Response, callback: Optional[Callable] = None) -> Any:
        if response.status != HTTPStatus.OK:
            raise JenkinsError(response.body)

        if not callback:
            return response.body

        return callback(response.body)

    @staticmethod
    def _validate_retry_argument(retry: dict) -> None:
        for key in retry:
            if key not in ('total', 'factor', 'statuses'):
                raise JenkinsError('Unknown key in retry argument: ' + key)

        if retry.get('total', 0) <= 0:
            raise JenkinsError('Invalid `total` in retry argument must be > 0')
