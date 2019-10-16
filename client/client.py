from imports import socket, select, constants
from .command_utils import parse_auth
import protocol
from protocol import parse_json


def start_client():
    print("Starting client...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((constants.IP, constants.PORT))

    raw_msg = client_socket.recv(4096)
    payload = parse_json(raw_msg)
    if payload["status"] == 200:
        print("Connected to server!")
    authenticate(client_socket)


def authenticate(sock):
    print("Possible commands: /login or /signup")

    auth_status = False
    while not auth_status:
        raw_command = input(">")
        try:
            command = parse_auth(
                raw_command,
                expect=[
                    r"(/login) ([a-zA-Z]+) ([a-zA-Z]+)",
                    r"(/signup) ([a-zA-Z]+) ([a-zA-Z]+)",
                ],
            )

            sock.send(command)
            raw_msg = sock.recv(constants.MAX_MSG_LEN)
            payload = parse_json(raw_msg)
            if payload["status"] in protocol.ERROR_CODES:
                print(payload)
        except AssertionError as e:
            print(e)
            continue


def main_loop(sock):
    pass
