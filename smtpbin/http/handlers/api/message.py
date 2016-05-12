from smtpbin.http.exceptions import HTTPError
from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class APIMessageHandler(Handler):
    def do_GET(self, req, inbox_name, message_id):
        inbox = self.database.get_inbox_by_name(inbox_name)
        if not inbox:
            raise HTTPError(404, "inbox not found")

        message = self.database.get_message(inbox['id'], message_id)
        if not message:
            raise HTTPError(404, 'message not found')

        return jsonify(message)
