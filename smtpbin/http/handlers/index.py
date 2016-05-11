from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.send_file import send_file


class IndexHandler(Handler):
    def do_GET(self, request):
        return send_file('index.html')
