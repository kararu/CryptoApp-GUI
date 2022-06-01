import socket
import os

import pyglet
from pyglet import gl
import imgui
from imgui.integrations.pyglet import create_renderer

class ServerConnectionError(Exception):
    pass

HEADER = 2048
SERVER = "127.0.0.1"
PORT = 7000
ADDR = (SERVER, PORT)
FMT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

username = ""
password = ""
balance = 0
send_recieve_amount = 0
logged_in = False


class V:
    username: str = ""
    password: str = ""
    balanace: int = 0
    send_recieve_amount: int = 0
    logged_in: bool = False


def recieve():
    while True:
        try:
            
            message = client.recv(HEADER).decode(FMT)

            if not message:
                raise ServerConnectionError

            print(message)
        
        except ServerConnectionError as e:
            print("Can't connect to the server")
            client.close()
            os._exit(1)

def main():

    window = pyglet.window.Window(width=1280, height=720, caption="Hello")
    #client.connect(ADDR)
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    imgui.create_context()
    impl = create_renderer(window)
    

    def login_screen(_):
        
        global logged_in
        
        imgui.new_frame()
        
        imgui.begin("Log In", closable = True, flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        changed, V.username = imgui.input_text('<- Username',V.username, 256, flags = imgui.INPUT_TEXT_AUTO_SELECT_ALL | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE)
        changed, V.password = imgui.input_text('<- Password',V.password, 256, flags = imgui.INPUT_TEXT_AUTO_SELECT_ALL | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE | imgui.INPUT_TEXT_PASSWORD)
                
        if imgui.button("Sign In"):
            logged_in = True

        imgui.same_line()

        if imgui.button("Sign Up"):
            logged_in = True

        imgui.end()
    
    def main_screen(_):

        global send_recieve_amount
        global balance

        imgui.new_frame()

        imgui.begin("cash In-Out", flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        changed, send_recieve_amount = imgui.input_float('', send_recieve_amount)

        if imgui.button("Send"):
            imgui.open_popup("Amount")
        if imgui.button("Request"):
            imgui.open_popup("Amount")
        if imgui.button("Cash-In"):
            imgui.open_popup("Amount")
            balance += send_recieve_amount
            send_recieve_amount = 0
        if imgui.button("Cash-Out"):
            imgui.open_popup("Amount")
            if send_recieve_amount != 0:
                balance -= send_recieve_amount
                send_recieve_amount = 0

        imgui.begin_popup

        imgui.end()

        
        imgui.begin("Mine", flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        if imgui.button("Mine"):
            ...
        imgui.end()

        imgui.begin("User", flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        imgui.text("Username: " + username)
        imgui.new_line()
        imgui.text("Coin: " + str(balance))

        imgui.end()

    
    def draw(_):
        if not logged_in:
            login_screen(_)
        else:
            main_screen(_)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    window.clear()
    pyglet.clock.schedule_interval(draw, 1/120.)
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