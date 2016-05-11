from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class MessagesHandler(Handler):
    def do_GET(self, req):
        message_count = self.db.count_messages()
        return jsonify({'messages': message_count})
