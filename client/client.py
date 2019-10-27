import threading
import time
import io
import sys
from imports import socket, select, constants
from .command_utils import parse_auth
import protocol
from protocol import parse_json


def start_client():
    print("Starting client...")
    print(threading.current_thread())
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
        print("Connected to server!")
    username = authenticate(client_socket)
    main_loop(client_socket, username)


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
        except AssertionError as e:
            print(e)
            continue

        sock.send(protocol.encode(command))
        raw_msg = sock.recv(constants.MAX_MSG_LEN)
        response = parse_json(raw_msg)

        if response["status"] != protocol.AUTH_SUCCESS:
            error_code = response["status"]
            error_msg = response["message"]
            print(f"Error {error_code}: {error_msg}")
            continue

        username = response["payload"]["username"]
        if command["command"] == "/signup":
            print(
                f"Successfully created user {username}"
                "Login with /login <username> <password>",
                sep="\n",
            )

        elif command["command"] == "/login":
            print(f"Welcome {username}!")
            return username


def safe_print(string, cv, out=sys.stdout):
    cv.acquire()
    where = out.tell()
    print(string, file=out)
    out.seek(where)
    cv.notify()
    cv.release()


def listen_server(sock, cv, out):
    while True:
        safe_print("a\n", cv, out)
        time.sleep(1)


def wait_user_input(sock):
    while True:
        raw_command = input("\r> ")
        print(f"You typed {raw_command}")


def maybe_print_line(out):
    where = out.tell()
    line = out.readline()
    if not line:
        out.seek(where)
    else:
        print(line)

def main_loop(sock, username="guest"):
    global has_quited
    has_quited = False
    chat_output = io.StringIO()
    has_new_message_cv = threading.Condition()

    listen_thread = threading.Thread(
        target=listen_server, args=(sock, has_new_message_cv, chat_output)
    )
    input_thread = threading.Thread(target=wait_user_input, args=(sock,))

    listen_thread.start()
    input_thread.start()

    while True:
        has_new_message_cv.acquire()
        has_new_message_cv.wait()
        msg = maybe_print_line(chat_output)
