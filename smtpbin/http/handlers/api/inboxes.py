from smtpbin.http.handlers.handler import Handler
from smtpbin.http.utils.jsonify import jsonify


class APIInboxesHandler(Handler):
    def do_GET(self, req):
        """Get a list of all inboxes with counts"""
        return jsonify(self.database.get_inboxes())

    def do_POST(self, req):
        """Create a new inbox"""
        return req.path