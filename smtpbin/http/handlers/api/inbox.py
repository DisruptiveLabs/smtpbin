from smtpbin.http.exceptions import HTTPError
from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class APIInboxHandler(Handler):
    def do_GET(self, req, inbox_name):
        """Get the details of specific inbox"""
        inbox = self.database.get_inbox_by_name(inbox_name)
        if not inbox:
            raise HTTPError(404)

        return jsonify(inbox)

    def do_PUT(self, req):
        """Change the name or apikey of an inbox"""
