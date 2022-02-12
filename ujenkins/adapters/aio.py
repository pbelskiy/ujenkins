import asyncio

from http import HTTPStatus
from typing import Any, Callable, List, Optional, Union

from aiohttp import (
    BasicAuth,
    ClientError,
    ClientResponse,
    ClientSession,
    ClientTimeout,
)

from ujenkins.adapters import CRUMB_ISSUER_URL
from ujenkins.core import Jenkins, JenkinsError, JenkinsNotFoundError, Response


class RetryClientSession:

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop], options: dict):
        self.total = options['total']
        self.factor = options.get('factor', 1)
        self.statuses = options.get('statuses', [])

        self.session = ClientSession(loop=loop)

    async def request(self, *args: Any, **kwargs: Any) -> ClientResponse:
        for total in range(self.total):
            try:
                response = await self.session.request(*args, **kwargs)
            except (ClientError, asyncio.TimeoutError) as e:
                if total + 1 == self.total:
                    raise JenkinsError from e
            else:
                if response.status not in self.statuses:
                    break

            await asyncio.sleep(self.factor * (2 ** (total - 1)))

        return response

    async def close(self) -> None:
        await self.session.close()


class AsyncJenkinsClient(Jenkins):

    session = None  # type: Union[ClientSession, RetryClientSession]
    timeout = None

    def __init__(self,
                 url: str,
                 user: Optional[str] = None,
                 password: Optional[str] = None,
                 *,
                 loop: Optional[asyncio.AbstractEventLoop] = None,
                 verify: bool = True,
                 timeout: Optional[float] = None,
                 retry: Optional[dict] = None
                 ):
        """
        Jenkins async client class.

        Args:
            url (str):
                URL of Jenkins server.

            user (Optional[str]):
                User name, login.

            password (Optional[str]):
                Password for user.

            loop (Optional[AbstractEventLoop]):
                Asyncio current event loop.

            verify (Optional[bool]):
                Verify SSL (default: true).

            timeout (Optional[int]):
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

        Returns:
            AsyncClient instance
        """
        super().__init__()

        self.loop = loop or asyncio.get_event_loop()
        self.host = url.rstrip('/')
        self.crumb = None  # type: Any

        self.auth = None
        if user and password:
            self.auth = BasicAuth(user, password)

        if retry:
            self._validate_retry_argument(retry)
            self.session = RetryClientSession(loop, retry)
        else:
            self.session = ClientSession(loop=self.loop)

        self.verify = verify

        if timeout:
            self.timeout = ClientTimeout(total=timeout)

    async def _http_request(self,
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

        response = await self.session.request(
            method,
            f'{self.host}{path}',
            auth=self.auth,
            ssl=self.verify,
            **kwargs
        )

        body = await response.text()

        result = self._process(
            Response(response.status, response.headers, body),
            callback
        )

        return result

    async def _get_crumb(self) -> Union[bool, dict]:
        try:
            response = await self._http_request('GET', CRUMB_ISSUER_URL)
            self.crumb = {response['crumbRequestField']: response['crumb']}
            return self.crumb
        except JenkinsNotFoundError:
            return False

    async def _request(self,
                       method: str,
                       path: str,
                       **kwargs: Any
                       ) -> Any:
        """
        Core class method for endpoints, which wraps auto crumb detection.
        """
        if self.crumb:
            try:
                return await self._http_request(method, path, **kwargs)
            except JenkinsError as e:
                if e.status != HTTPStatus.FORBIDDEN:
                    raise

        if self.crumb is not False:
            self.crumb = await self._get_crumb()

        return await self._http_request(method, path, **kwargs)

    @staticmethod
    async def _chain(functions: List[Callable]) -> Any:
        """
        Helper function for creating call chain of async and sync functions.
        """
        prev = None

        for func in functions:
            try:
                prev = func(prev)

                while True:
                    if asyncio.iscoroutine(prev):
                        prev = await prev  # type: ignore
                    elif callable(prev):
                        prev = prev()
                    else:
                        break
            except JenkinsError as e:
                prev = e

        return prev

    async def close(self) -> None:  # type: ignore
        """
        Close client session
        """
        await self.session.close()
