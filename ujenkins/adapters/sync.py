from http import HTTPStatus
from typing import Any, Callable, List, Optional, Union

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from ujenkins.adapters import CRUMB_ISSUER_URL
from ujenkins.core import Jenkins, Response
from ujenkins.exceptions import JenkinsError, JenkinsNotFoundError


class JenkinsClient(Jenkins):

    def __init__(self,
                 url: str,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 *,
                 verify: bool = True,
                 timeout: Optional[float] = None,
                 retry: Optional[dict] = None
                 ):
        """
        Jenkins sync client class.

        Args:
            url (str):
                URL of Jenkins server.

            user (Optional[str]):
                User name, login.

            password (Optional[str]):
                Password for user.

            verify (Optional[bool]):
                Verify SSL (default: true).

            timeout (Optional[float]):
                HTTP request timeout.

            retry (Optional[dict]):
                Retry options to prevent failures if server restarting or
                temporary network problem. Disabled by default use total > 0
                to enable.

                - total: ``int`` Total retries count.
                - factor: ``int`` Sleep between retries (default 1)
                    {factor} * (2 ** ({number of total retries} - 1))
                - statuses: ``List[int]`` HTTP statues retries on. (default [])

                Example:

                .. code-block:: python

                    retry = dict(
                        total=10,
                        factor=1,
                        statuses=[500]
                    )

                With factor = 1

                ============  =============
                Retry number  Sleep
                ============  =============
                1              0.5 seconds
                2              1.0 seconds
                3              2.0 seconds
                4              4.0 seconds
                5              8.0 seconds
                6             16.0 seconds
                7             32.0 seconds
                8              1.1 minutes
                9              2.1 minutes
                10             4.3 minutes
                11             8.5 minutes
                12            17.1 minutes
                13            34.1 minutes
                14             1.1 hours
                15             2.3 hours
                16             4.6 hours
                17             9.1 hours
                18            18.2 hours
                19            36.4 hours
                20            72.8 hours
                ============  =============

        Returns:
            Client instance
        """
        super().__init__()

        self.host = url.rstrip('/')
        self.session = Session()

        if user and password:
            self.session.auth = (user, password)

        self.timeout = timeout
        self.verify = verify
        self.crumb = None  # type: Any

        if not retry:
            return

        self._validate_retry_argument(retry)
        adapter = HTTPAdapter(max_retries=Retry(
            total=retry['total'],
            backoff_factor=retry.get('factor', 1),
            status_forcelist=retry.get('statuses', []),
            method_whitelist=['GET', 'POST', 'PATCH'],
        ))

        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _http_request(self,
                      method: str,
                      path: str,
                      *,
                      callback: Optional[Callable] = None,
                      **kwargs: Any
                      ) -> Any:

        if self.timeout and 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        if self.crumb:
            kwargs.setdefault('headers', {})
            kwargs['headers'].update(self.crumb)

        response = self.session.request(
            method,
            f'{self.host}{path}',
            verify=self.verify,
            **kwargs
        )

        result = self._process(
            Response(response.status_code, response.headers, response.text),
            callback
        )

        return result

    def _get_crumb(self) -> Union[bool, dict]:
        try:
            response = self._http_request('GET', CRUMB_ISSUER_URL)
            self.crumb = {response['crumbRequestField']: response['crumb']}
            return self.crumb
        except JenkinsNotFoundError:
            return False

    def _request(self,
                 method: str,
                 path: str,
                 **kwargs: Any
                 ) -> Any:
        """
        Core class method for endpoints, which wraps auto crumb detection.
        """
        if self.crumb:
            try:
                return self._http_request(method, path, **kwargs)
            except JenkinsError as e:
                if e.status != HTTPStatus.FORBIDDEN:
                    raise

        if self.crumb is not False:
            self.crumb = self._get_crumb()

        return self._http_request(method, path, **kwargs)

    @staticmethod
    def _chain(functions: List[Callable]) -> Any:
        """
        Helper function for creating call chain for functions.
        """
        prev = None

        for func in functions:
            try:
                prev = func(prev)

                while True:
                    if callable(prev):
                        prev = prev()
                    else:
                        break
            except JenkinsError as e:
                prev = e

        return prev

    def close(self) -> None:
        """
        Close client session
        """
        self.session.close()
