"""
World explorer tools module

It allows to create a map based on a grid where a character can move and explore.
"""


###############
### Imports ###
###############

### Python import ###

from math import floor, sqrt
import random as rd
import math


### Kivy imports ###

from kivy.clock import Clock
from kivy.atlas import Atlas
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar

### Module imports ###

from tools.tools_constants import (
    PATH_ATLAS,
    PATH_IMAGES,
    DICT_TILES_TEXTURE,
    SPEED,
    CASES_ON_WIDTH,
    INTERACT,
    WAIT_FRAMES,
    FRAMES_LATERAL,
    MOBILE_MODE,
    FPS,
    PATH_MAPS,
    DICT_TILES_MOVEMENT,
    MOVE,
    DICT_ORIENTATIONS,
    SQUARE_TWO,
    DEBUG_MODE,
    MAX_CRYSTALS,
    RATE_DIMINUTION_LIGHT,
    MAX_INTENSITY,
    RATE_AUGMENTATION_LIGHT_DISPLAY,
    MAP_SIZE,
    GAME_OVER_FREEZE_TIME,
    SOUND_RADIUS_CRYSTAL,
    START_BEACON_CASES,
    PROBABILITY_WATER_DROPS,
    MAX_TIME_IN_DARK,
    CHARACTER_MOVEMENT,
    PATH_SETTINGS,
    DICT_TREASURE_STONES,
    RATE_DIMINUTION_LIGHT_AUGMENTATION,
    DICT_DISPLAY_ORIENTATIONS,
    my_collection,
    SOUND_RADIUS_BEACON,
    Window,
    INC_TILE_SIZE_RATIO,
    CHARACTER_SCALE
)
from tools.tools_kivy_mobile import (
    MobileJoystick,
    MobileButton
)
from tools.tools_map import (
    create_new_map
)
from tools.tools_effect import (
    AmbientDarkness,
    CircleDarkness
)
from tools.tools_sound import (
    sound_mixer,
    music_mixer
)
from tools.tools_basis import (
    load_json_file
)


def change_window_size(*args):
    global WINDOW_SIZE, SCREEN_RATIO, TILE_SIZE, TILE_SIZE_HINT, CHARACTER_SIZE,\
        CASES_ON_HEIGHT, CASES_ON_WIDTH, CASES_ON_HALF_HEIGHT, CASES_ON_HALF_WIDTH,\
        CASES_ON_HALF_TUPLE

    # Compute the size of one tile in pixel
    WINDOW_SIZE = Window.size
    SCREEN_RATIO = WINDOW_SIZE[0] / WINDOW_SIZE[1]
    TILE_SIZE = WINDOW_SIZE[0] / CASES_ON_WIDTH
    TILE_SIZE_HINT = (INC_TILE_SIZE_RATIO * TILE_SIZE /
                      WINDOW_SIZE[0], INC_TILE_SIZE_RATIO * TILE_SIZE / WINDOW_SIZE[1])
    CHARACTER_SIZE = CHARACTER_SCALE * TILE_SIZE

    # Compute the number of cases that fit in height
    CASES_ON_HEIGHT = int(CASES_ON_WIDTH / SCREEN_RATIO) + 1

    CASES_ON_HALF_HEIGHT = CASES_ON_HEIGHT // 2 + 2
    CASES_ON_HALF_WIDTH = CASES_ON_WIDTH // 2 + 2
    CASES_ON_HALF_TUPLE = [CASES_ON_HALF_WIDTH, CASES_ON_HALF_HEIGHT]


Window.bind(on_resize=change_window_size)
change_window_size()


###############
### Classes ###
###############


class GridMap():
    def __init__(self) -> None:
        self.tiles = {}
        self.map_size = None
        self.offset_list = []

    def add_submap(self, grid_map_list, offset_tuple):
        if self.map_size is None:
            self.map_size = (len(grid_map_list[0]), len(grid_map_list))
        elif self.map_size != (len(grid_map_list[0]), len(grid_map_list)):
            return ValueError("The size does not correspond to the current size used")

        x_offset, y_offset = (
            offset_tuple[0] * self.map_size[0],
            offset_tuple[1] * self.map_size[1]
        )

        self.offset_list.append(offset_tuple)

        for j in range(len(grid_map_list)):
            for i in range(len(grid_map_list[0])):
                self.tiles[(i + x_offset, j + y_offset)
                           ] = grid_map_list[len(grid_map_list) - 1 - j][i]

    def get_texture(self, position):
        if position not in self.tiles:
            return "O"
        return self.tiles[position]

    def replace_texture(self, position, new_texture):
        self.tiles[position] = new_texture

    def get_tile_type(self, position):
        if position not in self.tiles:
            return None
        return self.tiles[position]

    def set_tile_type(self, position, value):
        self.tiles[position] = value

    def __str__(self) -> str:
        res = ""
        keys = self.tiles.keys()
        x_keys = [key[0] for key in keys]
        y_keys = [key[1] for key in keys]
        x_min_id = min(x_keys)
        x_max_id = max(x_keys)
        y_min_id = min(y_keys)
        y_max_id = max(y_keys)
        for j in range(y_max_id, y_min_id - 1, -1):
            for i in range(x_min_id, x_max_id + 1):
                if (i, j) in self.tiles:
                    res += self.tiles[(i, j)] + " "
                else:
                    res += "  "
            res += "\n"
        return res

    def __repr__(self) -> str:
        return self.__str__()


