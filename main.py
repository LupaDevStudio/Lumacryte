"""
Main module of the generator of dialogs.
"""


###############
### Imports ###
###############


### Python imports ###

import os
import time

### Kivy imports ###

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.clock import Clock


### Module imports ###

from tools.tools_constants import (
    PATH_KIVY_FOLDER,
    PATH_IMAGES,
    SPACE_KEY,
    FPS,
    PATH_LOGO,
    DEBUG_MODE,
    MOBILE_MODE
)
from tools.tools_world_explorer import (
    WorldExplorerScreen,
    load_texture,
    LogoTextureWidget
)
from screens import (
    MenuScreen,
    SettingsScreen,
    GameOverScreen,
    CollectionScreen
)
from tools.tools_kivy import (
    color_label,
    background_color,
    Window
)
from tools.tools_sound import (
    music_mixer
)


def change_window_size(*args):
    global WINDOW_SIZE, SCREEN_RATIO

    # Compute the size of one tile in pixel
    WINDOW_SIZE = Window.size
    SCREEN_RATIO = WINDOW_SIZE[0] / WINDOW_SIZE[1]


Window.bind(on_resize=change_window_size)
change_window_size()

# Set the fullscreen
if not MOBILE_MODE:
    # Window.fullscreen = "auto"
    pass


###############
### General ###
###############


class LogoScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    def init_screen(self):
        self.list_textures = self.load_logo_textures()
        self.counter_texture = 0
        self.logo_image = LogoTextureWidget(
            size_hint=(0.5, 0.5 * SCREEN_RATIO),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            texture=self.list_textures[self.counter_texture])
        self.logo_image.keep_ratio = True
        self.add_widget(self.logo_image)
        self.loading_logo = Clock.schedule_interval(self.update, 1 / FPS)

    def load_logo_textures(self):
        list_files = os.listdir(PATH_LOGO)
        list_files.sort(key=lambda file:
                        int(file[-7:-4].replace("k", "").replace("_", "")),
                        reverse=True)
        list_textures = []
        for file in list_files:
            list_textures.append(load_texture(PATH_LOGO + file))
        return list_textures

    def update(self, *args):
        time.sleep(0.0587)
        if self.counter_texture < len(self.list_textures):
            new_texture = self.list_textures[self.counter_texture]
            self.logo_image.texture = new_texture
            self.counter_texture += 1
        else:
            Clock.unschedule(self.loading_logo)
            self.manager.init_screen("menu")


class WindowManager(ScreenManager):
    """
    Screen manager, which allows the navigation between the different menus.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gray_color = background_color
        self.color_label = color_label
        self.transition = NoTransition()
        self.add_widget(Screen(name="opening"))
        self.current = "opening"
        self.list_former_screens = []

    def init_screen(self, screen_name, *args):
        # Link the keyboard
        if not MOBILE_MODE:
            self._keyboard = Window.request_keyboard(
                self._keyboard_closed, self, 'text')
            self._keyboard.bind(on_key_up=self.update_on_key_up)

        if screen_name == "world_explorer":
            music_mixer.play("game_music", loop=True)
        if screen_name != "logo":
            Window.clearcolor = background_color
        self.current = screen_name
        self.get_screen(self.current).init_screen(*args)

    def update_on_key_up(self, keyboard, keycode):
        """
        Update the the list of keys pressed when the key is up.

        Parameters
        ----------
        keyboard

        keycode: int
            Integer representing the key pressed by the user

        Returns
        -------
        None
        """
        if keycode[1] == SPACE_KEY and self.current == "menu":
            self.init_screen("world_explorer")

    def _keyboard_closed(self):
        """
        Unbind the keyboard.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._keyboard.unbind(on_key_up=self.update_on_key_up)
        self._keyboard = None


class MainApp(App, Widget):
    """
    Main class of the application.
    """

    def build(self):
        """
        Build the application.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        Window.clearcolor = (0, 0, 0, 1)
        self.icon = PATH_IMAGES + "logo.png"

    def on_start(self):
        if MOBILE_MODE:
            Window.update_viewport()
        music_mixer.play("title_music", loop=True)
        if DEBUG_MODE:
            self.root_window.children[0].init_screen("menu")
        else:
            self.root_window.children[0].init_screen("logo")
        return super().on_start()


# Run the application
if __name__ == "__main__":
    for file_name in os.listdir(PATH_KIVY_FOLDER):
        if file_name.endswith(".kv"):
            Builder.load_file(PATH_KIVY_FOLDER + file_name, encoding="utf-8")
    MainApp().run()
