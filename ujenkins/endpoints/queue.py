import json

from typing import Dict


class Queue:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    def get(self) -> Dict[int, dict]:
        """
        Get server queue.

        Returns:
            Dict[int, dict]: id item in queue, and it's detailed information.
        """
        def callback(response):
            items = json.loads(response.body)['items']
            return {item['id']: item for item in items}

        return self.jenkins._request(
            'GET',
            '/queue/api/json',
            _callback=callback,
        )

    def get_info(self, item_id: int) -> dict:
        """
        Get info about enqueued item (build) identifier.

        Args:
            item_id (int):
                enqueued item identifier.

        Returns:
            dict: identifier information.
        """
        return self.jenkins._request(
            'GET',
            f'/queue/item/{item_id}/api/json',
        )

    def cancel(self, item_id: int) -> None:
        """
        Cancel enqueued item (build) identifier.

        Args:
            item_id (int):
                enqueued item identifier.

        Returns:
            None
        """
        return self.jenkins._request(
            'POST',
            '/queue/cancelItem',
            params=dict(id=item_id),
        )
