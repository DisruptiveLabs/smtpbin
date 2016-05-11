import http.client


class HTTPError(Exception):
    status = None
    message = None

    def __init__(self, status, message=None):
        self.status = status
        self.message = message or http.client.responses[status]
