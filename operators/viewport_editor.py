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

from .. import globals
from .utils.env_img_utils import ENVImage
from .utils.init_utils import init_shaders, init_textures, init_world_node_tree
from .utils.general_utils import new_offscreen_fbo, refresh_viewers
from .utils.draw_utils import draw_env_img, draw_irra_map, pre_draw_viewport, post_draw_viewport, update_viewport_offscreen

class STRATUS_OT_viewport_editor(bpy.types.Operator):
    bl_idname = "stratus.viewport_editor"
    bl_label = "Stratus Viewport Editor"

    _fbo_viewport = None
    _viewport_texture = None

    _offscreen_viewport = None
    _offscreen_sky = None
    _offscreen_irra = None

    _scr_width = 0
    _scr_height = 0

    _handle_pre_draw = None
    _handle_post_draw = None
    _is_enabled = False

    _env_img = None

    # manage draw handler
    @staticmethod
    def _post_draw_callback(self, context):
        overlay_enabled = context.area.spaces[0].overlay.show_overlays
        if overlay_enabled:
            post_draw_viewport(self, context)

    @staticmethod
    def _pre_draw_callback(self, context):
        prop = context.scene.render_props

        overlay_enabled = context.area.spaces[0].overlay.show_overlays

        irra_tex = self._offscreen_irra.color_texture

        if globals.RESIZE_ENV_IMG:
            size = prop.env_img_viewport_size
            self._env_img.set_size(float(size))
            globals.RESIZE_ENV_IMG = False

        if globals.RESET_ENV_IMG:
            self._env_img.reset()
            globals.RESET_ENV_IMG = False

        if ((globals.DRAW_ENV_IMG and not globals.BAKE_ENV_IMG) or overlay_enabled):
            draw_irra_map(self._offscreen_sky, self._offscreen_irra, 'VIEWPORT')

        if globals.DRAW_ENV_IMG and not globals.BAKE_ENV_IMG:
            draw_env_img(self._env_img, irra_tex, 'VIEWPORT')
            
            if self._env_img.completed():
                globals.DRAW_ENV_IMG = False
                globals.REFRESH_VIEWPORT = True
                self._env_img.save()
                self._env_img.reset()

        if overlay_enabled:
            pre_draw_viewport(self, context, irra_tex)

    @staticmethod
    def _handle_add(self, context):
        self._handle_post_draw = bpy.types.SpaceView3D.draw_handler_add(
                self._post_draw_callback, (self, context),
                'WINDOW', 'POST_VIEW',
                )

        self._handle_pre_draw = bpy.types.SpaceView3D.draw_handler_add(
                self._pre_draw_callback, (self, context),
                'WINDOW', 'PRE_VIEW',
                )

    @staticmethod
    def _handle_remove(self):
        if self._handle_pre_draw is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_pre_draw, 'WINDOW')        
        if self._handle_post_draw is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_post_draw, 'WINDOW')

        self._handle_pre_draw = None
        self._handle_post_draw = None
        
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
            self.clean_up(context)
            return {'FINISHED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if STRATUS_OT_viewport_editor._is_enabled:
            return {'FINISHED'}
        else:
            prop = context.scene.render_props
            size = float(prop.env_img_viewport_size)

            self._env_img = ENVImage(globals.IMG_NAME)
            self._env_img.set_size(size)

            # Initialize, if you havent already
            init_textures(self)
            init_shaders(self)
            init_world_node_tree(self)

            update_viewport_offscreen(self, context)
        
            self._offscreen_sky = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)
            self._offscreen_irra = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)
            
            if not (self._offscreen_viewport and self._offscreen_sky and self._offscreen_irra):
                self.report({'ERROR'}, "STRATUS: error initializing offscreen buffer. More details in the console")
                return {'CANCELLED'}

            STRATUS_OT_viewport_editor._handle_add(self, context)
            STRATUS_OT_viewport_editor._is_enabled = True

            context.window_manager.modal_handler_add(self)

            globals.DRAW_ENV_IMG = True
            
            return {'RUNNING_MODAL'}

    def clean_up(self, context):
        STRATUS_OT_viewport_editor._handle_remove(self)
        STRATUS_OT_viewport_editor._is_enabled = False

        self._offscreen_viewport.free()
        self._offscreen_sky.free()
        self._offscreen_irra.free()

        if context.area:
            context.area.tag_redraw()