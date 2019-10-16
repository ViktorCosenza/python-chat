from imports import json

SUCCESS = 200
AUTH_SUCCESS=201

ERROR = 400
AUTH_ERROR = 401

SUCCESS_CODES = [SUCCESS]
ERROR_CODES = [ERROR, AUTH_ERROR]


def parse_json(payload):
    parsed = json.loads(payload)
    return parsed


class ServerProtocol:
    @staticmethod
    def new_payload(payload, message, status):
        return json.dumps(
            {"status": status, "message": message, "payload": payload}
        ).encode("utf-8")

    @staticmethod
    def success(payload=None, message="success", status=SUCCESS):
        return ServerProtocol.new_payload(payload, message, status)
    
    @staticmethod
    def auth_success(payload=None, message="auth success", status=AUTH_SUCCESS):
        return ServerProtocol.new_payload(payload, message, status)

    @staticmethod
    def error(payload=None, message="server error", status=ERROR):
        return ServerProtocol.new_payload(payload, message, status)

    @staticmethod
    def auth_error(payload=None, message="auth error", status=AUTH_ERROR):
        return ServerProtocol.new_payload(payload, message, status)


class ClientProtocol:
    @staticmethod
    def new_payload(command, payload):
        payload = {"command": command, "payload": payload}
        return json.dumps(payload).encode("utf-8")
