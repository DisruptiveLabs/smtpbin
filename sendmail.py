import argparse
import email.mime.text
import os
import smtplib

MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '25000'))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)

parser = argparse.ArgumentParser()
parser.add_argument('from_addr')
parser.add_argument('to_addr')
parser.add_argument('subject')
parser.add_argument('message')

if __name__ == '__main__':
    args = parser.parse_args()

    mime = email.mime.text.MIMEText(args.message, 'plain')
    mime['Subject'] = args.subject

    smtp = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)

    if MAIL_USERNAME and MAIL_PASSWORD:
        smtp.login(MAIL_USERNAME, MAIL_PASSWORD)

    smtp.sendmail(args.from_addr, [args.to_addr], mime.as_string())
