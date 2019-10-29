import threading
import time
import io
import sys
import random
from imports import socket, select, constants
from .command_utils import parse_auth, parse_command, AUTH_COMMANDS, MSG_COMMANDS
from .screen_helpers import *
import protocol


from protocol import parse_json


def start_client():
    screen = setup_screen()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((constants.IP, constants.PORT))
    except ConnectionRefusedError:
        print(
            "Could not connect :(."
            "\nFirst start Server with 'python main.py --server'"
        )
        return

    raw_msg = client_socket.recv(4096)
    payload = parse_json(raw_msg)
    if payload["status"] == 200:
        screen["out"]["printer"]("Connected to server!")
    username = authenticate(client_socket, screen)
    main_loop(client_socket, username, screen)


def authenticate(sock, screen):
    screen["out"]["printer"]("Possible commands: /login or /signup, term")
    auth_status = False

    while not auth_status:
        raw_command = gather_input(screen["in"])
        refresh_all(screen)
        try:
            command = parse_auth(raw_command)
        except AssertionError as e:
            screen["out"]["printer"](e)
            continue

        sock.send(protocol.encode(command))
        raw_msg = sock.recv(constants.MAX_MSG_LEN)
        response = parse_json(raw_msg)

        if response["status"] != protocol.AUTH_SUCCESS:
            error_code = response["status"]
            error_msg = response["message"]
            screen["out"]["printer"](f"Error {error_code}: {error_msg}")
            continue

        username = response["payload"]["username"]
        if command["command"] == "/signup":
            screen["out"]["printer"](
                f"Successfully created user {username}"
                "Login with /login <username> <password>",
                sep="\n",
            )

        elif command["command"] == "/login":
            screen["out"]["printer"](f"Welcome {username}!")
            return username


def listen_server(sock, printer):
    while True:
        message = sock.recv(constants.MAX_MSG_LEN)
        printer(message["payload"])


def wait_user_input(sock, screen, out_printer):
    while True:
        raw_command = gather_input(screen)
        command = parse_command(raw_command)
        out_printer(raw_command)


def main_loop(sock, username, screen):
    global has_quited
    has_quited = False
    listen_thread = threading.Thread(
        target=listen_server, args=(sock, screen["out"]["printer"])
    )
    input_thread = threading.Thread(
        target=wait_user_input, args=(sock, screen["in"], screen["out"]["printer"])
    )

    listen_thread.start()
    input_thread.start()
