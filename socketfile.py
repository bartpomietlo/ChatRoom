import socket
import threading
import time
from random import randint


class Client:
    _count = 0

    def __init__(self, conn, nickname):
        self.conn = conn
        self.nickname = nickname
        Client._count += 1

    def __del__(self):
        Client.decrement()

    @classmethod
    def decrement(cls):
        cls._count -= 1

    @classmethod
    def get_count(cls):
        return cls._count

    def receive_messages(self):
        while True:
            try:
                message = self.conn.recv(1024).decode('utf-8')
                if message:
                    print(message)
                else:
                    break
            except (ConnectionResetError, ConnectionAbortedError, socket.error) as e:
                print(f"An error occurred: {e}")
                self.conn.close()
                break

    def send_messages(self):
        while True:
            message = input('')
            if message.startswith('/nickname'):
                self.conn.send(message.encode('utf-8'))
            else:
                self.conn.send(f'{self.nickname}: {message}'.encode('utf-8'))

    def discover_server(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_socket.bind(("", 37020))
        print("Listening for broadcast...")
        while True:
            data, addr = udp_socket.recvfrom(1024)
            message = data.decode('utf-8')
            server_ip, server_port = message.split(':')
            server_port = int(server_port)
            print(f"Discovered server at {server_ip}:{server_port}")
            return server_ip, server_port

    def start(self, server_ip, server_port):
        try:
            self.conn.connect((server_ip, server_port))
            print("Connected to the server")

            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.start()

            send_thread = threading.Thread(target=self.send_messages)
            send_thread.start()
        except Exception as e:
            print(f"Could not connect to the server: {e}")


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        hostname = socket.gethostname()
        self.serv_ip_addr = socket.gethostbyname(hostname)
        self.port = randint(1000, 10000)
        self.server.bind((self.serv_ip_addr, self.port))
        self.server.listen(2)
        self.connections = []
        print(f"Server started on {self.serv_ip_addr}:{self.port}")

    def __receive(self, conn):
        while True:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                for client in self.connections:
                    if conn == client.conn:
                        if data[:9].lower() == "/nickname":
                            self.broadcast(f"zmieniono nick {client.nickname} na {data[10:]}", conn)
                            client.nickname = data[10:]
                        else:
                            self.broadcast(f'{client.nickname}: {data}', conn)
            except ConnectionResetError:
                break
        self.remove_connection(conn)

    def broadcast(self, message, conn):
        for client in self.connections:
            if conn != client.conn:
                client.conn.send(message.encode('utf-8'))
        print(message)

    def remove_connection(self, conn):
        for i, client in enumerate(self.connections):
            if client.conn == conn:
                self.connections.pop(i)
                del client
                break
        conn.close()
        print(f"Client disconnected. Total clients: {Client.get_count()}")

    def broadcast_udp(self):
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f"{self.serv_ip_addr}:{self.port}"
        while True:
            udp_socket.sendto(message.encode('utf-8'), ('<broadcast>', 37020))
            time.sleep(5)  # Broadcast every 5 seconds

    def start(self):
        threading.Thread(target=self.broadcast_udp).start()
        print("Server is running...")
        while True:
            conn, addr = self.server.accept()
            print(f"Connected by {addr}")
            nickname = f"Klient{len(self.connections) + 1}"
            new_client = Client(conn, nickname)
            self.connections.append(new_client)
            print(f"New client connected. Total clients: {Client.get_count()}")
            receive_thread = threading.Thread(target=self.__receive, args=(conn,))
            receive_thread.start()

