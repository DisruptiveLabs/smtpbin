from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class APIIndexHandler(Handler):
    def do_GET(self, req):
        return jsonify({
            '_links': {
                '/api/inbox': 'List your inboxes'
            }
        })
