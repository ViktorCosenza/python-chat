from imports import json
SUCCESS = 200
ERROR = 400

def new_payload(payload, message, status):
    return json.dumps({
        "status": status,
        "message": message,
        "payload": payload
    }).encode('utf-8')

def success(payload=None, message="success", status=SUCCESS):
    return new_payload(payload, message, status)

def error(payload=None, message="server error", status=ERROR):
    return new_payload(payload, message, status)