class LogoTextureWidget(Image):
    def __init__(self, texture, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.texture = texture


class TextureWidget(Image):
    """
    An image widget where the texture is direcltly set.
    """

    def __init__(self, name_texture, position=None, **kwargs):
        super().__init__(**kwargs)
        self.allow_stretch = True
        self.keep_ratio = False
        self.name_texture = name_texture
        if name_texture in DICT_TILES_TEXTURE.keys():
            self.texture = TEXTURE_DICT[
                rd.choice(DICT_TILES_TEXTURE[name_texture])]
        elif name_texture in DICT_TREASURE_STONES.keys():
            self.texture = TEXTURE_DICT[
                DICT_TREASURE_STONES[name_texture]]
        else:
            self.texture = TEXTURE_DICT[name_texture]
        self.position = position
        self.letter_tile = name_texture

    def set_texture(self, texture):
        self.texture = texture


class WorldExplorerScreen(Screen):
    """
    Class to define a world explorer screen
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the grid variables
        self.grid_map = GridMap()

        # Create the map variables
        self.x_char_on_map = 0.0
        self.y_char_on_map = 0.0
        self.x_char_on_screen = 0.0
        self.y_char_on_screen = 0.0
        self.x_map_on_screen = 0.0
        self.y_map_on_screen = 0.0
        self.prec_map_center_grid_pos = (0, 0)

        self.character_orientation = "bottom"
        self.display_orientation = "bottom"

        self.score = 0
        self.number_crystals = [0, 0]
        self.beacon_life = 10

        # Create a list to contain the widgets for texture maps
        self.textures_map_list = []
        self.textures_map_to_remove_list = []

        self.is_game_over = False
        self.game_over_timer = 0
        self.in_darkness_count = 0

    def init_screen(self):
        """
        Init the screen when loaded.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """

        self.font_ratio = Window.size[0] / 800

        # Choose the possible directions for the next beacons
        self.beacon_x_change = 1 - 2 * rd.randint(0, 1)
        self.beacon_y_change = 1 - 2 * rd.randint(0, 1)

        self.count_frame = 0
        self.rate_diminution_light = RATE_DIMINUTION_LIGHT

        self.is_game_over = False
        self.game_over_timer = 0
        self.in_darkness_count = 0
        SETTINGS = load_json_file(PATH_SETTINGS)
        self.INTERACT_KEY = SETTINGS["keys"][INTERACT]
        self.DICT_KEYS = SETTINGS["keys"]

        self.display_indicators()

        # Update the positions and display according to the FPS frequency
        Clock.schedule_interval(self.display_tutorial, 3 / FPS)

        # Store the map informations
        self.build_grid_map()

        # Set the default position
        self.x_char_on_map = self.grid_map.map_size[0] / 2 + 0.5 - 1
        self.y_char_on_map = self.grid_map.map_size[1] / 2 + 0.5
        self.update_map_on_screen_position()
        self.prec_map_center_grid_pos = self.get_map_center_grid_pos()

        # Create the character and display it on the screen
        self.character = TextureWidget(
            name_texture="front",
            x=self.x_char_on_screen - CHARACTER_SIZE / 2,
            y=self.y_char_on_screen - CHARACTER_SIZE / 2,
            size_hint=(CHARACTER_SIZE / WINDOW_SIZE[0], CHARACTER_SIZE / WINDOW_SIZE[1]))
        self.add_widget(self.character)
        self.character_state = 1
        self.crystal_1 = Image(
            texture=TEXTURE_DICT[DICT_TILES_TEXTURE["C"][0]],
            x=self.x_char_on_screen,
            y=self.y_char_on_screen - 3 * CHARACTER_SIZE / 4,
            size_hint=(None, None),
            width=TILE_SIZE // 4,
            keep_ratio=True,
            opacity=0)
        self.add_widget(self.crystal_1)
        self.crystal_1_name = ""
        self.crystal_2 = Image(
            texture=TEXTURE_DICT[DICT_TILES_TEXTURE["C"][0]],
            x=self.x_char_on_screen - CHARACTER_SIZE // 2,
            y=self.y_char_on_screen - 4 * CHARACTER_SIZE / 5,
            size_hint=(None, None),
            width=TILE_SIZE // 4,
            keep_ratio=True,
            opacity=0)
        self.add_widget(self.crystal_2)
        self.crystal_2_name = ""

        # Create the textures for the map
        x_min_value, x_max_value = self.compute_min_max_display_values(0)
        y_min_value, y_max_value = self.compute_min_max_display_values(1)
        for x in range(x_min_value, x_max_value + 1):
            for y in range(y_min_value, y_max_value + 1):
                self.add_texture_to_map((x, y))

        self.darkness_circle = CircleDarkness(
            3, x=WINDOW_SIZE[0] / 2, y=WINDOW_SIZE[1] / 2)
        self.add_widget(self.darkness_circle, 0)

        self.ambient_darkness = AmbientDarkness()
        self.add_widget(self.ambient_darkness)

        self.beacon_position = (MAP_SIZE // 2, MAP_SIZE // 2 - 0.5)
        self.list_keydown = []
        self.list_keyup = []
        self.take_crystal = False
        self.have_taken_crystal = False
        self.local_counter_tutorial = 0

        self.beacon_map_history = [(0, 0)]

        self.is_beacon_near = False

    def display_indicators(self):
        # Add a FPS counter for the debug mode
        if DEBUG_MODE:
            self.fps_label = Label(
                text="60",
                pos_hint={"x": 0, "y": 0},
                size_hint=(0.05, 0.05),
                font_size=10 * self.font_ratio)
            self.add_widget(self.fps_label)

        # Label for the number of crystals
        pos_hint = {"right": 0.95, "y": 0}
        if MOBILE_MODE:
            pos_hint = {"right": 0.95, "top": 0.95}
        self.number_crystals_label = Label(
            text="0 / " + str(MAX_CRYSTALS),
            pos_hint=pos_hint,
            size_hint=(0.075, 0.05 * SCREEN_RATIO),
            bold=True,
            font_size=10 * self.font_ratio
        )
        self.add_widget(self.number_crystals_label)

        # Image for the number of crystals
        pos_hint = {"right": 0.98, "y": 0.01}
        if MOBILE_MODE:
            pos_hint = {"right": 0.98, "top": 0.94}
        self.number_crystals_image = Image(
            texture=TEXTURE_DICT[DICT_TILES_TEXTURE["C"][0]],
            pos_hint=pos_hint,
            size_hint=(None, None),
            width=0.03 * WINDOW_SIZE[0]
        )
        self.number_crystals_image.height = self.number_crystals_image.width
        self.add_widget(self.number_crystals_image)

        # Progress bar of the life of the beacon
        self.progress_bar_beacon = ProgressBar(
            value=self.beacon_life,
            max=MAX_INTENSITY,
            pos_hint={"x": 0.025, "top": 1},
            size_hint=(0.95, 0.05)
        )
        self.add_widget(self.progress_bar_beacon)

    def build_grid_map(self):

        x_or_y_direction = rd.randint(0, 1)

        beacon_direction = (x_or_y_direction * self.beacon_x_change,
                            (1 - x_or_y_direction) * self.beacon_y_change)

        # Add the map in the center
        center_map, self.list_precious_stones = create_new_map(
            list_precious_stones=[], has_beacon=True)
        self.grid_map.add_submap(center_map, (0, 0))

        # Add the map with the other beacon
        for position in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            if position == beacon_direction:
                new_map, self.list_precious_stones = create_new_map(
                    list_precious_stones=self.list_precious_stones, has_beacon=True)
                self.grid_map.add_submap(new_map, position)
            else:
                new_map, self.list_precious_stones = create_new_map(
                    list_precious_stones=self.list_precious_stones, has_beacon=False)
                self.grid_map.add_submap(new_map, position)

    def expand_grid_map(self):
        # Scan maps around
        grid_offset = (self.prec_map_center_grid_pos[0] // MAP_SIZE,
                       self.prec_map_center_grid_pos[1] // MAP_SIZE)

        if grid_offset == (0, 0):
            return

        x_or_y_direction = rd.randint(0, 1)

        beacon_direction = (x_or_y_direction * self.beacon_x_change,
                            (1 - x_or_y_direction) * self.beacon_y_change)

        map_with_beacon_offset = (
            grid_offset[0] + beacon_direction[0], grid_offset[1] + beacon_direction[1])

        for i in range(-1, 2):
            for j in range(-1, 2):
                offset = (grid_offset[0] + i, grid_offset[1] + j)
                has_beacon = offset == map_with_beacon_offset
                if (i, j) != (0, 0) and offset not in self.beacon_map_history:
                    new_map, self.list_precious_stones = create_new_map(
                        list_precious_stones=self.list_precious_stones,
                        has_beacon=has_beacon)
                    self.grid_map.add_submap(new_map, offset)

        self.beacon_map_history.append(map_with_beacon_offset)

    def compute_min_max_display_values(self, direction_id):
        min_value = self.prec_map_center_grid_pos[direction_id] - \
            CASES_ON_HALF_TUPLE[direction_id]
        max_value = self.prec_map_center_grid_pos[direction_id] + \
            CASES_ON_HALF_TUPLE[direction_id]
        return min_value, max_value

    def update_map_on_screen_position(self):
        """
        Update the position of the map on the screen.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.x_map_on_screen = self.x_char_on_map * \
            TILE_SIZE - WINDOW_SIZE[0] / 2
        self.y_map_on_screen = self.y_char_on_map * \
            TILE_SIZE - WINDOW_SIZE[1] / 2

    def update_char_on_screen_position(self):
        """
        Update the position of the character on the screen.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Movements of the character
        offset = CHARACTER_MOVEMENT * math.sin(self.count_frame * 0.15)

        self.crystal_1.x = self.x_char_on_screen - CHARACTER_SIZE // 2 + 0.5 * offset
        self.crystal_1.y = self.y_char_on_screen - 3 * CHARACTER_SIZE / 4 + 0.5 * offset
        self.crystal_2.x = self.x_char_on_screen + 0.5 * offset
        self.crystal_2.y = self.y_char_on_screen - 4 * CHARACTER_SIZE / 5 - 0.5 * offset
        self.x_char_on_screen = WINDOW_SIZE[0] / 2
        self.y_char_on_screen = WINDOW_SIZE[1] / 2 + offset
        self.character.x = self.x_char_on_screen - CHARACTER_SIZE / 2
        self.character.y = self.y_char_on_screen - CHARACTER_SIZE / 2

    def get_char_grid_pos(self) -> tuple:
        """
        Return the grid coordinates of the main character.
        """
        return (floor(self.x_char_on_map), floor(self.y_char_on_map))

    def get_map_center_grid_pos(self) -> tuple:
        """
        Return the grid coordinates of the center of the map.
        """
        return (floor(self.x_map_on_screen / TILE_SIZE + CASES_ON_WIDTH / 2),
                floor(self.y_map_on_screen / TILE_SIZE + CASES_ON_HEIGHT / 2))

    def update_textures_map_list(self, forced_reload=False) -> None:
        """
        Update the list of textures to keep on display.
        """
        current_map_center_grid_pos = self.get_map_center_grid_pos()

        if self.prec_map_center_grid_pos != current_map_center_grid_pos or forced_reload:

            # Create the textures for the map
            x_min_value, x_max_value = self.compute_min_max_display_values(0)
            y_min_value, y_max_value = self.compute_min_max_display_values(1)

            to_delete_list = []
            to_add_list = []
            on_screen = []

            for x in range(x_min_value, x_max_value + 1):
                for y in range(y_min_value, y_max_value + 1):
                    on_screen.append((x, y))

            position_texture_map_list = [
                e.position for e in self.textures_map_list]

            for position in position_texture_map_list:
                if not position in on_screen:
                    to_delete_list.append(position)

            for position in on_screen:
                if not position in position_texture_map_list:
                    to_add_list.append(position)

            # Delete useless tiles
            for texture_map in self.textures_map_list[:]:
                if texture_map.position in to_delete_list:
                    self.textures_map_list.remove(texture_map)
                    self.remove_widget(texture_map)

            # Add necessary tiles
            textures_map_position_list = [
                texture_map.position for texture_map in self.textures_map_list]
            for position_to_add in to_add_list:
                if position_to_add not in textures_map_position_list:
                    self.add_texture_to_map(position_to_add)

            self.prec_map_center_grid_pos = self.get_map_center_grid_pos()

    def add_texture_to_map(self, position_to_add):
        """
        Add a texture to the list of textures to display
        """
        letter_tile = self.grid_map.get_texture(position_to_add)
        new_texture_map = TextureWidget(
            name_texture=letter_tile,
            position=position_to_add,
            size_hint=TILE_SIZE_HINT)
        self.textures_map_list.append(new_texture_map)
        self.add_widget(new_texture_map, 100)

        if letter_tile in DICT_TREASURE_STONES or letter_tile == "C":
            new_texture_map.size_hint = (
                TILE_SIZE_HINT[0] / 2, TILE_SIZE_HINT[1] / 2)

        if letter_tile != "G":
            ground_texture = TextureWidget(
                position=position_to_add,
                size_hint=TILE_SIZE_HINT,
                name_texture="G")
            self.textures_map_list.append(ground_texture)
            self.add_widget(ground_texture, 110)

    def update_textures_map_positions(self):
        """
        Update the positions of all textures on screen
        """
        texture_map: TextureWidget
        for texture_map in self.textures_map_list:
            x_grid, y_grid = texture_map.position
            texture_map.x = x_grid * TILE_SIZE - \
                self.x_map_on_screen
            texture_map.y = y_grid * TILE_SIZE - \
                self.y_map_on_screen
            if texture_map.name_texture in DICT_TREASURE_STONES or texture_map.name_texture == "C":
                texture_map.x += TILE_SIZE / 4
                texture_map.y += TILE_SIZE / 4

    def update_textures_map_on_screen(self):
        """
        Update all the textures map to display them on the screen.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.update_textures_map_list()
        self.update_textures_map_positions()

    def update_display_orientation(self, x_movement, y_movement):
        display_orientation = ""
        if abs(x_movement) > 0.25:
            if x_movement < 0:
                display_orientation += "left_"
            else:
                display_orientation += "right_"
        if abs(y_movement) > 0.25:
            if y_movement > 0:
                display_orientation += "top"
            else:
                display_orientation += "bottom"
        else:
            if display_orientation != "":
                display_orientation = display_orientation.replace("_", "")
            else:
                display_orientation = "bottom"
        return display_orientation

    def update_facing_character(self):
        self.character.texture = TEXTURE_DICT[
            DICT_DISPLAY_ORIENTATIONS[self.display_orientation]]

    def update_darkness_position(self):
        x_grid, y_grid = self.beacon_position
        self.darkness_circle.x = x_grid * TILE_SIZE - \
            self.x_map_on_screen + TILE_SIZE / 2
        self.darkness_circle.y = y_grid * TILE_SIZE - \
            self.y_map_on_screen - TILE_SIZE / 2
        self.darkness_circle.draw()

    def update_char_on_map_position(self, x_movement: float, y_movement: float):
        """
        Update the position of the character on the map.
        It takes into account the collisions; the character can only go on "MOVE" tiles.
        It also updates the orientation of the character on the map.

        Parameters
        ----------
        x_movement: float
            Movement on the x axis

        y_movement: float
            Movement on the y axis

        Returns
        -------
        None
        """
        # Update the orientation of the character on the map
        if abs(x_movement) > abs(y_movement):
            if x_movement > 0:
                new_orientation = DICT_ORIENTATIONS["right"]
            else:
                new_orientation = DICT_ORIENTATIONS["left"]
        else:
            if y_movement > 0:
                new_orientation = DICT_ORIENTATIONS["top"]
            else:
                new_orientation = DICT_ORIENTATIONS["bottom"]

        if self.character_orientation != new_orientation:
            self.character_orientation = new_orientation

        # Update the orientation of the display of the character
        display_orientation = self.update_display_orientation(
            x_movement, y_movement)
        if self.display_orientation != display_orientation:
            self.display_orientation = display_orientation
            self.update_facing_character()

        # Update the position of the character on the map
        x_extremity = self.x_char_on_map + SPEED * x_movement
        y_extremity = self.y_char_on_map + SPEED * y_movement

        # Values of next tiles
        next_xy = DICT_TILES_MOVEMENT[self.grid_map.get_tile_type(
            (floor(x_extremity), floor(y_extremity)))]
        next_x = DICT_TILES_MOVEMENT[self.grid_map.get_tile_type(
            (floor(x_extremity), floor(self.y_char_on_map)))]
        next_y = DICT_TILES_MOVEMENT[self.grid_map.get_tile_type(
            (floor(self.x_char_on_map), floor(y_extremity)))]

        if MOVE in next_xy and (MOVE in next_x or MOVE in next_y):
            self.x_char_on_map += SPEED * x_movement
            self.y_char_on_map += SPEED * y_movement
        elif MOVE in next_x:
            self.x_char_on_map += SPEED * x_movement
        elif MOVE in next_y:
            self.y_char_on_map += SPEED * y_movement
        self.update_textures_map_on_screen()

    def search_near_crystal(self, current_grid_pos):
        x_grid, y_grid = current_grid_pos
        has_near_crystal = False
        for i in range(x_grid - SOUND_RADIUS_CRYSTAL, x_grid + SOUND_RADIUS_CRYSTAL + 1):
            for j in range(y_grid - SOUND_RADIUS_CRYSTAL, y_grid + SOUND_RADIUS_CRYSTAL + 1):
                if self.grid_map.get_tile_type((i, j)) == "C":
                    has_near_crystal = True
        return has_near_crystal

    def search_near_off_beacon(self, current_grid_pos):
        x_grid, y_grid = current_grid_pos
        has_near_beacon = False
        for i in range(x_grid - SOUND_RADIUS_BEACON, x_grid + SOUND_RADIUS_BEACON + 1):
            for j in range(y_grid - SOUND_RADIUS_BEACON, y_grid + SOUND_RADIUS_BEACON + 1):
                if self.grid_map.get_tile_type((i, j)) == "B":
                    has_near_beacon = True
        return has_near_beacon

    def manage_near_beacon_sound(self):
        if self.is_beacon_near:
            if sound_mixer.musics["near_beacon"].state != "play":
                sound_mixer.play("near_beacon", stop_other_sounds=False)
        else:
            if sound_mixer.musics["near_beacon"].state == "play":
                sound_mixer.fade_out("near_beacon", 1, mode="exp")

    def manage_near_crystal_sound(self):
        if self.is_crystal_near:
            if sound_mixer.musics["near_crystal"].state != "play":
                sound_mixer.play("near_crystal", stop_other_sounds=False)
        else:
            if sound_mixer.musics["near_crystal"].state == "play":
                sound_mixer.fade_out("near_crystal", 1, mode="exp")

    def compute_distance_with_beacon(self):
        distance = sqrt(
            (self.x_char_on_map - self.beacon_position[0])**2 + (self.y_char_on_map - self.beacon_position[1])**2)
        return distance

    def clean(self):
        Clock.unschedule(self.update)
        self.darkness_circle.canvas.clear()
        self.grid_map = GridMap()
        self.ambient_darkness.canvas.clear()

    def game_over(self):
        self.game_over_timer += 1
        if self.game_over_timer > GAME_OVER_FREEZE_TIME * FPS:
            my_collection.update_high_score(self.score)
            self.manager.init_screen("game_over", self.score)
            self.clean()
            self.clear_widgets()

    def manage_in_darkness(self):
        distance_with_beacon = self.compute_distance_with_beacon()
        if distance_with_beacon > self.darkness_circle.radius:
            self.in_darkness = True
            if self.in_darkness_count == 0:
                sound_mixer.play(
                    "darkness", stop_other_sounds=False, loop=False)
            if self.in_darkness:
                self.in_darkness_count += 1
            if self.in_darkness_count > MAX_TIME_IN_DARK * FPS:
                sound_mixer.play("death", stop_other_sounds=True)
                self.darkness_circle.change_radius(0)
                self.update_darkness_position()
                self.is_game_over = True
                music_mixer.stop()

        else:
            if sound_mixer.musics["darkness"].state == "play":
                sound_mixer.fade_out("darkness", 1, mode="exp")
            self.in_darkness = False
            self.in_darkness_count = 0

    def get_next_tile(self):
        """
        Get tile towards which the character is oriented.

        Parameters
        ----------
        None

        Returns
        -------
        next_tile: str
            String representing the type of tile

        position: (int, int)
            Tuple representing the position of the corresponding tile
        """
        if self.character_orientation == DICT_ORIENTATIONS["top"]:
            position = (floor(self.x_char_on_map),
                        floor(self.y_char_on_map) + 1)
            next_tile = self.grid_map.get_tile_type(position)
        elif self.character_orientation == DICT_ORIENTATIONS["bottom"]:
            position = (floor(self.x_char_on_map),
                        floor(self.y_char_on_map) - 1)
            next_tile = self.grid_map.get_tile_type(position)
        elif self.character_orientation == DICT_ORIENTATIONS["left"]:
            position = (floor(self.x_char_on_map) -
                        1, floor(self.y_char_on_map))
            next_tile = self.grid_map.get_tile_type(position)
        elif self.character_orientation == DICT_ORIENTATIONS["right"]:
            position = (floor(self.x_char_on_map) +
                        1, floor(self.y_char_on_map))
            next_tile = self.grid_map.get_tile_type(position)
        return next_tile, position

    def interact_with_environment(self):
        """
        Interact with the environment.
        It takes into account the tile towards which the character is oriented.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        for key in self.list_keyup:
            bool_interact = False

            # Check the interaction with the current tile
            position = (floor(self.x_char_on_map), floor(self.y_char_on_map))
            my_tile = self.grid_map.get_tile_type(position)
            if key == self.DICT_KEYS[INTERACT] and (
                    INTERACT in DICT_TILES_MOVEMENT[my_tile] or my_tile in DICT_TREASURE_STONES):
                bool_interact = True

            # Check the interaction with the next tile
            if not bool_interact:
                my_tile, position = self.get_next_tile()
                if key == self.DICT_KEYS[INTERACT] and (
                        INTERACT in DICT_TILES_MOVEMENT[my_tile] or my_tile in DICT_TREASURE_STONES):
                    bool_interact = True

            if bool_interact:
                # Get crystal in our bag
                if my_tile == "C":

                    # Can only take crystals in less than MAX_CRYSTALS
                    if self.number_crystals[0] < MAX_CRYSTALS:
                        self.number_crystals[0] += 1
                        self.number_crystals[1] += 1
                        sound_mixer.play(
                            "get_crystal", stop_other_sounds=False)
                        self.number_crystals_label.text = str(
                            self.number_crystals[0]) + " / " + str(MAX_CRYSTALS)

                        self.grid_map.replace_texture(position, "G")

                        # Delete the former textures
                        for texture in self.textures_map_list:
                            if texture.position == position and (
                                    texture.name_texture == "C"):
                                self.remove_widget(texture)
                                self.textures_map_list.remove(texture)
                                break

                        if self.number_crystals[0] == 1:
                            self.crystal_1.texture = TEXTURE_DICT[DICT_TILES_TEXTURE["C"][0]]
                            self.crystal_1.opacity = 1
                            self.crystal_1_name = my_tile
                        else:
                            self.crystal_2.texture = TEXTURE_DICT[DICT_TILES_TEXTURE["C"][0]]
                            self.crystal_2.opacity = 1
                            self.crystal_2_name = my_tile

                # Bring back the crystals to the beacon
                elif my_tile in ["B", "b"]:
                    if my_tile == "B" and self.number_crystals[1] != 0:
                        self.darkness_circle.radius = START_BEACON_CASES
                    self.score += self.number_crystals[1]
                    self.darkness_circle.change_radius(
                        self.darkness_circle.radius + self.number_crystals[1] * RATE_AUGMENTATION_LIGHT_DISPLAY)
                    if self.number_crystals[0] != 0:
                        self.crystal_1.opacity = 0
                        if self.number_crystals[0] == 2:
                            self.crystal_2.opacity = 0

                        # Reset the counter of crystals
                        self.number_crystals[0] = 0
                        self.number_crystals[1] = 0
                        self.number_crystals_label.text = "0 / " + \
                            str(MAX_CRYSTALS)

                        # Update the collection if needed
                        if self.crystal_1_name not in ["C", ""]:
                            my_collection.find_new_stone(self.crystal_1_name)
                        if self.crystal_2_name not in ["C", ""]:
                            my_collection.find_new_stone(self.crystal_2_name)

                        if my_tile == "b":
                            sound_mixer.play(
                                "give_crystal", stop_other_sounds=False)
                        else:
                            self.start_new_beacon()

                # Interact with the precious stones
                elif my_tile in DICT_TREASURE_STONES:
                    if self.number_crystals[0] < MAX_CRYSTALS:
                        self.number_crystals[0] += 1
                        sound_mixer.play(
                            "get_crystal", stop_other_sounds=False)
                        self.number_crystals_label.text = str(
                            self.number_crystals[0]) + " / " + str(MAX_CRYSTALS)
                        self.grid_map.replace_texture(position, "G")

                        # Delete the former textures
                        for texture in self.textures_map_list:
                            if texture.position == position and (
                                    texture.name_texture == my_tile):
                                self.remove_widget(texture)
                                self.textures_map_list.remove(texture)
                                break

                        if self.number_crystals[0] == 1:
                            self.crystal_1.texture = TEXTURE_DICT[
                                DICT_TREASURE_STONES[my_tile]]
                            self.crystal_1.opacity = 1
                            self.crystal_1_name = my_tile
                        else:
                            self.crystal_2.texture = TEXTURE_DICT[
                                DICT_TREASURE_STONES[my_tile]]
                            self.crystal_2.opacity = 1
                            self.crystal_2_name = my_tile

        self.list_keyup = []

    def start_new_beacon(self):

        self.score += 5
        self.rate_diminution_light += RATE_DIMINUTION_LIGHT_AUGMENTATION

        # Play the sound
        on_screen_beacon_tile = self.get_next_tile()[1]
        sound_mixer.play(
            "start_beacon", stop_other_sounds=True)

        # Change the parameters
        self.progress_bar_beacon.value = MAX_INTENSITY
        self.beacon_life = MAX_INTENSITY

        # Remove the previous beacon
        self.grid_map.set_tile_type(
            (floor(self.beacon_position[0]), floor(self.beacon_position[1])), "R")

        # Change the position of the light circle
        self.beacon_position = (
            on_screen_beacon_tile[0], on_screen_beacon_tile[1] + 0.5)

        # Replace the texture of the beacon
        self.grid_map.set_tile_type(
            on_screen_beacon_tile, "b")
        for texture_map in self.textures_map_list[:]:
            if texture_map.position == on_screen_beacon_tile:
                self.textures_map_list.remove(texture_map)
                self.remove_widget(texture_map)
        self.add_texture_to_map(on_screen_beacon_tile)

        # Increase the size of the map
        self.expand_grid_map()

        # Reload all textures to avoid junction problems
        temp_list = self.textures_map_list[:]
        self.textures_map_list = []
        self.update_textures_map_list(forced_reload=True)
        for widget in temp_list:
            self.remove_widget(widget)

    def redraw_interface(self):
        self.remove_widget(self.number_crystals_label)
        self.add_widget(self.number_crystals_label)
        self.remove_widget(self.number_crystals_image)
        self.add_widget(self.number_crystals_image)
        self.remove_widget(self.progress_bar_beacon)
        self.add_widget(self.progress_bar_beacon)
        if DEBUG_MODE:
            self.remove_widget(self.fps_label)
            self.add_widget(self.fps_label)

    def display_tutorial(self, *args):
        self.is_tutorial = True
        if self.count_frame < WAIT_FRAMES:
            self.list_keyup = []
            self.list_keydown = []
        elif self.count_frame in range(WAIT_FRAMES, WAIT_FRAMES + FRAMES_LATERAL):
            self.list_keyup = []
            self.list_keydown = [self.DICT_KEYS["left"]]
        elif self.count_frame in range(WAIT_FRAMES + FRAMES_LATERAL, WAIT_FRAMES + FRAMES_LATERAL * 2):
            self.list_keyup = []
            self.list_keydown = [self.DICT_KEYS["right"]]
        elif self.count_frame < WAIT_FRAMES + FRAMES_LATERAL * 2 + 0.75 / SPEED:
            self.list_keyup = []
            self.list_keydown = [self.DICT_KEYS["bottom"]]
        elif not self.take_crystal and not self.have_taken_crystal:
            self.list_keyup = []
            self.list_keydown = [self.DICT_KEYS["bottom"]]
            self.take_crystal = True
        elif self.take_crystal:
            self.list_keyup = [self.INTERACT_KEY]
            self.list_keydown = [self.DICT_KEYS["bottom"]]
            if self.local_counter_tutorial > FRAMES_LATERAL:
                self.take_crystal = False
                self.have_taken_crystal = True
            if self.local_counter_tutorial != 0:
                self.list_keydown = []
            self.local_counter_tutorial += 1
        elif self.count_frame < WAIT_FRAMES + 3 * FRAMES_LATERAL + 1.25 / SPEED:
            self.list_keyup = []
            self.list_keydown = [self.DICT_KEYS["right"]]
        else:
            self.list_keyup = [self.INTERACT_KEY]
            self.list_keydown = [self.DICT_KEYS["right"]]
            self.is_tutorial = False

        self.count_frame += 1
        x_movement, y_movement = self.get_movements_keyboard()
        self.update_char_on_map_position(
            x_movement=x_movement,
            y_movement=y_movement)
        self.interact_with_environment()
        self.update_darkness_position()

        self.update_map_on_screen_position()
        self.update_char_on_screen_position()

        if not self.is_tutorial:
            Clock.unschedule(self.display_tutorial)
            Clock.schedule_interval(self.update, 1 / FPS)

            if not MOBILE_MODE:
                # Create the keyboard to move the character
                self._keyboard = Window.request_keyboard(
                    self._keyboard_closed, self, 'text')
                self._keyboard.bind(on_key_down=self.update_on_key_down)
                self._keyboard.bind(on_key_up=self.update_on_key_up)

            self.list_keydown = []
            self.list_keyup = []

            # Create the joystick to move the character
            if MOBILE_MODE:
                my_layout_joystick = RelativeLayout()
                self.add_widget(my_layout_joystick)
                self.mobile_joystick = MobileJoystick(my_layout_joystick)

                my_layout_button = RelativeLayout()
                self.add_widget(my_layout_button)
                self.mobile_button = MobileButton(my_layout_button)

                self.darkness_circle.change_radius(
                    self.darkness_circle.radius + START_BEACON_CASES)

    ##################################
    ### Controls with the keyboard ###
    ##################################

    def update_on_key_down(self, keyboard, keycode, text, modifiers):
        """
        Update the the list of keys pressed when the key is down.

        Parameters
        ----------
        keyboard

        keycode: int
            Integer representing the key pressed by the user

        text

        modifiers

        Returns
        -------
        None
        """
        return self.update_list_keydown("keydown", keycode)

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
        if keycode[1] in self.DICT_KEYS.values():
            self.list_keyup.append(keycode[1])
        return self.update_list_keydown("keyup", keycode)

    def update_list_keydown(self, action, keycode):
        """
        Update the list of keys pressed by the user.

        Parameters
        ----------
        action: Literal["keydown", "keyup"]
            String to explain how is pressed the key

        keycode: int
            Integer representing the key pressed by the user

        Returns
        -------
        None
        """
        key = keycode[1]
        if action == "keydown" and not (key in self.list_keydown):
            self.list_keydown.append(key)
        if action == "keyup" and key in self.list_keydown:
            self.list_keydown.remove(key)

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
        self._keyboard.unbind(on_key_down=self.update_on_key_down)
        self._keyboard.unbind(on_key_up=self.update_on_key_up)
        self._keyboard = None

    def get_movements_keyboard(self):
        """
        Extract the movement entered by the user to move the character.
        It only takes into account the movements with the keyboard.

        Parameters
        ----------
        None

        Returns
        -------
        x_movement: float
            Movement on the x axis

        y_movement: float
            Movement on the y axis
        """
        x_movement = 0
        y_movement = 0
        for key in self.list_keydown:
            for movement in self.DICT_KEYS:
                if key.lower() == self.DICT_KEYS[movement]:
                    if movement == "top":
                        y_movement = 1
                    if movement == "bottom":
                        y_movement = -1
                    if movement == "right":
                        x_movement = 1
                    if movement == "left":
                        x_movement = -1
        if x_movement != 0 and y_movement != 0:
            x_movement = x_movement / SQUARE_TWO
            y_movement = y_movement / SQUARE_TWO
        return x_movement, y_movement

    ######################
    ### General udpate ###
    ######################

    def update(self, *args):

        # Block the game update if the game is over
        if self.is_game_over:
            self.game_over()
            return

        # Get the last movements of the character
        if MOBILE_MODE:
            x_movement, y_movement = self.mobile_joystick.get_direction()
            self.mobile_joystick.draw()
        else:
            x_movement, y_movement = self.get_movements_keyboard()

        # Get the interactions with the buttons
        if MOBILE_MODE:
            if self.mobile_button.get_state():
                self.list_keyup = [self.INTERACT_KEY]
            self.mobile_button.draw()

        if DEBUG_MODE and self.count_frame % 60 == 0:
            self.fps_label.text = str(round(Clock.get_fps(), 2))

        # Increase the frame counter
        self.count_frame += 1

        # Decrease the intensity of the beacon
        self.beacon_life -= self.rate_diminution_light
        self.progress_bar_beacon.value = self.beacon_life
        if self.beacon_life < 0:
            self.grid_map.set_tile_type(
                position=(floor(self.beacon_position[0]), floor(
                    self.beacon_position[1])),
                value="R")
            self.darkness_circle.change_radius(0)

        # Manage crystal sound
        current_map_center_grid_pos = self.get_map_center_grid_pos()

        if self.prec_map_center_grid_pos != current_map_center_grid_pos:
            self.is_crystal_near = self.search_near_crystal(
                current_map_center_grid_pos)
            self.is_beacon_near = self.search_near_off_beacon(
                current_map_center_grid_pos)
            self.manage_near_beacon_sound()
            self.manage_near_crystal_sound()

        # Update the position of the character on the map
        self.update_char_on_map_position(
            x_movement=x_movement,
            y_movement=y_movement)

        # Get the interactions of the character with the environment
        self.manage_in_darkness()
        self.interact_with_environment()
        self.update_darkness_position()

        self.update_map_on_screen_position()
        self.update_char_on_screen_position()

        self.redraw_interface()

        sound_mixer.recursive_update()
        # Play randomly the water drops
        if rd.random() < PROBABILITY_WATER_DROPS:
            if sound_mixer.musics["flic"].state != "play":
                sound_mixer.play("flic", stop_other_sounds=False)


#################
### Functions ###
#################


def load_grid_map(filename: str):
    """
    Load a map from a file.

    Parameters
    ----------
    filename: str
        Path of the file to load

    Returns
    -------
    grid_map: list[list[str]]
        Map with letters discribing each tile
    """

    # Read the file
    with open(PATH_MAPS + filename + ".txt", mode="r", encoding="utf-8") as file:
        lines = file.readlines()

    # Create the grid map
    grid_map = []

    for line in lines:
        # Clean new lines
        line = line.replace("\n", "")

        # If line is not empty
        if line.replace(" ", "") != "":

            # Clean double spaces
            line = line.replace("  ", " ")

            # Remove last character if space
            if line[-1] == " ":
                line = line[:-1]

            # Remove first character if space
            if line[0] == " ":
                line = line[1:]

            # Split on spaces
            tiles = line.split(" ")

            # Add the tiles to the grid map
            grid_map.append(tiles)

    return grid_map


def load_texture(image_file):
    """
    Load a texture and create an Image widget in Kivy.

    Parameters
    ----------
    image_file: str
        Name of the image

    Returns
    -------
    None
    """
    texture = Image(source=image_file).texture
    texture.mag_filter = "nearest"
    return texture


def load_textures_from_atlas(atlas_name: str):
    """
    Load the textures in the atlas, given the name of the atlas.

    Parameters
    ----------
    atlas_name: str
        Name of the atlas

    Returns
    -------
    None
    """

    # Set the global path for the atlas and open it
    path_atlas = PATH_ATLAS + atlas_name + ".atlas"
    atlas = Atlas(path_atlas)

    # Extract the textures from the atlas
    dict_textures = {}
    for texture in atlas.original_textures:
        texture.mag_filter = "nearest"
    for key in atlas.textures:
        dict_textures[key] = atlas[key]

    return dict_textures


###############
### Process ###
###############

TEXTURE_DICT = load_textures_from_atlas("map_textures")
# TEXTURE_DICT["hero"] = load_texture(PATH_CHARACTER_IMAGES + "front.png")
TEXTURE_DICT["blank"] = load_texture(PATH_IMAGES + "blank.png")
TEXTURE_DICT.update(load_textures_from_atlas("ghost_textures"))
