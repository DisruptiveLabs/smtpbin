import json
import mimetypes
import os
import string

from smtpbin.http.exceptions import HTTPError

SEND_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
STATIC_PATH = os.path.join(os.path.split(SEND_FILE_PATH)[0], "static")
STATIC_FILE_EXTENSIONS = [
    # Media
    'bmp', 'tif', 'pict', 'tiff', 'jpg', 'jpeg', 'gif', 'svg', 'svgz', 'ico', 'png', 'webp',

    # Documents
    'pdf', 'swf', 'csv',

    # Fonts
    'ttf', 'woff2', 'eot', 'woff',

    # CSS/JS
    'css', 'js', 'jsx',
]

mime = mimetypes.MimeTypes()

with open(os.path.join(SEND_FILE_PATH, 'mime.json'), 'r') as f:
    mime_json_data = json.load(f)
    for type, data in mime_json_data.items():
        if 'extensions' in data:
            for extension in data['extensions']:
                mime.add_type(type, extension)


def get_file_contents(name, mode='rb'):
    if name.startswith("/"):
        name = name[1:]

    filename = os.path.join(STATIC_PATH, name)

    with open(filename, mode) as f:
        return f.read()


def send_file(name):
    mimetype = mime.guess_type(name)[0] or 'application/octet-stream'
    try:
        body = get_file_contents(name)
        return 200, body, {'Content-Length': len(body), 'Content-Type': mimetype}
    except IOError:
        raise HTTPError(404, name)


def render_template(name, **kwargs):
    mimetype = mime.guess_type(name)[0] or 'application/octet-stream'
    try:
        template = string.Template(get_file_contents(name, 'r'))
        body = template.substitute(**kwargs).encode()
        return 200, body, {'Content-Length': len(body), 'Content-Type': mimetype}
    except IOError:
        raise HTTPError(404, name)
