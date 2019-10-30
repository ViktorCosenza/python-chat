import json

SUCCESS = 200
AUTH_SUCCESS = 201
SEND_MESSAGE = 303


ERROR = 400
AUTH_ERROR = 401

SUCCESS_CODES = [SUCCESS, AUTH_SUCCESS]
ERROR_CODES = [ERROR, AUTH_ERROR]


def parse_json(payload):
    return json.loads(payload)


def encode(data):
    return json.dumps(data).encode("utf-8")


class ServerProtocol:
    @staticmethod
    def new_payload(payload, message, status):
        return {"payload": {**payload, "by": "server"}, "message": message, "status": status}

    @staticmethod
    def success(payload={}, message="success", status=SUCCESS):
        return ServerProtocol.new_payload(payload, message, status)

    @staticmethod
    def message(payload={}, message="you got mail", status=SEND_MESSAGE):
        return ServerProtocol.new_payload(payload, message, status)

    @staticmethod
    def auth_success(payload={}, message="auth success", status=AUTH_SUCCESS):
        return ServerProtocol.new_payload(payload, message, status)

    @staticmethod
    def error(payload={}, message="server error", status=ERROR):
        return ServerProtocol.new_payload(payload, message, status)

    @staticmethod
    def auth_error(payload={}, message="auth error", status=AUTH_ERROR):
        return ServerProtocol.new_payload(payload, message, status)


class ClientProtocol:
    @staticmethod
    def new_payload(command, payload):
        return {"command": command, "payload": payload}
