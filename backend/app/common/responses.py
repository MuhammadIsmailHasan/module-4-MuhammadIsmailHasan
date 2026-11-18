from flask import jsonify


def ok(data=None, status=200):
    """Success envelope: { "data": <payload> }."""
    return jsonify({"data": data}), status
