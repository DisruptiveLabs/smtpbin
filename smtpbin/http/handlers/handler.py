import http.client


class Handler(object):
    def __init__(self, client):
        self.client = client
        self.database = client.database

    def make_http_response(self, status):
        return 'HTTP/1.1 {} {}\n'.format(status, http.client.responses[status])

    def format_header(self, name, value):
        return '{!s}: {!s}\n'.format(name, value)

    def dispatch(self, req):
        # Get the method for the request, or raise error
        handler = getattr(self, "do_{}".format(req.command), None)
        response = handler(req)
        status, headers = 200, {}

        if isinstance(response, tuple):
            if len(response) == 3:
                status, response, headers = response
            elif len(response) == 2:
                status, response = response
            else:
                [response] = response

        self.send(self.make_http_response(status))
        for name, value in headers.items():
            self.send(self.format_header(name, value))
        self.send("\n")
        self.send(response)

    def send(self, data):
        if isinstance(data, str):
            data = str.encode(data)
        self.client.send(data)
