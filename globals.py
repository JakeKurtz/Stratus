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

import bgl

global IMG_NAME
IMG_NAME = "STRATUS_ENV_TEX"

global IRRA_WIDTH
IRRA_WIDTH = 128
global IRRA_HEIGHT
IRRA_HEIGHT = 64

global NMB_NOISE_TEXTURES
NMB_NOISE_TEXTURES = 4

global NMB_MOON_TEXTURES
NMB_MOON_TEXTURES = 2

global NOISE_TEXTURES
NOISE_TEXTURES = bgl.Buffer(bgl.GL_INT, [NMB_NOISE_TEXTURES])
global MOON_TEXTURES
MOON_TEXTURES = bgl.Buffer(bgl.GL_INT, [NMB_MOON_TEXTURES])

global MAX_TEXTURE_IMAGE_UNITS
max_tex_img_units = bgl.Buffer(bgl.GL_INT, [1])
bgl.glGetIntegerv(bgl.GL_MAX_TEXTURE_IMAGE_UNITS, max_tex_img_units)
MAX_TEXTURE_IMAGE_UNITS = max_tex_img_units[0] - 1

global SHADER
SHADER = {}
global BATCH
BATCH = {}

# ----------------------------------- Flags ---------------------------------- #

global INITIALIZED_SHADERS 
INITIALIZED_SHADERS = False

global INITIALIZED_TEXTURES
INITIALIZED_TEXTURES = False

global INITIALIZED_NODE_TREE
INITIALIZED_NODE_TREE = False

global EDITING_PROP
EDITING_PROP = False

global DRAW_ENV_IMG
DRAW_ENV_IMG = False

global BAKE_ENV_IMG
BAKE_ENV_IMG = False

global RESET_ENV_IMG
RESET_ENV_IMG = False

global RESIZE_ENV_IMG
RESIZE_ENV_IMG = False

global REFRESH_VIEWPORT
REFRESH_VIEWPORT = False
