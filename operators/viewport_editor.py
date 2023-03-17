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
import gpu
import bgl
import ctypes

from mathutils import Matrix

from .. import globals
from .utils.env_img_utils import ENVImage
from .utils.init_utils import init_shaders, init_textures
from .utils.general_utils import new_offscreen_fbo, bgl_uniform_sampler, refresh_viewers
from .utils.draw_utils import draw_env_img, draw_irra_map
from .utils.shader_utils import atmo_uniforms, cloud_uniforms, moon_uniforms, sun_uniforms

def pre_draw_viewport(self, context, irra_tex):

    cloud_prop = context.scene.cloud_props
    atmo_prop = context.scene.atmo_props 
    sun_prop = context.scene.sun_props  
    moon_prop = context.scene.moon_props
    render_prop = context.scene.render_props
    
    scr_width = context.region.width
    scr_height = context.region.height

    tex_width = int(float(scr_width)/float(render_prop.viewport_pixel_size))       
    tex_height = int(float(scr_height)/float(render_prop.viewport_pixel_size))
    
    with self._offscreen_viewport.bind():
        gpu.state.depth_test_set('NONE')
        _shader = globals.SHADER["viewport"]

        _shader.bind()

        proj_mat = context.region_data.perspective_matrix
        
        inv_vp_mat = proj_mat
        inv_vp_mat = inv_vp_mat.inverted()
        
        _shader.uniform_float("img_size", (tex_width, tex_height))
        
        _shader.uniform_float("inv_vp_mat", inv_vp_mat)      
        _shader.uniform_int("cld_max_steps", render_prop.max_steps_viewport)
        _shader.uniform_int("cld_max_light_steps", render_prop.max_light_steps_viewport)

        _shader.uniform_float("altitude", atmo_prop.prop_sky_altitude)

        _shader.uniform_int("enable_atm", atmo_prop.atm_show_viewport)
        _shader.uniform_int("enable_cld", cloud_prop.cld_show_viewport)
        _shader.uniform_int("enable_moon", moon_prop.moon_show_viewport)
        _shader.uniform_int("enable_sun", sun_prop.sun_show_viewport)

        atmo_uniforms(_shader)
        cloud_uniforms(_shader)
        moon_uniforms(_shader)
        sun_uniforms(_shader)

        bgl_uniform_sampler(_shader, "irra_tex", irra_tex, 2, 6)
 
        globals.BATCH["viewport"].draw(_shader)

def post_draw_viewport(self, context):
    scene = context.scene
    prop = scene.render_props

    r3d = context.area.spaces.active.region_3d

    if r3d.view_perspective == 'CAMERA':
        obj_camera = bpy.context.scene.camera
        clip_end = obj_camera.data.clip_end
    else:
        clip_end = context.area.spaces.active.clip_end
    
    trans = Matrix.Translation(r3d.view_matrix.inverted().translation)
    scale = Matrix.Scale((clip_end*0.9)*.5, 4)
    
    obj_mat = trans @ scale

    proj_view_mat = bpy.context.region_data.perspective_matrix

    monitor_width = ctypes.windll.user32.GetSystemMetrics(0)
    monitor_height = ctypes.windll.user32.GetSystemMetrics(1)    
    
    scr_width = context.region.width
    scr_height = context.region.height

    tex_width = int(float(scr_width)/float(prop.viewport_pixel_size))       
    tex_height = int(float(scr_height)/float(prop.viewport_pixel_size))

    gpu.state.depth_test_set('LESS')

    _shader = globals.SHADER["screen"]
    _shader.bind()

    _shader.uniform_float("projection", proj_view_mat @ obj_mat)

    _shader.uniform_float("monitor_size", (monitor_width, monitor_height))
    _shader.uniform_float("scr_size", (scr_width, scr_height))
    _shader.uniform_float("tex_size", (tex_width, tex_height))
    _shader.uniform_float("gamma", scene.view_settings.gamma)
    _shader.uniform_float("env_img_strength", prop.env_img_strength)

    bgl_uniform_sampler(_shader, "tex", self._offscreen_viewport.color_texture, 2, 0)

    globals.BATCH["screen"].draw(_shader)

    gpu.state.depth_test_set('NONE')

