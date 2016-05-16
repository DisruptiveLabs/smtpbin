import email
import smtpd

from smtpbin.smtp.channel import SMTPBinChannel


class SMTPServer(smtpd.SMTPServer):
    channel_class = SMTPBinChannel

    def __init__(self, addr, database):
        super(SMTPServer, self).__init__(addr, None)

        self.database = database
        database.smtpserver = self
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
            message_id = self.database.add_message(inbox, mailfrom, recipient, message['Subject'], data)
