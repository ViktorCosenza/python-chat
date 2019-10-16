from imports import socket, select, constants
from .command_utils import parse_auth


def start_client():
    print("Starting client...")
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((constants.IP, constants.PORT))

    msg = client_socket.recv(4096)
    authenticate(client_socket)


def authenticate(sock):
    print("Use /login or /register to procede")

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
            print(command)

        except AssertionError as e:
            print(e)
            continue


def main_loop(sock):
    pass
