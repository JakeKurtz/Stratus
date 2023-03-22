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
import bgl

from ... import globals
from .shader_utils import new_shader
from .general_utils import bgl_texture_from_image, get_dir

def init_world_node_tree(self):
    if globals.INITIALIZED_NODE_TREE is False:
        self.report({'INFO'}, "STRATUS: initializing world node tree.")
        scene = bpy.context.scene
        prop = scene.render_props

        # Get the environment node tree of the current scene
        node_tree = scene.world.node_tree
        nodes = node_tree.nodes

        # Clear all nodes
        nodes.clear()

        # Add Background node
        node_background = nodes.new(type='ShaderNodeBackground')
        node_background.inputs["Strength"].default_value = prop.env_img_strength

        # Add Environment Texture node
        node_environment = nodes.new('ShaderNodeTexEnvironment')
        # Load and assign the image to the node property
        node_environment.image = bpy.data.images[globals.IMG_NAME]
        node_environment.interpolation = 'Smart'
        node_environment.location = -300,0

        # Add Output node
        node_output = nodes.new(type='ShaderNodeOutputWorld')   
        node_output.location = 200,0

        # Link all nodes
        links = node_tree.links
        link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
        link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])

        globals.INITIALIZED_NODE_TREE = True

def init_shaders(self):
    if globals.INITIALIZED_SHADERS is False:
        self.report({'INFO'}, "STRATUS: building shaders.")
        dir = get_dir()

        plane_coords = (
            (-1, +1, 0),
            (+1, +1, 0),
            (-1, -1, 0),
            (+1, -1, 0))        
        plane_indices = ((0,1,2), (1,3,2))

        cube_coords = (
            (-1, -1, -1), (+1, -1, -1),
            (-1, +1, -1), (+1, +1, -1),
            (-1, -1, +1), (+1, -1, +1),
            (-1, +1, +1), (+1, +1, +1))
        cube_indices = (
            (0, 1, 3), (0, 2, 3), (4,5,7), (4,6,7),
            (0,4,5), (0,1,5), (2,0,4), (2,6,4),
            (1,3,7), (1, 5,7), (3, 2, 6), (3, 6, 7))

        # -------------------------------- HRDI Shader ------------------------------- #

        with open(dir+"\\shaders\\vertex_shaders\\stratus_env_img.vert", 'r') as file:
            vertex_shader = file.read()
        with open(dir+"\\shaders\\fragment_shaders\\stratus_env_img.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("env_img", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # -------------------------------- Sky Shader -------------------------------- #

        with open(dir+"\\shaders\\vertex_shaders\\stratus_sky.vert", 'r') as file:
            vertex_shader = file.read()
        with open(dir+"\\shaders\\fragment_shaders\\stratus_sky.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("sky", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # ----------------------------- Irradiance Shader ---------------------------- #

        with open(dir+"\\shaders\\vertex_shaders\\stratus_irra.vert", 'r') as file:
            vertex_shader = file.read()
        with open(dir+"\\shaders\\fragment_shaders\\stratus_irra.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("sky_irra", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # ------------------------------ Viewport Shader ----------------------------- #
        
        with open(dir+"\\shaders\\vertex_shaders\\stratus_viewport.vert", 'r') as file:
            vertex_shader = file.read()
        with open(dir+"\\shaders\\fragment_shaders\\stratus_viewport.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("viewport", vertex_shader, fragment_shader, plane_coords, plane_indices)

        # ------------------------------- Screen Shader ------------------------------ #

        with open(dir+"\\shaders\\vertex_shaders\\stratus_screen.vert", 'r') as file:
            vertex_shader = file.read()
        with open(dir+"\\shaders\\fragment_shaders\\stratus_screen.frag", 'r') as file:
            fragment_shader = file.read()
        new_shader("screen", vertex_shader, fragment_shader, cube_coords, cube_indices)

        globals.INITIALIZED_SHADERS = True

def init_textures(self):
    if globals.INITIALIZED_TEXTURES is False:
        self.report({'INFO'}, "STRATUS: initializing textures.")
        dir = get_dir()

        bgl.glGenTextures(globals.NMB_NOISE_TEXTURES, globals.NOISE_TEXTURES)
        bgl.glGenTextures(globals.NMB_MOON_TEXTURES, globals.MOON_TEXTURES)

        img = bpy.data.images.load(dir+"\\textures\\noise\\noise_tex_64.png", check_existing=True)
        bgl_texture_from_image(img, (64, 64, 64), globals.NOISE_TEXTURES[0])

        img = bpy.data.images.load(dir+"\\textures\\noise\\noise_tex_128.png", check_existing=True)
        bgl_texture_from_image(img, (128, 128, 128), globals.NOISE_TEXTURES[1])
        
        img = bpy.data.images.load(dir+"\\textures\\noise\\noise_tex_2048.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), globals.NOISE_TEXTURES[2])

        img = bpy.data.images.load(dir+"\\textures\\noise\\noise_blue_128.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), globals.NOISE_TEXTURES[3])
        
        img = bpy.data.images.load(dir+"\\textures\\moon\\moon_albedo.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), globals.MOON_TEXTURES[0])

        img = bpy.data.images.load(dir+"\\textures\\moon\\moon_normal.png", check_existing=True)
        bgl_texture_from_image(img, (img.size[0], img.size[1]), globals.MOON_TEXTURES[1])

        globals.INITIALIZED_TEXTURES = True
