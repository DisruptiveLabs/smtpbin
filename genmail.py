import argparse
import email.mime.text
import os
import smtplib
import random
from faker import Faker
MAIL_SERVER = os.environ.get('MAIL_SERVER', 'localhost')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '25000'))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'frankcmng.ngrok.io')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'thisisatest')
MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', False)
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', False)

parser = argparse.ArgumentParser()
parser.add_argument('count', type=int)

if __name__ == '__main__':
    args = parser.parse_args()

    smtp = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)

    if MAIL_USERNAME and MAIL_PASSWORD:
        smtp.login(MAIL_USERNAME, MAIL_PASSWORD)
    i = args.count

    faker = Faker()
    while i:
        mime = email.mime.text.MIMEText('\n'.join(faker.sentences(random.randint(1,15))), 'plain')
        mime['Subject'] = ' '.join(faker.words(random.randint(5,15)))
        smtp.sendmail(faker.email(), [faker.email()], mime.as_string())
        i-=1
