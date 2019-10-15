from argparse import ArgumentParser
from server import start_server
from client import start_client

def main():
    parser = ArgumentParser(description="A simple chat application")
    parser.add_argument("--server", help="Run server app or client", action='store_true')
    args = parser.parse_args()
    if args.server: 
        start_server()
    else:
        start_client()

if __name__ == "__main__":
    main()
