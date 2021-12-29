import re

from typing import List, Tuple
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
                         description: str = None,
                         parameters: List[dict] = None,
                         commands: List[str] = None
                         ) -> str:
    """
    Constructs an XML for job creating depends on arguments.

    Args:
        - description: Job description
        - parameters: Parameters for job, note that name is mandatory field.

            Example:

            .. code-block:: python

                [
                    dict(name='param1'),
                    dict(name='param2', description='helpfull information'),
                    dict(name='param3', default='default command value'),
                ]

        - commands: List of commands which will be joined as one string by note
                    that entire command block will run in one shell instance.


            Example:

            .. code-block:: python

                [
                    'echo 1',
                    'sleep 5',
                ]

    Returns:
        - str: Prettified XML ready to submit on Jenkins
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
        - name: Node name
        - remote_fs: Remote node root directory
        - executors: Number of node executors

    Returns:
        - dict: return ready to use dict with nodes.create()
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
    Extract job name and build number from build url
    """
    match = JOB_BUILD_URL_RE.search(build_url)
    if not match:
        raise JenkinsError('Invalid URL: {}'.format(build_url))

    name = '/'.join(filter(
        lambda x: x != 'job',
        match.group('job_name').split('/')
    ))

    return name, int(match.group('build_number'))
