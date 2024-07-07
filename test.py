from socketfile import Client
import socket


def main():
    # choice = input("Start server (s) or client (c)? ")
    #
    # if choice == 's':
    #     server = Server()
    #     server.start()
    # elif choice == 'c':
    client = Client(socket.socket(socket.AF_INET, socket.SOCK_STREAM), "")
    server_ip, server_port = client.discover_server()
    client.start(server_ip, server_port)


if __name__ == "__main__":
    main()