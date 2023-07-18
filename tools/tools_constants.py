"""
Module referencing the main constants of the application.

Constants
---------
__version__ : str
    Version of the application.

MOBILE_MODE : bool
    Whether the application is launched on mobile or not.

APPLICATION_NAME : str
    Name of the application.

PATH_DATA_FOLDER : str
    Path to the data folder.

PATH_SETTINGS : str
    Path to the json file of settings.

PATH_RESOURCES_FOLDER : str
    Path to the resources folder.

PATH_LANGUAGE : str
    Path to the folder where are stored the json files of language.

PATH_APP_IMAGES : str
    Path to the folder where are stored the images for the application.

PATH_KIVY_FOLDER : str
    Path to the folder where are stored the different kv files.

DICT_LANGUAGE_FONT : dict
    Dictionary associating the code of language to the font.

DICT_LANGUAGE_CORRESPONDANCE : dict
    Dictionary associating the language to its code.
"""


###############
### Imports ###
###############


import math

### Kivy imports ###

from kivy import platform
from kivy.config import Config
from kivy.graphics import Color
from kivy.core.window import Window


from tools.tools_basis import (
    load_json_file,
    save_json_file
)


#################
### Constants ###
#################


### Version ###

__version__ = "1.1.0"

### Mode ###

MOBILE_MODE = platform == "android"
# MOBILE_MODE = True
DEBUG_MODE = False

### Kivy parameters ###

FPS = 30
OPACITY_RATE = 0.02
MSAA_LEVEL = 4

Config.set("graphics", "maxfps", FPS)
Config.set("graphics", "multisamples", MSAA_LEVEL)

### Paths ###

APPLICATION_NAME = "world_explorer"

PATH_DATA_FOLDER = "data/"
PATH_SETTINGS = PATH_DATA_FOLDER + "settings.json"

PATH_RESOURCES_FOLDER = "resources/"
PATH_LANGUAGE = PATH_RESOURCES_FOLDER + "languages/"
PATH_IMAGES = PATH_RESOURCES_FOLDER + "images/"
PATH_MAP_TEXTURES = PATH_IMAGES + "map_textures/"
PATH_ATLAS = PATH_RESOURCES_FOLDER + "atlas/"
PATH_KIVY_FOLDER = PATH_RESOURCES_FOLDER + "kivy/"
PATH_MAPS = PATH_RESOURCES_FOLDER + "maps/"
PATH_CHARACTER_IMAGES = PATH_IMAGES + "ghost_textures/"
PATH_LOGO = PATH_RESOURCES_FOLDER + "start_logo/"
PATH_SOUNDS = PATH_RESOURCES_FOLDER + "sounds/"
PATH_MUSICS = PATH_RESOURCES_FOLDER + "musics/"
PATH_FONTS = PATH_RESOURCES_FOLDER + "fonts/"
PATH_TITLE_FONT = PATH_FONTS + "enchanted_land/Enchanted Land.otf"

### Language ###

DICT_LANGUAGE_FONT = {
    "french": "Roboto",
    "english": "Roboto",
    "german": "Roboto",
    "italian": "Roboto",
    "spanish": "Roboto",
    "japanese": "resources/fonts/ShinGoPr5.otf"
}

DICT_LANGUAGE_CORRESPONDANCE = {
    "french": "Français",
    "english": "English",
    "german": "Deutsch",
    "italian": "Italiano",
    "spanish": "Español",
    "japanese": "Japanese"
}

################
### SETTINGS ###
################


MOVE = "MOVE"
STOP = "STOP"
INTERACT = "INTERACT"

SPACE_KEY = "spacebar"
SETTINGS = load_json_file(PATH_SETTINGS)
INTERACT_KEY = SETTINGS["keys"][INTERACT]
DICT_KEYS = SETTINGS["keys"]


class MyCollection():
    def __init__(self) -> None:
        self.dict_collection = SETTINGS["collection"]
        self.high_score = SETTINGS["high_score"]

    def find_new_stone(self, stone_name):
        self.dict_collection[DICT_TREASURE_STONES[stone_name]] = True
        SETTINGS["collection"] = self.dict_collection
        save_json_file(PATH_SETTINGS, SETTINGS)

    def update_high_score(self, score):
        if self.high_score < score:
            self.high_score = score
            SETTINGS["high_score"] = self.high_score
            save_json_file(PATH_SETTINGS, SETTINGS)


my_collection = MyCollection()

######################
### World explorer ###
######################


### Display ###

