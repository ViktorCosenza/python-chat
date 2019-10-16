from imports import socket, select, constants
from protocol import ServerProtocol, parse_json


def start_server(ip=constants.IP, port=constants.PORT):
    print("Starting server...")
    server = Server(ip, port)
    print(f"Server started! Listening at {constants.IP}:{constants.PORT}...")
    server.listen()


def new_user(sockt, username, password):
    return {"username": username, "password": password, "connection": sockt}


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        self.listening = [self.server_socket]
        self.registered_users = []
        self.authenticated_users = []

        self.request_types = [
            {
                "command": "/login",
                "params": ["username", "password"],
                "action": self.handle_login,
            },
            {
                "command": "/signup",
                "params": ["username", "password"],
                "action": self.handle_signup,
            },
        ]

    def listen(self):
        while True:
            read_sockets, _, exception_sockets = select.select(
                self.listening, [], self.listening
            )
            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    self.handle_connect(notified_socket)
                else:
                    self.handle_request(notified_socket)

    def handle_connect(self, request):
        client_socket, address = request.accept()
        self.listening.append(client_socket)
        client_socket.send(ServerProtocol.success())

    def handle_disconnect(self, request):
        pass

    def find_user(self, target_user, by="username", only_authenticated=True):
        if only_authenticated: users = self.authenticated_users
        else: users = self.registered_users
        user = filter(
            lambda user: target_user[by] == user[by], users
        )
        user = list(user)
        return user


    def handle_login(self, payload):
        username = payload["username"]
        password = payload["password"]
        user = self.find_user(payload)

        if user:
            if user["password"] == password:
                self.authenticated_users.append(user)
                response = ServerProtocol.auth_success(message="User authenticated")
            else:
                response = ServerProtocol.auth_error(message="Incorrect password")
        else:
            response = ServerProtocol.auth_error(message="User does not exist")
        return response

    def handle_signup(self, payload):
        exists = find_user(payload)


    def handle_request(self, connection):
        request = self.apply_middleware(connection)
        for request_type in self.request_types:
            if request["command"] == request_type["command"]:
                response = request_type["action"](request["payload"])
                break
        else:
            response = ServerProtocol.error()
        connection.send(response)

    def apply_middleware(self, request):
        raw_message = request.recv(constants.MAX_MSG_LEN)
        payload = parse_json(raw_message)
        return payload
