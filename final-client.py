import os
import socket

import imgui
import pyglet
import logging

from pyglet import gl
from imgui.integrations.pyglet import create_renderer


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ServerConnectionError(Exception):
    pass


class U:
    username: str = ""
    password: str = ""
    balance: int = 0
    send_recieve_amount: int = 0
    logged_in: bool = False


HEADER = 2048
SERVER = "127.0.0.1"
PORT = 7000
ADDR = (SERVER, PORT)
FMT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def recieve():
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
    # client.connect(ADDR)
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    imgui.create_context()
    impl = create_renderer(window)

    def login_screen(_):
        imgui.new_frame()

        imgui.begin("Log In")
        _changed, U.username = imgui.input_text(
            "<- Username",
            U.username,
            256,
            flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL
            | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE,
        )
        _changed, U.password = imgui.input_text(
            "<- Password",
            U.password,
            256,
            flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL
            | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE
            | imgui.INPUT_TEXT_PASSWORD,
        )

        if imgui.button("Sign In"):
            client.send(f"I|{U.username}{U.password}".encode(FMT))

            if client.recv(HEADER).decode(FMT) == "F":  # Implement Failed Log in Splash
                ...
            else:
                U.logged_in = True

        imgui.same_line()

        if imgui.button("Sign Up"):
            client.send(f"I|{U.username}{U.password}".encode(FMT))

            if False:  # Implement username and password check
                ...
            else:
                U.logged_in = True
        imgui.end()

    def main_screen(_):
        imgui.new_frame()

        imgui.begin(
            "Cash-In/Out",
            flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR,
        )
        _changed, U.send_recieve_amount = imgui.input_float("", U.send_recieve_amount)

        if imgui.button("Send"):
            ...

        if imgui.button("Request"):
            ...

        if imgui.button("Cash-In"):
            ...
            U.balance += U.send_recieve_amount
            U.send_recieve_amount = 0

        if imgui.button("Cash-Out"):
            if U.send_recieve_amount != 0:
                U.balance -= U.send_recieve_amount
                U.send_recieve_amount = 0

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
        imgui.text(f"Username: {U.username}")
        imgui.text(
            f"Public Key: 8vMbjPj2MS^Bb#yF^YpaJ1@zP6@#Ozl4%d3NPJZFszjqYIIclZSUEYPgyt@dRTITDn6AGphd1b*6sWLyU4qm5NjpQ&eMYgR%5vUuMX38^9xmjU2p9nR304a6k2YdVDD!"
        )
        imgui.new_line()
        imgui.text(f"Balance: {U.balance}")

        imgui.end()

    def draw(_):
        if not U.logged_in:
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
