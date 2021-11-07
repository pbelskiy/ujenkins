import json

from functools import partial
from typing import Any, Dict


class Nodes:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    @staticmethod
    def _normalize_name(name: str) -> str:
        # embedded node `master` actually have brackets in HTTP requests
        if name == 'master':
            return '(master)'
        return name

    def get(self) -> Dict[str, dict]:
        """
        Get all available nodes on server.

        Example:

        .. code-block:: python

            {
                "master": dict(...),
                "buildbot1": dict(...)
            }

        Returns:
            Dict[str, dict]: node name, and it`s detailed information.
        """
        def callback(response):
            nodes = json.loads(response.body)
            return {v['displayName']: v for v in nodes['computer']}

        return self.jenkins._request(
            'GET',
            '/computer/api/json',
            callback=callback,
        )

    def get_info(self, name: str) -> dict:
        """
        Get node detailed information.

        Args:
            name (str): node name.

        Returns:
            dict: detailed node information.
        """
        name = self._normalize_name(name)

        return self.jenkins._request(
            'GET',
            '/computer/{}/api/json'.format(name),
        )

    def get_config(self, name: str) -> str:
        """
        Return node config in XML format.

        Args:
            name (str): node name.

        Returns:
            str: node config.
        """
        name = self._normalize_name(name)

        return self.jenkins._request(
            'GET',
            '/computer/{}/config.xml'.format(name)
        )

    def enable(self, name: str) -> None:
        """
        Enable node.

        Args:
            name (str): node name.

        Returns:
            None
        """
        name = self._normalize_name(name)

        def callback1(_) -> Any:
            return partial(self.get_info, name)

        def callback2(response: dict) -> None:
            if not response['offline']:
                return None

            return self.jenkins._request('POST', '/computer/{}/toggleOffline'.format(name))

        return self.jenkins._chain([callback1, callback2])
