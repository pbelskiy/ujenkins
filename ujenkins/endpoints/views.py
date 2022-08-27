import json

from typing import Dict

from ujenkins.exceptions import JenkinsError


class Views:

    def __init__(self, jenkins) -> None:
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
            _callback=callback,
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
            _callback=self.jenkins._return_body,
        )

    def create(self, name: str, config: str) -> None:
        """
        Create view using XML config.

        Args:
            name (str):
                View name.

            config (str):
                XML config.

        Returns:
            None
        """
        def callback1(_):
            return self.get

        def callback2(response: dict) -> None:
            if name in response:
                raise JenkinsError(f'View `{name}` is already exists')

            headers = {'Content-Type': 'text/xml'}
            params = {'name': name}

            return self.jenkins._request(
                'POST',
                '/createView',
                data=config,
                params=params,
                headers=headers,
            )

        return self.jenkins._chain([callback1, callback2])

    def reconfigure(self, name: str, config: str) -> None:
        """
        Reconfigure view using XML config.

        Args:
            name (str):
                View name.

            config (str):
                XML config.

        Returns:
            None
        """
        return self.jenkins._request(
            'POST',
            f'/view/{name}/config.xml',
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    def delete(self, name: str) -> None:
        """
        Delete view.

        Args:
            name (str):
                View name.

        Returns:
            None
        """
        return self.jenkins._request('POST', f'/view/{name}/doDelete')
