import asyncio

from typing import Any, Coroutine, overload, TypeVar, Generic, Union


ClientT = TypeVar('ClientT', bound=Union['JenkinsClient', 'AsyncJenkinsClient'])


class Builds(Generic[ClientT]):
    def __init__(self, jenkins: ClientT) -> None:
        self.jenkins = jenkins

    @overload
    def get(self: 'Builds[JenkinsClient]', name: str) -> str:
        ...

    @overload
    def get(self: 'Builds[AsyncJenkinsClient]', name: str) -> Coroutine[Any, Any, str]:
        ...

    def get(self, name: str) -> str | Coroutine[Any, Any, str]:
        return self.jenkins._request(name)


class AsyncJenkinsClient:
    def __init__(self) -> None:
        self.builds = Builds(self)

    async def _request(self, name: str) -> Any:
        return name


class JenkinsClient:
    def __init__(self) -> None:
        self.builds = Builds(self)

    def _request(self, name: str) -> Any:
        return name


async def main() -> None:
    async_client = AsyncJenkinsClient()
    result = await async_client.builds.get('async')
    print(result)

    client = JenkinsClient()
    result = client.builds.get('sync')
    print(result)


asyncio.run(main())
