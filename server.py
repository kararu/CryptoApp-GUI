import auth
import socket
from _thread import *
import logging
import traceback
import threading

HEADER = 2048
FMT = 'utf-8'
SERVER = "127.0.0.1"
PORT = 7000
ADDR = (SERVER, PORT)
CLIENTS: list[socket.socket] = []
USERS = []


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(ADDR)
except socket.error as e:
    str(e)
    
s.listen()
print("Waiting for a connection, Server Started")


logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)
logging.basicConfig(level=logging.DEBUG)

def broadcast(message: bytes) -> None:
    for client in CLIENTS:
        client.send(message)

def handle(client: socket.socket) -> None:
    while True:
        try:
            message = client.recv(HEADER)
            broadcast(message)

        except Exception as e:
            # Remove that person

            i = CLIENTS.index(client)
            CLIENTS.remove(client)
            client.close()
            user = USERS[i]
            #logger.error(''.join(traceback.format_tb(e.__traceback__)))
            broadcast(f"Client's {user} had left the chat due to and exception".encode(FMT))
            USERS.remove(user)
            return

def wait_for_client() -> None:
    
    while True:
        client, address = s.accept()
        logger.info(f"Connected with {str(address)}")
        
        try:
            action, username, password = client.recv(HEADER).decode(FMT).split('|')
        except Exception:
            logger.critical('Timeout Error')
        else:
            match action:
                case 'U':
                    try:
                        auth.sign_up(username, password)
                    except auth.AlreadyRegistered:
                        client.send("Already registered".encode(FMT))
                        logger.warning(f"Client {username} tried to sign up, but failed")
                        # client.send("$LOGINUP".encode(FMT))
                        client.close()
                        continue
                case 'I':
                    if not auth.sign_in(username, password):
                        client.send("Wrong username or password".encode(FMT))
                        logger.warning(f"Client {username} tried to sign in, but failed")
                        client.close()
                        continue
                        

            USERS.append(username)
            CLIENTS.append(client)

            logger.info(f"Client name: {username}")
            broadcast(f"{username} joined the chat\n".encode(FMT))
            client.send("Connected to the server".encode(FMT))

            thread = threading.Thread(target = handle, args = (client, ))
            thread.start()

def main():
    logger.info("Server is running ...")
    wait_for_client()


if __name__ == '__main__':
    main()