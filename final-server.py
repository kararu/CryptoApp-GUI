from ctypes import FormatError

import auth
import socket
import logging
import traceback
import threading


HEADER = 1024
SERVER = "127.0.0.1"
PORT = 5555
ADDR = (SERVER, PORT)
FMT = "utf-8"
CLIENTS: list[socket.socket] = []
USERS = []

# create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()


logger = logging.getLogger("server")
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch.setFormatter(formatter)

logger.addHandler(ch)
logging.basicConfig(level=logging.DEBUG)


def broadcast(message: bytes) -> None:
    # Broadcast the message to all client
    for client in CLIENTS:
        client.send(message)


def handle(client: socket.socket) -> None:
    while True:
        try:
            action, username, password = client.recv(HEADER).decode(FMT).split("|")

            print(action, username, password)

        except Exception as e:
            # Remove that person

            i = CLIENTS.index(client)
            CLIENTS.remove(client)
            client.close()
            user = USERS[i]
            logger.error("".join(traceback.format_tb(e.__traceback__)))
            broadcast(
                f"Client's {user} had left the chat due to and exception".encode(FMT)
            )
            USERS.remove(user)
            return


def wait_for_client() -> None:
    while True:
        client, address = server.accept()
        logger.info(f"Connected with {str(address)}")

        try:
            action, username, password = client.recv(HEADER).decode(FMT).split("|")
        except Exception:
            logger.critical("Timeout Error")
        else:

            match action:
                case "SU":
                    try:
                        auth.sign_up(username, password)
                    except auth.AlreadyRegistered:
                        client.send("already".encode(FMT))
                        logger.warning(
                            f"Client {username} tried to sign up, but failed"
                        )
                        client.close()
                        continue
                    else:
                        client.send("pass".encode(FMT))

                        logger.info(f"Client name: {username}")
                        client.send("Connected to the server".encode(FMT))
                case "SI":
                    if not auth.sign_in(username, password):
                        client.send("failed".encode(FMT))
                        logger.warning(
                            f"Client {username} tried to sign in, but failed"
                        )
                        client.close()
                        continue
                    else:
                        client.send("pass".encode(FMT))

                        logger.info(f"Client name: {username}")
                        client.send("Connected to the server".encode(FMT))

            USERS.append(username)
            CLIENTS.append(client)

            logger.info(f"Client name: {username}")
            broadcast(f"{username} joined the chat\n".encode(FMT))
            client.send("Connected to the server".encode(FMT))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()


def main():
    logger.info("Server is running ...")
    wait_for_client()


if __name__ == "__main__":
    main()
