import argparse
import asyncore
import os
import uuid

from smtpbin.backend import DataBase
from .http.server import HTTPServer
from .smtp.server import SMTPServer
from .websocket.server import WebSocketServer

LISTEN_ADDR = os.environ.get('LISTEN_ADDR', '0.0.0.0')
HTTP_PORT = int(os.environ.get('HTTP_PORT', '8000'))
WEBSOCKET_PORT = int(os.environ.get('WEBSOCKET_PORT', '8080'))
SMTP_PORT = int(os.environ.get('SMTP_PORT', '25000'))

map = {}


def run_servers(database, listen, http_port, smtp_port, websocket_port):
    map['http'] = HTTPServer((listen, http_port), database)
    map['smtp'] = SMTPServer((listen, smtp_port), database)
    map['websocket'] = WebSocketServer((listen, websocket_port), database)

    try:
        asyncore.loop(timeout=5)
    except KeyboardInterrupt:
        pass


def print_connection_information(name, apikey):
    print("""Connection information as follows:

        SMTP Address: {LISTEN_ADDR}:{SMTP_PORT}
        SMTP Username: {name}
        SMTP Password: {apikey}
        """.format(LISTEN_ADDR=LISTEN_ADDR, SMTP_PORT=SMTP_PORT, name=name, apikey=apikey))


def create_inbox(database, name):
    apikey = uuid.uuid4().hex
    database.create_inbox(name, apikey)
    database.commit()
    print_connection_information(name, apikey)


def reset_apikey(database, name):
    apikey = uuid.uuid4().hex
    if not database.set_inbox_apikey(name, apikey):
        raise ValueError("No inbox found named {}".format(name))
    database.commit()
    print_connection_information(name, apikey)


parser = argparse.ArgumentParser()
parser.add_argument("--database", "-d", help="Path to store the sqlite database", default="smtpbin.db")

subparsers = parser.add_subparsers(help="Available Commands", dest="action")

run_parser = subparsers.add_parser('run', help='Run the server')
run_parser.add_argument("--listen", default=LISTEN_ADDR, type=str, help="Address to listen on")
run_parser.add_argument("--http-port", default=HTTP_PORT, type=int, help="Port for the HTTP Server")
run_parser.add_argument("--websocket-port", default=WEBSOCKET_PORT, type=int, help="Port for the Websocket Server")
run_parser.add_argument("--smtp-port", default=SMTP_PORT, type=int, help="Port for the SMTP Server")

create_inbox_parser = subparsers.add_parser('create_inbox', help="Create a new inbox")
create_inbox_parser.add_argument("name", help="Inbox name, also the username for SMTP")

reset_apikey_parser = subparsers.add_parser('reset_apikey', help="Reset an inbox's apikey")
reset_apikey_parser.add_argument("name", help="Inbox name, also the username for SMTP")


def main():
    args = parser.parse_args()

    if not args.action:
        return parser.print_help()

    database = DataBase(args.database)

    if args.action == 'run':
        return run_servers(database, args.listen, args.http_port, args.smtp_port, args.websocket_port)
    elif args.action == 'create_inbox':
        return create_inbox(database, args.name)
    elif args.action == 'reset_apikey':
        return reset_apikey(database, args.name)
    else:
        return parser.print_help()


if __name__ == '__main__':
    main()
