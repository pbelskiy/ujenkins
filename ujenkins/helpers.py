import re

from typing import List, Optional, Tuple
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring

from ujenkins.exceptions import JenkinsError

JOB_BUILD_URL_RE = re.compile(
    r'/job/(?P<job_name>.+)/(?P<build_number>\d+)'
)


def _construct_commands_block(parent, commands: List[str]) -> None:
    SubElement(parent, 'command').text = '\n'.join(commands)


def _construct_parameters_block(parent, parameters: List[dict]) -> None:
    props = SubElement(parent, 'hudson.model.ParametersDefinitionProperty')
    props = SubElement(props, 'parameterDefinitions')

    for parameter in parameters:
        new_p = SubElement(props, 'hudson.model.StringParameterDefinition')

        SubElement(new_p, 'name').text = parameter['name']
        SubElement(new_p, 'description').text = parameter.get('description')
        SubElement(new_p, 'defaultValue').text = parameter.get('default')


def construct_job_config(*,
                         description: Optional[str] = None,
                         parameters: Optional[List[dict]] = None,
                         commands: Optional[List[str]] = None
                         ) -> str:
    """
    Constructs an XML for job creating depends on arguments.

    Example:

    .. code-block:: python

        parameters = [
            dict(name='param1'),
            dict(name='param2', description='helpfull information'),
            dict(name='param3', default='default command value'),
        ]

        commands = [
            'echo 1',
            'sleep 5',
        ]

    Args:
        description (Optional[str]):
            Job description.

        parameters (Optional[List[dict]]):

            Parameters for job, note that name is mandatory field.

        commands (Optional[List[str]]):
            List of commands which will be joined as one string by note that
            entire command block will run in one shell instance.

    Returns:
        str: Prettified XML ready to submit on Jenkins.
    """
    root = Element('project')

    SubElement(root, 'actions')
    SubElement(root, 'description').text = description
    SubElement(root, 'keepDependencies').text = 'false'

    properties = SubElement(root, 'properties')

    if parameters:
        _construct_parameters_block(properties, parameters)

    SubElement(root, 'scm', attrib={'class': 'hudson.scm.NullSCM'})
    SubElement(root, 'canRoam').text = 'true'
    SubElement(root, 'disabled').text = 'false'
    SubElement(root, 'blockBuildWhenDownstreamBuilding').text = 'false'
    SubElement(root, 'blockBuildWhenUpstreamBuilding').text = 'false'
    SubElement(root, 'triggers')
    SubElement(root, 'concurrentBuild').text = 'false'

    builders = SubElement(root, 'builders')
    shell = SubElement(builders, 'hudson.tasks.Shell')

    if commands:
        _construct_commands_block(shell, commands)
    else:
        # probably it's need to at least add empty block
        SubElement(shell, 'command')

    SubElement(root, 'publishers')
    SubElement(root, 'buildWrappers')

    rough_string = tostring(root, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent='  ')


def construct_node_config(*,
                          name: str,
                          remote_fs: str = '/tmp',
                          executors: int = 2
                          ) -> dict:
    """
    Construct node config.

    Args:
        name (str):
            Node name.

        remote_fs (str):
            Remote node root directory.

        executors (int):
            Number of node executors

    Returns:
        dict: return ready to use dict with nodes.create()
    """
    return {
        'name': name,
        'nodeDescription': '',
        'numExecutors': executors,
        'remoteFS': remote_fs,
        'labelString': '',
        'launcher': {
            'stapler-class': 'hudson.slaves.JNLPLauncher',
        },
        'retentionStrategy': {
            'stapler-class': 'hudson.slaves.RetentionStrategy$Always',
        },
        'nodeProperties': {
            'stapler-class-bag': 'true'
        }
    }


def parse_build_url(build_url: str) -> Tuple[str, int]:
    """
    Extract job name and build number from build url.

    Args:
        build_url (str):
            URL to build.

    Returns:
        Tuple[str, int]: job name and build number.
    """
    match = JOB_BUILD_URL_RE.search(build_url)
    if not match:
        raise JenkinsError(f'Invalid URL: {build_url}')

    name = '/'.join(filter(
        lambda x: x != 'job',
        match.group('job_name').split('/')
    ))

    return name, int(match.group('build_number'))


def normalize_url(path: str) -> str:
    """
    Amend job path in case it starts from two forward slashes.

    Args:
        path (str):
            Path to amend, e.g. //job/some_job/enable

    Returns:
        str: amended path, e.g.: /job/some_job/enable
    """
    if path.startswith('//'):
        return path[1:]
    return path
