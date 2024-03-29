import os
import socket

import imgui
import pyglet
import logging

from pyglet import gl
from imgui.integrations.pyglet import create_renderer

from crypto_app_core import transactions as ts


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ServerConnectionError(Exception):
    pass


class A:
    username: str = ""
    password: str = ""
    warning: str = ""
    balance: int = 0
    send_recieve_amount: int = 0
    logged_in: bool = False
    

class X:
    sender_name: str = ""
    recipient_name: str = ""
    amount: float = .0
    fee: float = .0
    message: str = ""


HEADER = 2048
SERVER = "172.104.185.153"
PORT = 7000
ADDR = (SERVER, PORT)
FMT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def authenticate():
    while True:
        try:
            if not (respond := client.recv(HEADER).decode(FMT)):
                raise ServerConnectionError
            else:
                match respond:
                    case 'F':
                        A.warning = "Failed to sign in, please try again"
                    case 'A':
                        A.warning = "This username has already been used"
                    case 'N':
                        A.warning = "Username not found"
                    case 'P':
                        A.logged_in = True
                    case _:
                        raise NotImplementedError

                break

        except ServerConnectionError:
            logger.error("Cannot connect to the server")
            client.close()
            os._exit(1)


def recieve_data_from_server():
    while True:
        try:
            if not (message := client.recv(HEADER).decode(FMT)):
                raise ServerConnectionError

            logger.debug(message)
        except ServerConnectionError:
            logger.error("Cannot connect to the server")
            client.close()
            os._exit(1)


def main():
    window = pyglet.window.Window(width=1280, height=720, caption="Hello")
    client.connect(ADDR)
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    imgui.create_context()
    impl = create_renderer(window)

    def login_screen(_):
        imgui.new_frame()

        imgui.begin("Log In")
        _changed, A.username = imgui.input_text(
            "<- Username",
            A.username,
            256,
            flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL
            | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE,
        )
        _changed, A.password = imgui.input_text(
            "<- Password",
            A.password,
            256,
            flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL
            | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE
            | imgui.INPUT_TEXT_PASSWORD,
        )
        imgui.text(A.warning)

        if imgui.button("Sign In"):
            client.send(f"SI|{A.username}{A.password}".encode(FMT))

            authenticate()

        imgui.same_line()

        if imgui.button("Sign Up"):
            client.send(f"SU|{A.username}{A.password}".encode(FMT))

            if len(A.username) >= 5 and len(A.password) >= 5:
                authenticate()
            else:
                A.warning = "Username and password should be 5 letter or longer"

        imgui.end()

    def main_screen(_):
        imgui.new_frame()

        imgui.begin(
            "Cash-In/Out",
            flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR,
        )
        _changed, A.send_recieve_amount = imgui.input_float("", A.send_recieve_amount)

        if imgui.button("Send"):
            ...

        if imgui.button("Request"):
            ...

        if imgui.button("Cash-In"):
            ...
            A.balance += A.send_recieve_amount
            A.send_recieve_amount = 0

        if imgui.button("Cash-Out"):
            if A.send_recieve_amount != 0:
                A.balance -= A.send_recieve_amount
                A.send_recieve_amount = 0

        imgui.end()

        imgui.begin(
            "Mine", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR
        )
        if imgui.button("Mine"):
            ...
        imgui.end()

        imgui.begin(
            "User", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR
        )
        imgui.text(f"Username: {A.username}")
        imgui.text(
            f"Public Key: 8vMbjPj2MS^Bb#yF^YpaJ1@zP6@#Ozl4%d3NPJZFszjqYIIclZSUEYPgyt@dRTITDn6AGphd1b*6sWLyU4qm5NjpQ&eMYgR%5vUuMX38^9xmjU2p9nR304a6k2YdVDD!"
        )
        imgui.new_line()
        imgui.text(f"Balance: {A.balance}")

        imgui.end()

        
        imgui.begin("Broadcasted Transactions")

        imgui.columns(6, "Transactions")

        imgui.separator()
        for i, (txt, o) in enumerate(
            zip(
                ("Index", "Sender", "Recipient", "Amount", "Fee", "Message"),
                (50, 150, 250, 325, 375, 600),
            ),
            1,
        ):
            imgui.text(txt)
            imgui.next_column()
            imgui.core.set_column_offset(i, o)
        imgui.separator()
        
        u = ts.N.get_user_with_name(A.username)
        assert u
        
        for tx in u.caught_up_transactions:
            tx_info = tx.info
            for txt in (tx.index, tx_info.sender, tx_info.recipient, tx_info.amount, tx_info.fee, tx_info.message):
                imgui.text(txt)
                imgui.next_column()

        if imgui.button("Broadcast Transaction"):
            imgui.open_popup("Create Transaction")

        if imgui.begin_popup("Create Transaction"):
            imgui.core.input_text("<- Sender username", X.sender_name, 256)
            imgui.core.input_text("<- Recipient username", X.recipient_name, 256)
            imgui.core.input_float("<- Amount", X.amount)
            imgui.core.input_float("<- Fee", X.fee)
            imgui.core.input_text_multiline("<- Message", X.message, 1024)

            imgui.end_popup()



        imgui.end()

        

    def draw(_):
        if not A.logged_in:
            login_screen(_)
        else:
            main_screen(_)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    window.clear()
    pyglet.clock.schedule_interval(draw, 1 / 120.0)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()


"""
    message = f"{action}|{username}|{password}"

    client.send(message.encode(FMT))
    
    recieve_thread = threading.Thread(target = recieve)
    recieve_thread.start()
"""
