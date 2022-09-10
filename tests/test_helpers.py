import pytest

from ujenkins.exceptions import JenkinsError
from ujenkins.helpers import (
    construct_job_config,
    construct_node_config,
    parse_build_url,
)


def test_construct_job_config():
    config = construct_job_config(
        description='awesome',
        parameters=[dict(
            name='param2',
            description='helpfull information',
            default='default command value'
        )],
        commands=['echo 1', 'sleep 5'],
    )
    assert '<description>awesome</description>' in config
    assert 'param2' in config
    assert 'sleep 5' in config


def test_construct_node_config():
    config = construct_node_config(name='my_node')
    assert config['name'] == 'my_node'


def test_parse_build_urlt():
    name, number = parse_build_url(
        'http://localhost:8080/job/jobbb/1/console'
    )
    assert name == 'jobbb'
    assert number == 1

    name, number = parse_build_url(
        'http://localhost:8080/job/test_folder/job/test_job/567/console'
    )
    assert name == 'test_folder/test_job'
    assert number == 567

    with pytest.raises(JenkinsError):
        parse_build_url('xxx')
