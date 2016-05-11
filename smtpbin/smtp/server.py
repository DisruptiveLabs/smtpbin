import email
import smtpd

from smtpbin.backend import DataBase


class SMTPBinServer(smtpd.SMTPServer):
    def __init__(self, addr):
        super().__init__(addr, None)
        self.log_to_stdout = True
        self.database = DataBase()
        print("Listening for SMTP on {0}:{1}".format(*addr))

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        message = email.message_from_string(data)

        if self.log_to_stdout:
            print("-" * 80)
            print("From: {}".format(mailfrom))
            print("To: {}".format(rcpttos))
            print("Subject: {}".format(message.get('Subject', None)))
            print(data)

        for recipient in rcpttos:
            self.database.add_message(mailfrom, recipient, message['Subject'], data)
