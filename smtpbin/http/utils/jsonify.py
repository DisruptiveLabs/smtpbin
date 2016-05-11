import json


def jsonify(data, status=200):
    return status, json.dumps(data), {'Content-Type': 'application/json'}