# Display parameters
CASES_ON_WIDTH = 8
CHARACTER_SCALE = 0.75
AUTOREMOVE_DELAY = 5

INC_TILE_SIZE_RATIO = 1.005


# Dictionary of textures
DICT_TILES_TEXTURE = {
    "G": ["ground"],
    "R": ["rock1", "rock2", "rock3"],
    "C": ["crystal"],
    "b": ["beacon"],
    "B": ["beacon_off"],
    "O": ["blank"]
}

DICT_TREASURE_STONES = {
    "Ag": "Agate",
    "Am": "Amber",
    "Ay": "Amethyst",
    "Av": "Aventurine",
    "Az": "Azurite",
    "Ci": "Citrine",
    "Di": "Diamond",
    "Em": "Emerald",
    "Fl": "Fluorine",
    "Ga": "Garnet",
    "Ja": "Jade",
    "Ll": "Lapis lazuli",
    "Ma": "Malachite",
    "Ob": "Obsidian",
    "On": "Onyx",
    "Op": "Opal",
    "Qu": "Rose quartz",
    "Ru": "Ruby",
    "Sa": "Sapphire",
    "Ti": "Tiger eye",
    "Tu": "Turquoise"
}

### Movements ###

SQUARE_TWO = math.sqrt(2)

# Speed of the character when moving
SPEED = 0.08

DICT_ORIENTATIONS = {
    "top": "back",
    "bottom": "front",
    "right": "right",
    "left": "left"
}
DICT_DISPLAY_ORIENTATIONS = {
    "top": "back",
    "bottom": "front",
    "right": "right",
    "left": "left",
    "left_bottom": "left_front",
    "right_bottom": "right_front",
    "left_top": "left_back",
    "right_top": "right_back",
}

# Dictionary indicating the different interactions between elements
DICT_TILES_MOVEMENT = {
    "G": [MOVE],
    "C": [INTERACT, MOVE],
    "R": [STOP],
    "B": [INTERACT, STOP],
    "b": [INTERACT, STOP],
    None: [STOP],
    "Ag": [INTERACT, MOVE],
    "Am": [INTERACT, MOVE],
    "Ay": [INTERACT, MOVE],
    "Av": [INTERACT, MOVE],
    "Az": [INTERACT, MOVE],
    "Ci": [INTERACT, MOVE],
    "Di": [INTERACT, MOVE],
    "Em": [INTERACT, MOVE],
    "Fl": [INTERACT, MOVE],
    "Ga": [INTERACT, MOVE],
    "Ja": [INTERACT, MOVE],
    "Ll": [INTERACT, MOVE],
    "Ma": [INTERACT, MOVE],
    "Ob": [INTERACT, MOVE],
    "On": [INTERACT, MOVE],
    "Op": [INTERACT, MOVE],
    "Qu": [INTERACT, MOVE],
    "Ru": [INTERACT, MOVE],
    "Sa": [INTERACT, MOVE],
    "Ti": [INTERACT, MOVE],
    "Tu": [INTERACT, MOVE]
}

MAX_TIME_IN_DARK = 10
CHARACTER_MOVEMENT = 5


################
### Tutorial ###
################


WAIT_FRAMES = 15
FRAMES_LATERAL = 5


######################
### Map generation ###
######################


MAP_SIZE = 10
CRYSTAL_PROBABILITY = 0.04
PRECIOUS_STONE_PROBABILITY = 0.02
NUMBER_CASES_DIGGER = 4
NUMBER_TRIALS = 6


##############
### Colors ###
##############

NB_DARK_CIRCLES = 8
DARKNESS_LIST = [Color(0.0, 0.0, 0.0, 1.0 - i * 0.7 / (NB_DARK_CIRCLES - 1))
                 for i in range(NB_DARK_CIRCLES)]

DARKNESS_COLOR_BACK = Color(0.0, 0.0, 0.0, 0.3)
MAX_CRYSTALS = 2
RATE_DIMINUTION_LIGHT = 0.02
RATE_DIMINUTION_LIGHT_AUGMENTATION = 0.0025
RATE_AUGMENTATION_LIGHT_DISPLAY = 1.0  # per crystal
START_BEACON_CASES = 3
MAX_INTENSITY = 100

#############
### Sound ###
#############

SOUND_VOLUME = 0.5
MUSIC_VOLUME = 0.5

SOUND_RADIUS_CRYSTAL = 3
SOUND_RADIUS_BEACON = 3
PROBABILITY_WATER_DROPS = 0.005

GAME_OVER_FREEZE_TIME = 2
