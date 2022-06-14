import os
import socket
from sys import flags
import threading
import pyglet
from pyglet import gl
import imgui
from imgui.integrations.pyglet import create_renderer

HEADER = 2048
SERVER = "127.0.0.1"
PORT = 7000
ADDR = (SERVER, PORT)
FMT = "utf-8"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
message = "text here"


class ServerConnectionError(Exception):
    pass


def recieve():
    while True:
        try:
            # Recieve Message
            message = client.recv(HEADER).decode(FMT)

            if not message:
                raise ServerConnectionError

            print(message)

        except ServerConnectionError as e:
            print("Can't connect to the server")
            client.close()
            os._exit(1)
            return


def main():
    window = pyglet.window.Window(width=1280, height=720, caption="Hello")
    client.connect(ADDR)
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    imgui.create_context()
    impl = create_renderer(window)

    def login_screen(dt):
        global message

        imgui.new_frame()

        imgui.begin(
            "Texting",
            closable=True,
            flags=imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE,
        )
        changed, message = imgui.input_text(
            "<- Message",
            message,
            256,
            flags=imgui.INPUT_TEXT_AUTO_SELECT_ALL
            | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE,
        )

        if imgui.button("Send"):
            client.send(message.encode(FMT))
            message = "text here"

        imgui.end()

    def draw(dt):
        login_screen(dt)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    recieve_thread = threading.Thread(target=recieve)
    recieve_thread.start()

    window.clear()
    pyglet.clock.schedule_interval(draw, 1 / 120.0)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()
