from smtpbin.http.exceptions import HTTPError
from smtpbin.http.handlers.handler import Handler


class ErrorHandler(Handler):
    def dispatch(self, req, error):
        if isinstance(error, HTTPError):
            status = error.status
            message = error.message
        else:
            status = 500
            message = repr(error)

        self.send(self.make_http_response(status))
        self.send("There was a server error: \n\n{} {}".format(status, message))
