import os
import socket
from sys import flags
import threading
import traceback
import pyglet
from pyglet import gl
import imgui
from imgui.integrations.pyglet import create_renderer


def main():
    window = pyglet.window.Window(width=1280, height=720, caption="Hello")
    gl.glClearColor(0.1, 0.1, 0.1, 1)
    imgui.create_context()
    impl = create_renderer(window)

    def play_screen(dt):
        imgui.new_frame()
        imgui.begin("Ledger")

        a = ""

        if imgui.button("Broadcast Transaction"):
            imgui.open_popup("Create Transaction")

        if imgui.begin_popup("Create Transaction"):
            imgui.core.input_text("", a, 256)
            imgui.end_popup()

        imgui.end()

    def draw(dt):
        play_screen(dt)
        window.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    window.clear()
    pyglet.clock.schedule_interval(draw, 1 / 120.0)
    pyglet.app.run()
    impl.shutdown()


if __name__ == "__main__":
    main()
