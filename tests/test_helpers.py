import pytest

from ujenkins.exceptions import JenkinsError
from ujenkins.helpers import parse_build_url


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
