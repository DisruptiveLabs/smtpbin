from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class APIIndexHandler(Handler):
    def do_GET(self, req):
        return jsonify({
            'status': 'online'
        })
