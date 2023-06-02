# ------------------------------------------------------------------------- #
#
#    Copyright (C) 2023 Jake Kurtz
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# ------------------------------------------------------------------------- #

import bpy

from ... import globals
from .general_utils import new_offscreen_fbo

class ENVImage:
    _width = 1024
    _height = 512

    _max_img_size = 24

    _grid_width = 0
    _grid_height = 0

    _tile_size = 0
    _tile_id = 0
    _nmb_of_tiles = 0

    _tiling_enabled = True

    _offscreen = None
    _name = None

    _img_buff = []

    def __init__(self, name):
        self._name = name
        if self._name not in bpy.data.images:
            bpy.data.images.new(
                self._name, 
                self._width, 
                self._height, 
                alpha=True, 
                float_buffer=True)
        self._offscreen = new_offscreen_fbo(self._width, self._height)
        self.set_tile_size(512)

        self._max_img_size = int(float(globals.MAX_TEXTURE_SIZE) / 1024.0) 

    def __del__(self):
        self._offscreen.free()
    
    def _init_tile_props(self):
        self._grid_width = int(self._width / self._tile_size)
        self._grid_height = int(self._height / self._tile_size) 
        self._nmb_of_tiles = int(self._grid_width * self._grid_height)

    def set_size(self, size):
        assert type(size) == int or float, "size should be a number, i.e. int or float."
        assert (size >= 0.25 and size <= 24.0), "size should be between the values 0.25 and 24.0"
        
        if (size >= self._max_img_size): 
            size = self._max_img_size

        self._width = int(1024.0 * float(size))
        self._height = int(512.0 * float(size))

        if self._offscreen is not None:
            self._offscreen.free()
        self._offscreen = new_offscreen_fbo(self._width, self._height)

        self._init_tile_props()

    def get_size(self):
        return (self._width, self._height)

    def enable_tiling(self):
        self._tiling_enabled = True

    def disable_tiling(self):
        self._tiling_enabled = False

    def use_tiling(self):
        valid_tile_size = (self._tile_size <= self._width and self._tile_size <= self._height)
        return valid_tile_size and self._tiling_enabled

    def set_tile_size(self, tile_size):
        self._tile_size = tile_size
        self._init_tile_props()

    def get_tile_size(self):
        return self._tile_size

    def get_tile_pos(self):
        if (self.use_tiling()):
            tile_x = int(self._tile_id % self._grid_width)
            tile_y = int(self._tile_id / self._grid_width)
            return (tile_x, tile_y)
        else:
            return (0,0)

    def get_offscreen(self):
        return self._offscreen

    def increment_tile(self):
        if not self.completed():
            self._tile_id += 1

    def completed(self):
        if self.use_tiling():
            return (self._tile_id >= self._nmb_of_tiles)
        else:
            return True
    
    def reset(self):
        self._tile_id = 0

    def save(self):
        self._img_buff = self._offscreen.texture_color.read()
        self._img_buff.dimensions = self._width * self._height * 4

        bpy.data.images[self._name].scale(self._width, self._height)
        bpy.data.images[self._name].pixels.foreach_set(self._img_buff)
    
    def save_to_disk(self, context, filename):
        prop = context.scene.render_props

        scene = bpy.data.scenes.new("STRATUS_TMP_SCENE")
        
        settings = scene.render.image_settings

        settings.color_management = 'FOLLOW_SCENE'
        settings.file_format = prop.file_format
        settings.color_mode = prop.color_mode
        settings.exr_codec = prop.exr_codec

        self._img_buff = self._offscreen.texture_color.read()
        self._img_buff.dimensions = self._width * self._height * 4

        extension = '.exr' if (prop.file_format in {'OPEN_EXR', 'OPEN_EXR_MULTILAYER'}) else '.hdr'
        
        bpy.data.images[self._name].filepath = prop.file_path+filename+extension
        bpy.data.images[self._name].file_format = prop.file_format

        bpy.data.images[self._name].scale(self._width, self._height)
        bpy.data.images[self._name].pixels.foreach_set(self._img_buff)

        bpy.data.images[self._name].save_render(prop.file_path+filename+extension, scene=scene)

        print(prop.file_path+filename+extension)

        bpy.data.scenes.remove(scene)
        

