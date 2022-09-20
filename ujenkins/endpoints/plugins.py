import json

from typing import Dict


class Plugins:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    def get(self, depth: int = 2) -> Dict[str, dict]:
        """
        Get dict of all existed plugins in the system.

        Returns:
            Dict[str, dict] - plugin name and plugin properties.
        """
        def callback(response) -> Dict[str, dict]:
            plugins = json.loads(response.body)['plugins']
            return {p['shortName']: p for p in plugins}

        return self.jenkins._request(
            'GET',
            f'/pluginManager/api/json?depth={depth}',
            _callback=callback,
        )
