from smtpbin.http.handlers.handler import Handler


class APIInboxHandler(Handler):
    def do_GET(self, req):
        """Get the details of specific inbox"""

    def do_PUT(self, req):
        """Change the name or apikey of an inbox"""
