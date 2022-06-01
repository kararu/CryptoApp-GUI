import socket
import threading

HEADER = 2048
FMT = 'utf-8'
SERVER = "127.0.0.1"
PORT = 7000
ADDR = (SERVER, PORT)
CLIENTS: list[socket.socket] = []
USERS = []

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

def broadcast(message: bytes) -> None:
    # Broadcast the message to all client
    for client in CLIENTS:
        client.send(message)

def handle(client: socket.socket) -> None:
    while True:
        try:
            message = client.recv(HEADER)
            broadcast(message)

        except Exception as e:

            i = CLIENTS.index(client)
            CLIENTS.remove(client)
            client.close()
            user = USERS[i]
            broadcast(f"Client's {user} had left the chat due to and exception".encode(FMT))
            USERS.remove(user)
            return


def wait_for_client() -> None:
    while True:
        client, address = server.accept()
        USERS.append(address)
        CLIENTS.append(client)
        client.send("Connected to the server".encode(FMT))

        thread = threading.Thread(target = handle, args = (client, ))
        thread.start()


def main():
    wait_for_client()


if __name__ == '__main__':
    main()
