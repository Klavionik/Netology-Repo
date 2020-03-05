class APIError(Exception):
    """General VK API Error"""

    def __init__(self, message, **kwargs):
        error = kwargs['error']
        self.code = error.get('error_code')
        self.msg = error.get('error_msg')
        self.request = error.get('request_params')
        super().__init__(message)


class InternalServerError(APIError):
    """Raised if VK API returned error 500 Internal Server Error"""
    pass


class TooManyRequestsPerSecond(APIError):
    """Raised if the application makes more than 3 requests per second"""
    pass
