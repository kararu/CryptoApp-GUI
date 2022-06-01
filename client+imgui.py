import os
import socket
from sys import flags
import threading
import traceback
import pyglet
from pyglet import gl
import imgui
from imgui.integrations.pyglet import create_renderer

HEADER = 2048
SERVER = "127.0.0.1"
PORT = 7000
ADDR = (SERVER, PORT)
FMT = 'utf-8'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

action = ""
username = ""
password = ""

screen = 0

class ServerConnectionError(Exception):
    pass

def recieve():
    while True:
        try:
            
            message = client.recv(HEADER).decode(FMT)

            if not message:
                raise ServerConnectionError

            match message:
                case '$LOGINUP':
                    client.send(action.encode(FMT))
                    continue
                case _:
                    print(message)

        except ServerConnectionError as e:
            print("Can't connect to the server")
            client.close()
            os._exit(1)
            return
                
        except Exception as e:
            print(''.join(traceback.format_tb(e.__traceback__)))
            client.close()
            return




def main():
    window = pyglet.window.Window(width=1280, height=720, caption="Hello")
    client.connect(ADDR)
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    imgui.create_context()
    impl = create_renderer(window)
    

    def login_screen(dt):
        global action
        global username
        global password
        global screen
        
        imgui.new_frame()

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item(
                    "Quit", 'Cmd+Q', False, True
                )

                if clicked_quit:
                    exit()

                imgui.end_menu()
            imgui.end_main_menu_bar()
        
        imgui.begin("Log In", closable = True, flags = imgui.WINDOW_NO_MOVE | imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        changed, username = imgui.input_text('<- Username',username, 256, flags = imgui.INPUT_TEXT_AUTO_SELECT_ALL | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE)
        changed, password = imgui.input_text('<- Password',password, 256, flags = imgui.INPUT_TEXT_AUTO_SELECT_ALL | imgui.INPUT_TEXT_ALWAYS_INSERT_MODE | imgui.INPUT_TEXT_PASSWORD)
        
        if imgui.button("Sign In"):
            imgui.open_popup("select-popup")
            screen += 1
            action = "I"

        imgui.same_line()

        if imgui.button("Sign Up"):
            screen += 1
            action = "U"

        if imgui.begin_popup("select-popup"):
            imgui.text("Select one")
            imgui.end_popup()

        imgui.end()
    
    def play_screen(dt):
        amount = 0

        imgui.new_frame()

        imgui.begin("cash In-Out", flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        if imgui.button("Send"):
            imgui.open_popup("Amount")
        if imgui.button("Request"):
            imgui.open_popup("Amount")
        if imgui.button("Cash-In"):
            imgui.open_popup("Amount")
        if imgui.button("Cash-Out"):
            imgui.open_popup("Amount")

        if imgui.begin_popup("Amount"):
            imgui.text("Select one")
            imgui.separator()
            changed, amount = imgui.input_text('', amount, 256)
            imgui.end_popup()
        imgui.end()

        
        imgui.begin("Mine", flags = imgui.WINDOW_ALWAYS_AUTO_RESIZE | imgui.WINDOW_NO_TITLE_BAR)
        if imgui.button("Mine"):
            ...
        imgui.end()

    
    def draw(dt):
        if screen == 0:
            login_screen(dt)
        else:
            play_screen(dt)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    message = f"{action}|{username}|{password}"

    client.send(message.encode(FMT))
    
    recieve_thread = threading.Thread(target = recieve)
    recieve_thread.start()

    window.clear()
    pyglet.clock.schedule_interval(draw, 1/120.)
    pyglet.app.run()
    impl.shutdown()

if __name__ == "__main__":
    main()