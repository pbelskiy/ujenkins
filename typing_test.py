import asyncio

from typing import Any


class Builds:
    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    def get(self, name: str) -> str:
        return self.jenkins._request(name)


class Jenkins:
    def __init__(self) -> None:
        self.builds = Builds(self)


class AsyncJenkinsClient(Jenkins):
    async def _request(self, name: str) -> Any:
        return name


class JenkinsClient(Jenkins):
    def _request(self, name: str) -> Any:
        return name


async def main():
    client = AsyncJenkinsClient()
    result = await client.builds.get('async')
    print(result)

    client = JenkinsClient()
    result = client.builds.get('sync')
    print(result)


asyncio.run(main())
