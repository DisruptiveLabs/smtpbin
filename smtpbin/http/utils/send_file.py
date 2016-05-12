import json
import mimetypes
import os

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


def send_file(name):
    if name.startswith("/"):
        name = name[1:]

    filename = os.path.join(STATIC_PATH, name)
    mimetype, encoding = mime.guess_type(filename)

    try:
        with open(filename, 'rb') as f:
            return 200, f.read(), {'Content-Length': os.stat(filename).st_size,
                                   'Content-Type': mimetype or 'application/octet-stream'}
    except IOError:
        raise HTTPError(404, name)