class STRATUS_OT_viewport_editor(bpy.types.Operator):
    bl_idname = "stratus.viewport_editor"
    bl_label = "Stratus Viewport Editor"

    _offscreen_viewport = None
    _offscreen_sky = None
    _offscreen_irra = None

    _handle_draw = None
    _is_enabled = False
    _enable_previewer = True

    _env_img = None

    # manage draw handler
    def post_draw_callback(self, context):
        if context.scene.render_props.enable_previewer: 
            post_draw_viewport(self, context)

    def pre_draw_callback(self, context):
        prop = context.scene.render_props

        irra_tex = self._offscreen_irra.color_texture

        if globals.RESIZE_ENV_IMG:
            size = prop.env_img_viewport_size
            self._env_img.set_size(float(size))
            globals.RESIZE_ENV_IMG = False

        if globals.RESET_ENV_IMG:
            self._env_img.reset()
            globals.RESET_ENV_IMG = False

        if ((globals.DRAW_ENV_IMG and not globals.BAKE_ENV_IMG) or prop.enable_previewer):
            draw_irra_map(self._offscreen_sky, self._offscreen_irra, 'VIEWPORT')

        if globals.DRAW_ENV_IMG and not globals.BAKE_ENV_IMG:
            draw_env_img(self._env_img, irra_tex, 'VIEWPORT')
            
            if self._env_img.completed():
                globals.DRAW_ENV_IMG = False
                globals.REFRESH_VIEWPORT = True
                self._env_img.save()
                self._env_img.reset()

        if prop.enable_previewer:
            pre_draw_viewport(self, context, irra_tex)

    def handle_add(self, context):
        STRATUS_OT_viewport_editor._handle_draw = bpy.types.SpaceView3D.draw_handler_add(
                self.post_draw_callback, (self, context),
                'WINDOW', 'POST_VIEW',
                )

        STRATUS_OT_viewport_editor._handle_draw = bpy.types.SpaceView3D.draw_handler_add(
                self.pre_draw_callback, (self, context),
                'WINDOW', 'PRE_VIEW',
                )

    def handle_remove():
        if STRATUS_OT_viewport_editor._handle_draw is not None:
            bpy.types.SpaceView3D.draw_handler_remove(STRATUS_OT_viewport_editor._handle_draw, 'WINDOW')

        STRATUS_OT_viewport_editor._handle_draw = None

    def init_world_node_tree(self):
        C = bpy.context
        scn = C.scene

        # Get the environment node tree of the current scene
        node_tree = scn.world.node_tree
        tree_nodes = node_tree.nodes

        # Clear all nodes
        tree_nodes.clear()

        # Add Background node
        node_background = tree_nodes.new(type='ShaderNodeBackground')
        node_background.inputs["Strength"].default_value = 0.1

        # Add Environment Texture node
        node_environment = tree_nodes.new('ShaderNodeTexEnvironment')
        # Load and assign the image to the node property
        node_environment.image = bpy.data.images[globals.IMG_NAME]
        node_environment.interpolation = 'Smart'
        node_environment.location = -300,0

        # Add Output node
        node_output = tree_nodes.new(type='ShaderNodeOutputWorld')   
        node_output.location = 200,0

        # Link all nodes
        links = node_tree.links
        link = links.new(node_environment.outputs["Color"], node_background.inputs["Color"])
        link = links.new(node_background.outputs["Background"], node_output.inputs["Surface"])
        
    # operator functions
    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if globals.REFRESH_VIEWPORT:
            refresh_viewers(context)
            globals.REFRESH_VIEWPORT = False

        if event.type in {'ESC'}:
            #bpy.types.SpaceView3D.draw_handler_remove(self._handle_3d, 'WINDOW')
            #context.scene.my_tool.enable_previewer = False 
            #self.tag_redraw()
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if STRATUS_OT_viewport_editor._is_enabled:
            self.cancel(context)
            return {'FINISHED'}
        else:
            # Initialize textures, if they havent already
            init_textures()
            # Initialize shaders, if they havent already
            init_shaders()

            self._env_img = ENVImage(globals.IMG_NAME)

            STRATUS_OT_viewport_editor.init_world_node_tree(self)

            monitor_width = ctypes.windll.user32.GetSystemMetrics(0)
            monitor_height = ctypes.windll.user32.GetSystemMetrics(1)

            self._offscreen_viewport = new_offscreen_fbo(monitor_width, monitor_height)
            self._offscreen_sky = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)
            self._offscreen_irra = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)

            bgl.glBindTexture(bgl.GL_TEXTURE_2D, self._offscreen_viewport.color_texture)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MIN_FILTER, bgl.GL_NEAREST)
            bgl.glTexParameteri(bgl.GL_TEXTURE_2D, bgl.GL_TEXTURE_MAG_FILTER, bgl.GL_NEAREST)
            bgl.glBindTexture(bgl.GL_TEXTURE_2D, 0)
            
            if not (self._offscreen_viewport and self._offscreen_sky and self._offscreen_irra):
                self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
                return {'CANCELLED'}

            STRATUS_OT_viewport_editor.handle_add(self, context)
            STRATUS_OT_viewport_editor._is_enabled = True

            if context.area:
                context.area.tag_redraw()

            context.window_manager.modal_handler_add(self)
            
            return {'RUNNING_MODAL'}

    def cancel(self, context):
        STRATUS_OT_viewport_editor.handle_remove()
        STRATUS_OT_viewport_editor._is_enabled = False

        if context.area:
            context.area.tag_redraw()