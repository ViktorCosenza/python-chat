import socket, select, constants, protocol
from protocol import ServerProtocol, parse_json


def start_server(verboose=False, ip=constants.IP, port=constants.PORT):
    print("Starting server...")
    server = Server(ip, port, debug=verboose)
    print(f"Server started! Listening at {constants.IP}:{constants.PORT}...")
    server.listen()


def new_user(username, password, sockt=None):
    return {"username": username, "password": password, "connection": sockt}


class Server:
    def __init__(self, ip, port, debug=False):
        self.debug = debug
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((socket.gethostbyname("0.0.0.0"), self.port))
        self.server_socket.listen()
        self.listening = [self.server_socket]
        self.clients = [
            {"username": None, "password": None, "socket": self.server_socket}
        ]
        self.registered_users = []

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
            {
                "command": "/msg",
                "params": ["message"],
                "action": self.handle_global_message,
            },
            {
                "command": "/private",
                "params": ["message", "dest"],
                "action": self.handle_private_message,
            },
        ]

    def listen(self):
        while True:
            read_sockets, _, _ = select.select(self.listening, [], self.listening)
            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    self.handle_connect(notified_socket)
                else:
                    self.handle_request(notified_socket)

    def update_client(self, user_data):
        user = self.find_user(
            user_data, by="socket", only_authenticated=True, where=self.clients
        )
        updated_user = {**user, **user_data}
        self.clients.remove(user)
        self.clients.append(updated_user)
        self.update_listeners()

    def update_listeners(self):
        self.listening = list(map(lambda client: client["socket"], self.clients))

    def handle_connect(self, connection):
        client_socket, _ = connection.accept()
        self.clients.append(
            {"username": None, "password": None, "socket": client_socket}
        )
        self.update_listeners()
        self.respond(ServerProtocol.success(), client_socket)

    def handle_disconnect(self, request):
        pass

    def find_user(
        self, target_user, by="username", only_authenticated=True, where=None
    ):
        if not where:
            where = self.registered_users
        user = filter(lambda user: target_user[by] == user[by], where)
        user = list(user)

        if only_authenticated:
            assert len(user) < 2, "Two users Share same username!!"
        user = user[0] if user else None
        return user

    def handle_login(self, payload):
        user = self.find_user(payload)
        if not user:
            return (ServerProtocol.auth_error(message="User does not exist"), None)
        if not payload["password"] == user["password"]:
            return (ServerProtocol.auth_error(message="Incorrect password"), None)

        return (
            ServerProtocol.auth_success(
                payload={"username": user["username"]}, message="User authenticated"
            ),
            user,
        )

    def handle_signup(self, payload):
        if self.find_user(payload):
            return (ServerProtocol.auth_error(message="Username already taken"), None)
        if len(payload["password"]) < 2:
            return (ServerProtocol.auth_error(message="Password is too small"), None)

        user = new_user(payload["username"], payload["password"])
        self.registered_users.append(user)
        return (
            ServerProtocol.auth_success(
                payload={"username": user["username"]},
                message="Successfully created user",
            ),
            user,
        )

    def handle_logout(self, connection):
        user = self.find_user({"socket": connection}, by="socket", where=self.clients)
        if user:
            self.clients.remove(user)
        return False

    def handle_private_message(self, payload):
        dest, message = payload["message"].split(":")
        dest = self.find_user(
            {"username": dest}, only_authenticated=True, where=self.clients
        )
        print(f"Private message dest: {dest['username']}")
        self.respond(
            ServerProtocol.message(
                {"username": f"private-{dest['username']}", "message": message}
            ),
            dest["socket"]
        )
        return (ServerProtocol.success(), None)

    def handle_global_message(self, payload):
        for client in self.clients:
            try:
                client["socket"].getpeername()
            except:
                continue
            self.respond(
                ServerProtocol.message(
                    {"username": payload["username"], "message": payload["message"]}
                ),
                client["socket"],
            )

        return (ServerProtocol.success(), None)

    def handle_request(self, connection):
        request = self.apply_middleware(connection)

        if not request:
            return
        for request_type in self.request_types:
            if request["command"] == request_type["command"]:
                (response, payload) = request_type["action"](request["payload"])
                if response["status"] in [protocol.AUTH_SUCCESS]:
                    client = {**payload, "socket": connection}
                    self.update_client(client)
                break
        else:
            response = ServerProtocol.error()
        self.respond(response, connection)

    def respond(self, data, connection):
        if self.debug:
            print(f"Responding: {data}\n\n")
            print(f"{connection}")
        response = protocol.encode(data)
        connection.send(response)

    def apply_middleware(self, connection):
        raw_message = connection.recv(constants.MAX_MSG_LEN)
        if len(raw_message) == 0:
            return self.handle_logout(connection)
        request = parse_json(raw_message)

        if self.debug:
            print(f"PRE-MIDDLEWARE {request}")
        if request["command"] not in ["/login", "/signup"]:
            user = self.find_user(
                {"socket": connection},
                by="socket",
                only_authenticated=False,
                where=self.clients,
            )
            request["payload"] = {**request["payload"], "username": user["username"]}

        if self.debug:
            print(f"POST-MIDDLEWARED: {request}")
        return request
