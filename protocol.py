from imports import json

SUCCESS = 200
ERROR = 400


class ServerProtocol:
    @staticmethod
    def new_payload(payload, message, status):
        return json.dumps(
            {"status": status, "message": message, "payload": payload}
        ).encode("utf-8")

    @staticmethod
    def success(payload=None, message="success", status=SUCCESS):
        return new_payload(payload, message, status)

    @staticmethod
    def error(payload=None, message="server error", status=ERROR):
        return new_payload(payload, message, status)


class ClientProtocol:
    @staticmethod
    def new_payload(command, payload):
        payload = {"command": command, "payload": payload}
        return json.dumps(payload)
