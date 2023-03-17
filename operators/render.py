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
from .utils.init_utils import init_shaders, init_textures
from .utils.general_utils import new_offscreen_fbo
from .utils.draw_utils import draw_env_img, draw_irra_map

class STRATUS_OT_render(bpy.types.Operator):
    bl_idname = "stratus.render_env_img"
    bl_label = "Stratus Render HRDI"

    _offscreen_sky = None
    _offscreen_irra = None

    _env_img = None

    def invoke(self, context, event):
        # Initialize textures, if they havent already
        init_textures()
        # Initialize shaders, if they havent already
        init_shaders()

        prop = context.scene.render_props
        size = int(prop.env_img_render_size)

        self._env_img = ENVImage(globals.IMG_NAME)
        self._env_img.set_size(size)

        self._offscreen_sky = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)
        self._offscreen_irra = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)

        if not (self._offscreen_sky and self._offscreen_irra):
            self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
            return {'CANCELLED'}

        return self.execute(context)

    def execute(self, context):
        scene = context.scene
        fp = scene.render.filepath

        for frame in range(scene.frame_start, scene.frame_end + 1):
            scene.frame_set(frame)
            scene.render.filepath = fp + str(frame).zfill(4)

            start_time = datetime.now()

            draw_irra_map(self._offscreen_sky, self._offscreen_irra, 'RENDER')
            while(not self._env_img.completed()):
                irra_tex = self._offscreen_irra.color_texture
                draw_env_img(self._env_img, irra_tex, 'RENDER')
            self._env_img.save()
            self._env_img.reset()

            end_time = datetime.now()

            bpy.ops.render.render(write_still=True) 

            duration = end_time - start_time
            s = duration.total_seconds()
            print(" STRATUS Time: "+'{:02.0f}:{:05.2f}'.format(s % 3600 // 60, s % 60)+"\n")

        scene.render.filepath = fp

        return {'FINISHED'}