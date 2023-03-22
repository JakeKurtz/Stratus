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
from datetime import datetime

from .. import globals
from .utils.env_img_utils import ENVImage
from .utils.init_utils import init_shaders, init_textures, init_world_node_tree
from .utils.general_utils import new_offscreen_fbo
from .utils.draw_utils import draw_env_img, draw_irra_map

class STRATUS_OT_render_animation (bpy.types.Operator):
    bl_idname = "stratus.render_animation"
    bl_label = "Stratus Render Animation"

    _offscreen_sky = None
    _offscreen_irra = None
    _handle_pre_draw = None
    _current_frame = 0
    _frame_end = 0
    _start_time = None
    _frame_done = False
    _is_enabled = False
    _timer = None
    _render_filepath = None
    _env_img = None

    @staticmethod
    def _pre_draw_callback(self, context):
        draw_irra_map(self._offscreen_sky, self._offscreen_irra, 'RENDER')
        irra_tex = self._offscreen_irra.color_texture
        draw_env_img(self._env_img, irra_tex, 'RENDER')
        self._frame_done = self._env_img.completed()

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
        if STRATUS_OT_render_animation._is_enabled:
            return {'FINISHED'}
        else:
            prop = context.scene.render_props
            size = int(prop.env_img_render_size)

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

            file_format = context.scene.render.image_settings.file_format
            if file_format in {'AVI_JPEG', 'AVI_RAW', 'FFMPEG'}:
                self.report({'ERROR'}, "STRATUS: animation formats AVI_JPEG, AVI_RAW, FFMPEG, are not supported. Please select an image format type.")
                return {'CANCELLED'}

            self._render_filepath = context.scene.render.filepath
            self._current_frame = context.scene.frame_start
            self._frame_end = context.scene.frame_end + 1

            context.scene.frame_set(self._current_frame)
            context.scene.render.filepath = self._render_filepath + str(self._current_frame).zfill(4)
            self._start_time = datetime.now()

            STRATUS_OT_render_animation._handle_add(self, context)
            STRATUS_OT_render_animation._is_enabled = True

            self._timer = context.window_manager.event_timer_add(0.016, window=context.window)
            context.window_manager.modal_handler_add(self)

            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        if event.type in {'ESC'}:
            self.clean_up(context)
            return {'FINISHED'}

        if event.type == 'TIMER':
            if self._frame_done:
                self._env_img.save()
                self._env_img.reset()

                end_time = datetime.now()
                duration = end_time - self._start_time
                s = duration.total_seconds()

                self.report({'INFO'}, "STRATUS: Frame took "+'{:02.0f}:{:05.2f}'.format(s % 3600 // 60, s % 60)+"\n")

                bpy.ops.render.render(write_still=True) 

                scene = context.scene

                self._current_frame += 1
                scene.frame_set(self._current_frame)
                scene.render.filepath = self._render_filepath + str(self._current_frame).zfill(4)

                self._frame_done = False
                self._start_time = datetime.now()

            if (self._current_frame == self._frame_end) or globals.RESET_ENV_IMG:
                self.clean_up(context)
                return {'FINISHED'}

        return {'PASS_THROUGH'}

    def clean_up(self, context):
        STRATUS_OT_render_animation._handle_remove(self)
        STRATUS_OT_render_animation._is_enabled = False

        context.scene.render.filepath = self._render_filepath

        self._offscreen_sky.free()
        self._offscreen_irra.free()

        context.window_manager.event_timer_remove(self._timer)