import os

from math import ceil, sqrt

from PIL import Image as PIL_Image

from tools.tools_constants import PATH_ATLAS, DICT_TILES_TEXTURE, PATH_MAP_TEXTURES, PATH_CHARACTER_IMAGES

from tools.tools_basis import save_json_file

from tools.tools_map import create_new_map, grid_to_string

from tools.tools_world_explorer import load_grid_map


def create_atlas_from_folder(folder_path: str, rescale_size: tuple = None) -> None:
    """
    Create an atlas with pictures contained in a folder.

    Parameters
    ----------
    folder_path: str
        Path to the folder containing the images

    rescale_size: (int, int)
        Rescale the images

    Returns
    -------
    None
    """

    # Get the list of files in the folder
    file_list = os.listdir(folder_path)
    atlas_name = os.path.basename(folder_path[:-1])
    atlas_texture_name = atlas_name + ".png"

    # Compute variables to define the atlas
    nb_pictures = len(file_list)
    nb_textures_on_side = ceil(sqrt(nb_pictures))
    if rescale_size is None:
        image = PIL_Image.open(folder_path + file_list[0])
        rescale_size = image.size[0]

    # Create the atlas texture
    atlas_side = rescale_size * nb_textures_on_side
    atlas_size = (atlas_side,
                  atlas_side)
    atlas_texture = PIL_Image.new(mode="RGBA",
                                  size=atlas_size)

    # Create the atlas dict
    atlas_dict = {atlas_texture_name: {}}

    # Create the atlas
    for i, file in enumerate(file_list):

        # Extract the name of the file
        file_name = file.split(".")[0]

        # Open the image
        image = PIL_Image.open(folder_path + file)
        image = image.resize((rescale_size, rescale_size))

        # Compute its coordinates
        x_coord = (i % nb_textures_on_side) * rescale_size
        y_coord = (i // nb_textures_on_side) * rescale_size
        texture_box_PIL = [x_coord, y_coord, rescale_size, rescale_size]
        texture_box_atlas = [x_coord,
                             atlas_side - y_coord - rescale_size, rescale_size, rescale_size]
        atlas_texture.paste(image,
                            texture_box_PIL[:2])

        # Add the texture to the atlas
        atlas_dict[atlas_texture_name][file_name] = texture_box_atlas

    # Save the atlas
    atlas_texture.save(PATH_ATLAS + atlas_name + ".png")
    save_json_file(PATH_ATLAS + atlas_name + ".atlas", atlas_dict)


def create_map_single_image(grid_map, tile_size, image_folder_path):
    """
    Create the map in png to visualize it quickly.
    """
    x_size = len(grid_map[0])
    y_size = len(grid_map)
    map_size = ((x_size) * tile_size, (y_size) * tile_size)
    map_texture = PIL_Image.new(mode="RGBA",
                                size=map_size)

    for x in range(x_size):
        for y in range(y_size):
            image = PIL_Image.open(image_folder_path +
                                   DICT_TILES_TEXTURE[grid_map[y][x]] + ".png")
            image = image.resize((tile_size, tile_size))

            image_box = [x * tile_size,
                         y * tile_size, tile_size, tile_size]

            map_texture.paste(image, box=image_box[:2])

    map_texture.save("map.png")


create_atlas_from_folder(folder_path=PATH_MAP_TEXTURES, rescale_size=100)
create_atlas_from_folder(folder_path=PATH_CHARACTER_IMAGES, rescale_size=100)

# grid_map = create_new_map(True, [])
# # # grid_map = load_grid_map("magic_forest")
# # create_map_single_image(grid_map, 50, PATH_MAP_TEXTURES)
# print(grid_to_string(grid_map))
