import email
import smtpd

from smtpbin.backend import DataBase
from smtpbin.smtp.channel import SMTPBinChannel


class SMTPBinServer(smtpd.SMTPServer):
    channel_class = SMTPBinChannel

    def __init__(self, addr, database):
        super().__init__(addr, None)
        self.database = database
        self.log_to_stdout = True

        print("Listening for SMTP on {0}:{1}".format(*addr))

    def process_message(self, inbox, peer, mailfrom, rcpttos, data, **kwargs):
        message = email.message_from_string(data)

        if self.log_to_stdout:
            print("-" * 80)
            print("From: {}".format(mailfrom))
            print("To: {}".format(rcpttos))
            print("Subject: {}".format(message.get('Subject', None)))
            print(data)

        for recipient in rcpttos:
            self.database.add_message(inbox, mailfrom, recipient, message['Subject'], data)
