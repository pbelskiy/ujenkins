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
