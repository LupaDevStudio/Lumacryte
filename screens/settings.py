"""
Module for the settings menu
"""


from kivy.uix.screenmanager import Screen
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from tools.tools_constants import (
    PATH_TITLE_FONT,
    DICT_KEYS,
    INTERACT,
    PATH_SETTINGS,
    SETTINGS,
    PATH_IMAGES,
    my_collection,
    Window
)
from tools.tools_basis import (
    save_json_file
)


class SettingsScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)

    path_images = PATH_IMAGES
    font = PATH_TITLE_FONT
    high_score = StringProperty("")
    top_key = StringProperty()
    left_key = StringProperty("")
    bottom_key = StringProperty("")
    right_key = StringProperty("")
    interact_key = StringProperty("")
    path_back_image = PATH_IMAGES + "settings_background.png"
    font_ratio = NumericProperty(0)
    width_back_image = ObjectProperty(Window.size[0])
    height_back_image = ObjectProperty(Window.size[0] * 392 / 632)

    def init_screen(self):
        self.font_ratio = Window.size[0]/800
        self.width_back_image = Window.size[0]
        self.height_back_image = Window.size[0] * 392 / 632
        self.high_score = "High score: " + str(my_collection.high_score)
        self.top_key = DICT_KEYS["top"]
        self.left_key = DICT_KEYS["left"]
        self.bottom_key = DICT_KEYS["bottom"]
        self.right_key = DICT_KEYS["right"]
        self.interact_key = DICT_KEYS[INTERACT]
        self._keyboard = Window.request_keyboard(
            self._keyboard_closed, self, 'text')
        self._keyboard.bind(on_key_up=self.update_on_key_up)
        self.current_button = None

    def select_next_key(self, type_input):
        dict_buttons = {
            "top": [self.ids.top_button, self.ids.top_key_input],
            "left": [self.ids.left_button, self.ids.left_key_input],
            "bottom": [self.ids.bottom_button, self.ids.bottom_key_input],
            "right": [self.ids.right_button, self.ids.right_key_input],
            INTERACT: [self.ids.interact_button, self.ids.interact_key_input]
        }
        for key in dict_buttons:
            if key == type_input:
                self.current_button = dict_buttons[key][0]
                dict_buttons[key][1].text = "Press new key"
            else:
                dict_buttons[key][1].text = DICT_KEYS[key]

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
        global DICT_KEYS, SETTINGS
        dict_widgets = {
            self.ids.top_button: [self.ids.top_key_input, "top"],
            self.ids.left_button: [self.ids.left_key_input, "left"],
            self.ids.bottom_button: [self.ids.bottom_key_input, "bottom"],
            self.ids.right_button: [self.ids.right_key_input, "right"],
            self.ids.interact_button: [self.ids.interact_key_input, INTERACT],
        }
        if self.current_button is not None:
            dict_widgets[self.current_button][0].text = keycode[1]
            DICT_KEYS[dict_widgets[self.current_button][1]] = keycode[1]
            SETTINGS["keys"] = DICT_KEYS
            save_json_file(PATH_SETTINGS, SETTINGS)
            self.current_button = None

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
        if self._keyboard is not None:
            self._keyboard.unbind(on_key_up=self.update_on_key_up)
            self._keyboard = None
