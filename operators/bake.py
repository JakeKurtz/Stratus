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
import functools
from datetime import datetime

from .. import globals
from .utils.env_img_utils import ENVImage
from .utils.init_utils import init_shaders, init_textures, init_world_node_tree
from .utils.general_utils import new_offscreen_fbo, refresh_viewers
from .utils.draw_utils import draw_env_img, draw_irra_map

class STRATUS_OT_bake_env_img(bpy.types.Operator):
    bl_idname = "stratus.bake_env_img"
    bl_label = "Stratus Bake"

    _offscreen_sky = None
    _offscreen_irra = None

    _env_img = None

    _start_time = 0

    _is_enabled = False
    _bake_done = False
    _handle_pre_draw = None

    _timer = None

    @staticmethod
    def _pre_draw_callback(self, context):
        draw_irra_map(self._offscreen_sky, self._offscreen_irra, 'RENDER')
        irra_tex = self._offscreen_irra.color_texture
        draw_env_img(self._env_img, irra_tex, 'RENDER')
        self._bake_done = self._env_img.completed()

    @staticmethod
    def _handle_add(self, context):
        self._handle_pre_draw = bpy.types.SpaceView3D.draw_handler_add(
                self._pre_draw_callback, (self, context),
                'WINDOW', 'PRE_VIEW',
                )

    @staticmethod
    def _handle_remove(self):
        if self._handle_pre_draw is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle_pre_draw, 'WINDOW')        

        self._handle_pre_draw = None

    def invoke(self, context, event):
        if STRATUS_OT_bake_env_img._is_enabled:
            return {'FINISHED'}
        else:
            globals.BAKE_ENV_IMG = True

            prop = context.scene.render_props
            size = float(prop.env_img_render_size)

            self._env_img = ENVImage(globals.IMG_NAME)
            self._env_img.set_size(size)
            
            # Initialize, if you havent already
            init_textures(self)
            init_shaders(self)
            init_world_node_tree(self)
    
            if prop.enable_tiling:
                i = int(prop.render_tile_size)
                tile_size = prop.tile_size[i][4]
                self._env_img.enable_tiling()
                self._env_img.set_tile_size(tile_size)
            else:
                self._env_img.disable_tiling()

            self._offscreen_sky = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)
            self._offscreen_irra = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)

            if not (self._offscreen_sky and self._offscreen_irra):
                self.report({'ERROR'}, "STRATUS: error initializing offscreen buffer. More details in the console")
                return {'CANCELLED'}


            STRATUS_OT_bake_env_img._handle_add(self, context)
            STRATUS_OT_bake_env_img._is_enabled = True

            self.report({'INFO'}, "STRATUS: baking "+prop.env_img_render_size+"K texture.")
            self._start_time = datetime.now()

            self._timer = context.window_manager.event_timer_add(0.016, window=context.window)
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type == 'TIMER':
            if self._bake_done:
                globals.BAKE_ENV_IMG = False
                self._env_img.save()
                self._env_img.reset()

                refresh_viewers(context)

                end_time = datetime.now()
                duration = end_time - self._start_time
                s = duration.total_seconds()

                self.report({'INFO'}, "STRATUS: bake completed. Took "+'{:02.0f}:{:05.2f}'.format(s % 3600 // 60, s % 60))
                self.clean_up(context)

                return {'FINISHED'}
        return {'PASS_THROUGH'}
    
    def clean_up(self, context):
        STRATUS_OT_bake_env_img._handle_remove(self)
        STRATUS_OT_bake_env_img._is_enabled = False

        self._offscreen_sky.free()
        self._offscreen_irra.free()

        context.window_manager.event_timer_remove(self._timer)