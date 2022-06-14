import auth
import socket
import logging
import traceback
import threading


HEADER = 1024
SERVER = ""
PORT = 7000
ADDR = (SERVER, PORT)
FMT = "utf-8"


class U:
    clients: list[socket.socket] = []
    users: list[str] = []


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


def broadcast_data(message: bytes) -> None:
    # Broadcast the message to all client
    for client in U.clients:
        client.send(message)


def accept_new_users(client: socket.socket) -> None:
    while True:
        try:
            action, username, password = client.recv(HEADER).decode(FMT).split("|")

            print(action, username, password)

        except Exception as e:
            # Remove that person

            i = U.clients.index(client)
            U.clients.remove(client)
            client.close()
            user = U.users[i]
            logger.error("".join(traceback.format_tb(e.__traceback__)))
            broadcast_data(
                f"Client's {user} had left the chat due to and exception".encode(FMT)
            )
            U.users.remove(user)
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
                case auth.R.SIGN_UP:
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
                case auth.R.SIGN_IN:
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

            U.users.append(username)
            U.clients.append(client)

            logger.info(f"Client name: {username}")
            broadcast_data(f"{username} joined the chat\n".encode(FMT))
            client.send("Connected to the server".encode(FMT))

            thread = threading.Thread(target=accept_new_users, args=(client,))
            thread.start()


def main():
    logger.info("Server is running ...")
    wait_for_client()


if __name__ == "__main__":
    main()
