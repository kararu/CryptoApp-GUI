from crypto_app_core import auth, transactions
import socket
import logging
import traceback
import threading
import typing as t

from dotenv import load_dotenv, find_dotenv
import os
from numpy import insert
from pymongo.mongo_client import MongoClient


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

# mongo connect
password = os.environ.get("MONGODB_PWD")
connection_string = f"mongodb+srv://Kararu:{password}@cryptoapp.zhsbqpe.mongodb.net/?retryWrites=true&w=majority"
mongo = MongoClient(connection_string)
user = mongo.user_data.passwords


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


def sign_in(client: socket.socket, username: str, password: str):
    try:
        check: t.Optional[dict[str, t.Any]] = user.find_one({"name": username})
        if not check:
            client.send("N".encode(FMT))
            return
        auth.verify_password(check, password)

    except auth.AuthenticationError:
        client.send("F".encode(FMT))
        logger.warning(f"Client {username} tried to sign in, but failed")
        client.close()
    else:
        client.send("P".encode(FMT))
        logger.info(f"Client name: {username}")



def sign_up(client, username, password):

    if not user.find_one({"name": username}):
        doc = {"name": username, "password": auth.finalize_password(password, auth.hash_algo)}
        user.insert_one(doc)
        client.send("P".encode(FMT))
        logger.info(f"Client name: {username}")
    else:
        client.send("A".encode(FMT))
        logger.warning(f"Client {username} tried to sign up, but failed")
        client.close()


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
                case "SI":
                    sign_in(client, username, password)

                case "SU":
                    sign_up(client, username, password)

            U.users.append(username)
            U.clients.append(client)
            u = transactions.HybridUser(username)
            transactions.N.connected_users.add(u)

            logger.info(f"Client name: {username}")

            thread = threading.Thread(target=accept_new_users, args=(client,))
            thread.start()


def main():
    logger.info("Server is running ...")
    wait_for_client()


if __name__ == "__main__":
    main()
