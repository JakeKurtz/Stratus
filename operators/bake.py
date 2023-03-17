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
from .utils.draw_utils import draw_env_img, draw_irra_map

class STRATUS_OT_bake_env_img(bpy.types.Operator):
    bl_idname = "stratus.bake_env_img"
    bl_label = "Stratus Bake"

    _offscreen_sky = None
    _offscreen_irra = None

    _env_img = None

    def invoke(self, context, event):
        globals.BAKE_ENV_IMG = True
        # Initialize, if you havent already
        init_textures()
        init_shaders()
        init_world_node_tree()

        prop = context.scene.render_props
        size = float(prop.env_img_render_size)

        self._env_img = ENVImage(globals.IMG_NAME)
        self._env_img.set_size(size)

        self._offscreen_sky = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)
        self._offscreen_irra = new_offscreen_fbo(globals.IRRA_WIDTH, globals.IRRA_HEIGHT)

        if not (self._offscreen_sky and self._offscreen_irra):
            self.report({'ERROR'}, "Error initializing offscreen buffer. More details in the console")
            return {'CANCELLED'}

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self._env_img.completed():
            print("Bake Finished.")
            refresh_viewers(context)
            globals.BAKE_ENV_IMG = False
            self._env_img.save()
            self._env_img.reset()
            return {'FINISHED'}

        draw_irra_map(self._offscreen_sky, self._offscreen_irra, 'RENDER')
        irra_tex = self._offscreen_irra.color_texture
        draw_env_img(self._env_img, irra_tex, 'RENDER')

        return {'PASS_THROUGH'}