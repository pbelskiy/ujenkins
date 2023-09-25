import json

# Sample usage
builds_data = [
    {
        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun',
        'actions': [
            {'_class': 'hudson.model.CauseAction'},
            {'_class': 'jenkins.metrics.impl.TimeInQueueAction'},
            {'_class': 'org.jenkinsci.plugins.workflow.libs.LibrariesAction'},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.RunDisplayAction'},
            {},
            {'_class': 'org.jenkinsci.plugins.workflow.job.views.FlowGraphAction'},
            {},
            {},
            {},
            {}
        ],
        'artifacts': [],
        'building': False,
        'description': None,
        'displayName': '#5',
        'duration': 110338,
        'estimatedDuration': 55,
        'executor': None,
        'fingerprint': [],
        'fullDisplayName': '💻 dev » testgene #5',
        'id': '5',
        'keepLog': False,
        'number': 5,
        'queueId': 12216,
        'result': 'SUCCESS',
        'timestamp': 1695091214082,
        'url': 'https://localhost:8080/job/dev/job/testgene/5/',
        'changeSets': [],
        'culprits': [],
        'inProgress': False,
        'nextBuild': {},
        'previousBuild': {}
    },
    {
        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun',
        'actions': [
            {'_class': 'hudson.model.CauseAction'},
            {'_class': 'jenkins.metrics.impl.TimeInQueueAction'},
            {'_class': 'org.jenkinsci.plugins.workflow.libs.LibrariesAction'},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.RunDisplayAction'},
            {},
            {'_class': 'org.jenkinsci.plugins.workflow.job.views.FlowGraphAction'},
            {},
            {},
            {},
            {}
        ],
        'artifacts': [],
        'building': False,
        'description': None,
        'displayName': '#4',
        'duration': 110411,
        'estimatedDuration': 55,
        'executor': None,
        'fingerprint': [],
        'fullDisplayName': '💻 dev » testgene #4',
        'id': '4',
        'keepLog': False,
        'number': 4,
        'queueId': 12214,
        'result': 'SUCCESS',
        'timestamp': 1695090700131,
        'url': 'https://localhost:8080/job/dev/job/testgene/4/',
        'changeSets': [],
        'culprits': [],
        'inProgress': False,
        'nextBuild': {},
        'previousBuild': {}
    },
    {
        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun',
        'actions': [
            {'_class': 'hudson.model.CauseAction'},
            {'_class': 'jenkins.metrics.impl.TimeInQueueAction'},
            {'_class': 'org.jenkinsci.plugins.workflow.libs.LibrariesAction'},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.RunDisplayAction'},
            {},
            {'_class': 'org.jenkinsci.plugins.workflow.job.views.FlowGraphAction'},
            {},
            {},
            {},
            {}
        ],
        'artifacts': [],
        'building': False,
        'description': None,
        'displayName': '#3',
        'duration': 110375,
        'estimatedDuration': 55,
        'executor': None,
        'fingerprint': [],
        'fullDisplayName': '💻 dev » testgene #3',
        'id': '3',
        'keepLog': False,
        'number': 3,
        'queueId': 12212,
        'result': 'SUCCESS',
        'timestamp': 1695087505819,
        'url': 'https://localhost:8080/job/dev/job/testgene/3/',
        'changeSets': [],
        'culprits': [],
        'inProgress': False,
        'nextBuild': {},
        'previousBuild': {}
    },
    {
        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun',
        'actions': [
            {'_class': 'hudson.model.CauseAction'},
            {'_class': 'jenkins.metrics.impl.TimeInQueueAction'},
            {'_class': 'org.jenkinsci.plugins.workflow.libs.LibrariesAction'},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.RunDisplayAction'},
            {},
            {'_class': 'org.jenkinsci.plugins.workflow.job.views.FlowGraphAction'},
            {},
            {},
            {},
            {}
        ],
        'artifacts': [],
        'building': False,
        'description': None,
        'displayName': '#2',
        'duration': 110381,
        'estimatedDuration': 55,
        'executor': None,
        'fingerprint': [],
        'fullDisplayName': '💻 dev » testgene #2',
        'id': '2',
        'keepLog': False,
        'number': 2,
        'queueId': 12210,
        'result': 'SUCCESS',
        'timestamp': 1695087480148,
        'url': 'https://localhost:8080/job/dev/job/testgene/2/',
        'changeSets': [],
        'culprits': [],
        'inProgress': False,
        'nextBuild': {},
        'previousBuild': {}
    },
    {
        '_class': 'org.jenkinsci.plugins.workflow.job.WorkflowRun',
        'actions': [
            {'_class': 'hudson.model.CauseAction'},
            {'_class': 'jenkins.metrics.impl.TimeInQueueAction'},
            {'_class': 'org.jenkinsci.plugins.workflow.libs.LibrariesAction'},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {},
            {'_class': 'org.jenkinsci.plugins.displayurlapi.actions.RunDisplayAction'},
            {},
            {'_class': 'org.jenkinsci.plugins.workflow.job.views.FlowGraphAction'},
            {},
            {},
            {},
            {}
        ],
        'artifacts': [],
        'building': False,
        'description': None,
        'displayName': '#1',
        'duration': 110528,
        'estimatedDuration': 55,
        'executor': None,
        'fingerprint': [],
        'fullDisplayName': '💻 dev » testgene #1',
        'id': '1',
        'keepLog': False,
        'number': 1,
        'queueId': 12208,
        'result': 'SUCCESS',
        'timestamp': 1695087098240,
        'url': 'https://localhost:8080/job/dev/job/testgene/1/',
        'changeSets': [],
        'culprits': [],
        'inProgress': False,
        'nextBuild': {},
        'previousBuild': None
    }
]


def filter_builds_response(fields=None, start=None, end=None):
    """
    Dynamically filters the Jenkins data.

    Args:
    - data (list of dict):
        The list containing Jenkins build data.
    - fields (list of str, optional):
        The fields you want to retain. If None, or contains '*', all fields are retained


    Returns:
    - list of dict: Filtered Jenkins build data.
    """

    # Filter by range if start and end are provided
    data = builds_data
    data = data[start-1:end]

    # Filter by fields if provided and * is not in fields
    if fields and '*' not in fields:
        data = [{k: v for k, v in item.items() if k in fields or k == '_class'} for item in data]

    return json.dumps(
            {
                '_class': 'hudson.model.FreeStyleProject',
                'allBuilds': data
            }
        )
