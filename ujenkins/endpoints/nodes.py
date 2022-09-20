import json
import xml.etree.ElementTree

from functools import partial
from typing import Any, Dict, List

from ujenkins.exceptions import JenkinsError, JenkinsNotFoundError
from ujenkins.helpers import parse_build_url


def _parse_rss(rss: str) -> List[dict]:
    builds = []
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    root = xml.etree.ElementTree.fromstring(rss)
    for entry in root.findall('atom:entry', ns):
        link = entry.find('atom:link', ns)
        if link is not None:
            build_url = link.attrib['href']
            job_name, build_id = parse_build_url(build_url)

            builds.append({
                'url': build_url,
                'job_name': job_name,
                'number': build_id,
            })

    return list(reversed(builds))


class Nodes:

    def __init__(self, jenkins) -> None:
        self.jenkins = jenkins

    @staticmethod
    def _normalize_name(name: str) -> str:
        # embedded node `master` actually have brackets in HTTP requests
        if name in ('master', 'Built-In Node'):
            return '(master)'
        return name

    def get(self) -> Dict[str, dict]:
        """
        Get all available nodes on server.

        Returns:
            Dict[str, dict]: node name, and it`s detailed information.

        Example:

        .. code-block:: python

            response = {
                "master": dict(...),
                "buildbot1": dict(...)
            }

        """
        def callback(response):
            nodes = json.loads(response.body)
            return {v['displayName']: v for v in nodes['computer']}

        return self.jenkins._request(
            'GET',
            '/computer/api/json',
            _callback=callback,
        )

    def get_failed_builds(self, name: str) -> List[dict]:
        """
        Return list of detalizied failed builds for node name. Actually it
        parsed from RSS feed. usefull for build restart. Ascending builds sort.

        Args:
            name (str):
                Node name.

        Returns:
            List[dict]: builds and their information.

        Example:

        .. code-block:: python

            response = [{
                'job_name': 'test',
                'number': 1,
                'url': 'http://localhost:8080/job/test/1/'
            }]
        """
        def callback(response) -> List[dict]:
            return _parse_rss(response.body)

        name = self._normalize_name(name)

        return self.jenkins._request(
            'GET',
            f'/computer/{name}/rssFailed',
            _callback=callback
        )

    def get_all_builds(self, name: str) -> List[dict]:
        """
        Return list of all detalizied builds for node name, actually it parsed
        from RSS feed. Ascending builds sort.

        Args:
            name (str):
                Node name.

        Returns:
            List[dict]: list of all builds for specified node.

        Example:

        .. code-block:: python

            response = [{
                'job_name': 'test',
                'number': 1,
                'url': 'http://localhost:8080/job/test/1/'
            }]
        """
        def callback(response) -> List[dict]:
            return _parse_rss(response.body)

        name = self._normalize_name(name)

        return self.jenkins._request(
            'GET',
            f'/computer/{name}/rssAll',
            _callback=callback
        )

    def get_info(self, name: str) -> dict:
        """
        Get node detailed information.

        Args:
            name (str):
                Node name.

        Returns:
            dict: detailed node information.
        """
        def callback1(_):
            return self.jenkins._request('GET', f'/computer/{name}/api/json')

        def callback2(response: Any):
            if isinstance(response, JenkinsError):
                return response

            response['_disconnected'] = (
                response['offline'] is True and
                response['temporarilyOffline'] is False
            )

            return response

        name = self._normalize_name(name)
        return self.jenkins._chain([callback1, callback2])

    def get_config(self, name: str) -> str:
        """
        Return node config in XML format.

        Args:
            name (str):
                Node name.

        Returns:
            str: node config.
        """
        name = self._normalize_name(name)

        return self.jenkins._request(
            'GET',
            f'/computer/{name}/config.xml',
            _callback=self.jenkins._return_body,
        )

    def is_exists(self, name: str) -> bool:
        """
        Check is node exist.

        Args:
            name (str):
                Node name.

        Returns:
            bool: node existing.
        """
        if name == '':
            return False

        def callback1(_) -> Any:
            return partial(self.get_info, name)

        def callback2(response: Any) -> bool:
            if isinstance(response, JenkinsNotFoundError):
                return False

            return True

        return self.jenkins._chain([callback1, callback2])

    def create(self, name: str, config: dict) -> None:
        """
        Create new node.

        Args:
            name (str):
                Node name.

            config (dict):
                Config for new node, see ujenkins.helpers.construct_node_config

        Returns:
            None

        Raises:
            JenkinsError: in case node already exists.
        """
        def callback1(_) -> Any:
            return partial(self.get)

        def callback2(response: Any) -> bool:
            # if not check, then we get 400 error with unclear stacktrace
            if name in response:
                raise JenkinsError(f'Node `{name}` is already exists')

            if 'type' not in config:
                config['type'] = 'hudson.slaves.DumbSlave'

            config['name'] = name

            params = {
                'name': name,
                'type': config['type'],
                'json': json.dumps(config)
            }

            return self.jenkins._request(
                'POST',
                '/computer/doCreateItem',
                params=params,
            )

        return self.jenkins._chain([callback1, callback2])

    def delete(self, name: str) -> None:
        """
        Delete node.

        Args:
            name (str):
                Node name.

        Returns:
            None
        """
        name = self._normalize_name(name)

        return self.jenkins._request(
            'POST',
            f'/computer/{name}/doDelete'
        )

    def reconfigure(self, name: str, config: str) -> None:
        """
        Reconfigure node.

        Args:
            name (str):
                Node name.

            config (str):
                New XML config for node.

        Returns:
            None
        """
        name = self._normalize_name(name)

        if name == '(master)':
            raise JenkinsError('Cannot reconfigure master node')

        return self.jenkins._request(
            'POST',
            f'/computer/{name}/config.xml',
            data=config,
            headers={'Content-Type': 'text/xml'},
        )

    def enable(self, name: str) -> None:
        """
        Enable node if it disabled.

        Args:
            name (str):
                Node name.

        Returns:
            None
        """
        name = self._normalize_name(name)

        def callback1(_) -> Any:
            return partial(self.get_info, name)

        def callback2(response: dict) -> None:
            # skip if already enabled
            if response['temporarilyOffline'] is False:
                return None

            return self.jenkins._request('POST', f'/computer/{name}/toggleOffline')

        return self.jenkins._chain([callback1, callback2])

    def disable(self, name: str, message: str = '') -> None:
        """
        Disable node if it enabled.

        Args:
            name (str):
                Node name.

            message (Optional[str]):
                Reason message.

        Returns:
            None
        """
        name = self._normalize_name(name)

        def callback1(_) -> Any:
            return partial(self.get_info, name)

        def callback2(response: dict) -> None:
            # skip if already disabled
            if response['temporarilyOffline'] is True:
                return None

            return self.jenkins._request(
                'POST',
                f'/computer/{name}/toggleOffline',
                params={'offlineMessage': message},
            )

        return self.jenkins._chain([callback1, callback2])

    def update_offline_reason(self, name: str, message: str) -> None:
        """
        Update reason message of disabled node.

        Args:
            name (str):
                Node name.

            message (str):
                Reason message.

        Returns:
            None
        """
        name = self._normalize_name(name)

        return self.jenkins._request(
            'POST',
            f'/computer/{name}/changeOfflineCause',
            params={'offlineMessage': message}
        )

    def launch_agent(self, name: str) -> None:
        """
        Launch agent on node, for example in case when disconnected.

        State of connection can be determinated by `get_info(...)` method,
        which contains custom property defined by packages: `_disconnected`.

        Args:
            name (str):
                Node name.

        Returns:
            None
        """
        name = self._normalize_name(name)

        return self.jenkins._request(
            'POST',
            f'/computer/{name}/launchSlaveAgent',
        )
