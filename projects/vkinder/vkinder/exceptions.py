class APIError(Exception):

    def __init__(self, response):
        if "error" in response:
            self.message = response['error'].get('error_msg')
            self.code = response['error'].get('error_code')
        if "execute_errors" in response:
            self.message = response.get("execute_errors")
            self.body = response
        super().__init__(response)
