class JenkinsError(Exception):
    """
    Core library exception
    """
    ...


class JenkinsNotFoundError(JenkinsError):
    """
    Raises when request return HTTP code 404 (not found)
    """
    ...
