import json

from typing import Dict


class Views:

    def __init__(self, jenkins):
        self.jenkins = jenkins

    def get(self) -> Dict[str, dict]:
        """
        Get views and their details.

        Returns:
            Dict[str, dict]: plugin name and plugin properties.
        """
        def callback(response):
            views = json.loads(response.body)['views']
            return {v['name']: v for v in views}

        return self.jenkins._request(
            'GET',
            '/api/json',
            callback=callback,
        )

    def is_exists(self, name: str) -> bool:
        """
        Check if view exists.

        Args:
            name (str):
                View name.

        Returns:
            bool: view existing.
        """
        def callback1(_):
            return self.get

        def callback2(response):
            return name in response

        return self.jenkins._chain([callback1, callback2])

    def get_config(self, name: str) -> str:
        """
        Return view config in XML format.

        Args:
            name (str):
                View name.

        Returns:
            str: XML config of view.
        """
        return self.jenkins._request(
            'GET',
            f'/view/{name}/config.xml',
            callback=self.jenkins._return_body,
        )
