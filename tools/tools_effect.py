"""
Module to create visual effects with kivy
"""

from kivy.uix.widget import Widget
from kivy.graphics import Line, Rectangle


from tools.tools_constants import (
    DARKNESS_LIST,
    DARKNESS_COLOR_BACK,
    NB_DARK_CIRCLES,
    MAP_SIZE,
    Window,
    CASES_ON_WIDTH
)


def change_window_size(*args):
    global WINDOW_SIZE, SCREEN_RATIO, TILE_SIZE

    # Compute the size of one tile in pixel
    WINDOW_SIZE = Window.size
    SCREEN_RATIO = WINDOW_SIZE[0] / WINDOW_SIZE[1]
    TILE_SIZE = WINDOW_SIZE[0] / CASES_ON_WIDTH


Window.bind(on_resize=change_window_size)
change_window_size()


class AmbientDarkness(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.canvas.add(DARKNESS_COLOR_BACK)
        self.canvas.add(Rectangle(pos=(0, 0), size=(
            WINDOW_SIZE[0], WINDOW_SIZE[1])))


class CircleDarkness(Widget):
    def __init__(self, radius, **kwargs):
        super().__init__(**kwargs)
        self.radius = radius
        self.radius_line = MAP_SIZE * TILE_SIZE * 2
        self.update()
        self.draw()

    def change_radius(self, new_radius):
        self.radius = new_radius
        self.update()

    def update(self):
        self.line_width = self.radius_line - self.radius * TILE_SIZE

    def draw(self):
        self.canvas.clear()
        for i in range(NB_DARK_CIRCLES):
            self.canvas.add(DARKNESS_LIST[i])
            self.canvas.add(
                Line(circle=(self.x, self.y, self.radius_line), width=self.line_width + TILE_SIZE * 0.5 * i / (NB_DARK_CIRCLES - 1)))
