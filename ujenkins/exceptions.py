class JenkinsError(Exception):
    """
    Core library exception
    """
    def __init__(self, message=None, status=None):
        super().__init__(message)
        self.message = message
        self.status = status


class JenkinsNotFoundError(JenkinsError):
    """
    Raises when request return HTTP code 404 (not found)
    """
    ...
