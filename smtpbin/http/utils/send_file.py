import os

from smtpbin.http.exceptions import HTTPError

STATIC_PATH = os.path.join(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0], "static")


def send_file(name):
    if name.startswith("/"):
        name = name[1:]

    filename = os.path.join(STATIC_PATH, name)
    try:
        with open(filename, 'rb') as f:
            return 200, f.read(), {'Content-Length': os.stat(filename).st_size}
    except IOError:
        raise HTTPError(404, name)
