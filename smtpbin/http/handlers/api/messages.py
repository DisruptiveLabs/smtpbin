from smtpbin.http.exceptions import HTTPError
from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class APIMessagesHandler(Handler):
    def do_GET(self, req, inbox_name):
        inbox = self.database.get_inbox_by_name(inbox_name)
        if not inbox:
            raise HTTPError(404, 'inbox not found')

        messages = self.database.get_messages(inbox['id'])
        return jsonify(messages)
