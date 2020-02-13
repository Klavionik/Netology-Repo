class APIError(Exception):

    def __init__(self, response):
        if "error" in response:
            self.body = response["error"]
            self.message = response['error']['error_msg']
        if "execute_errors" in response:
            self.message = response["execute_errors"]
            self.body = response
        super().__init__(response)
