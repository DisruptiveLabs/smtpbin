from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.send_file import send_file, render_template


class IndexHandler(Handler):
    def do_GET(self, request):
        return render_template('index.html',
                               websocketport=self.client.database.websocketserver.port)
