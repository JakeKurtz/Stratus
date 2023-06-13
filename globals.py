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

global WORLD_SHADER_NAME
WORLD_SHADER_NAME = "STRATUS_WORLD_SHADER"

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

global MAX_TEXTURE_SIZE
max_tex_size = bgl.Buffer(bgl.GL_INT, [1])
bgl.glGetIntegerv(bgl.GL_MAX_TEXTURE_SIZE, max_tex_size)
MAX_TEXTURE_SIZE = max_tex_size[0]

global ENV_IMG_SIZE
ENV_IMG_SIZE = []

env_img_size = [
    ('1',   "1K",   '1024 x 512',    '', 1),
    ('2',   "2K",   '2048 x 1024',   '', 2),
    ('4',   "4K",   '4096 x 2048',   '', 4),
    ('8',   "8K",   '8192 x 4096',   '', 8),
    ('16',  "16K",  '16384 x 8192',  '', 16),
    ('24',  "24K",  '24576 x 12288', '', 24),
]

for size in env_img_size:
    if (int(size[4])*1024) >= MAX_TEXTURE_SIZE:
        break
    else:
        ENV_IMG_SIZE.append(size)

global TILE_SIZE
TILE_SIZE = []

tile_size = [
    ('0', "128",  '128 x 128',   '', 128),
    ('1', "256",  '256 x 256',   '', 256),
    ('2', "512",  '512 x 512',   '', 512),
    ('3', "1024", '1024 x 1024', '', 1024),
    ('4', "2048", '2048 x 2048', '', 2048),
    ('5', "4096", '4096 x 4096', '', 4096),
]

for size in tile_size:
    if int(size[4]) >= MAX_TEXTURE_SIZE:
        break
    else:
        TILE_SIZE.append(size)

global SHADER
SHADER = {}
global BATCH
BATCH = {}

global LAST_FRAME
LAST_FRAME = 0

global CURRENT_FRAME
CURRENT_FRAME = 0

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

global VIEWPORT_RUNNING
VIEWPORT_RUNNING = False

global KILL_VIEWPORT
KILL_VIEWPORT = False

# ----------------------------------- Icons ---------------------------------- #

global ICONS
ICONS = None

global CIRR_ICON
CIRR_ICON = 0

global CUMU_ICON
CUMU_ICON = 0

global CELE_ICON
CELE_ICON = 0