from imports import socket, select, constants, protocol


def start_server(ip=constants.IP, port=constants.PORT):
    print("Starting server...")
    server = Server(ip, port)
    print(f"Server started! Listening at {constants.IP}:{constants.PORT}...")
    server.listen()


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen()
        self.listening = [self.server_socket]

    def listen(self):
        while True:
            read_sockets, _, exception_sockets = select.select(
                self.listening, [], self.listening
            )
            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    self.handle_connect(notified_socket)
                else:
                    self.handle_message(notified_socket)

    def handle_request(self, request):
        print(request)
        raise NotImplementedError

    def handle_connect(self, request):
        client_socket, address = self.server_socket.accept()
        client_socket.send(protocol.success())

    def handle_disconnect(self, request):
        pass

    def handle_message(self, request):
        pass
