import json

from typing import Dict


class Queue:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    def get(self) -> Dict[int, dict]:
        """
        Get server builds queue.

        Returns:
            Dict[int, dict]: id in queue, and it's detailed information.
        """
        def callback(response):
            items = json.loads(response.body)['items']
            return {item['id']: item for item in items}

        return self.jenkins._request(
            'GET',
            '/queue/api/json',
            _callback=callback,
        )

    def get_info(self, identifier: int) -> dict:
        """
        Get info about enqueued build identifier.

        Args:
            id (int):
                enqueued item identifier.

        Returns:
            dict: inforrmation about enqueued build identifier.
        """
        return self.jenkins._request(
            'GET',
            f'/queue/item/{identifier}/api/json',
        )
