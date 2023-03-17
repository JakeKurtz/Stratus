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

class STRATUS_OT_prop_observer(bpy.types.Operator):
    bl_idname = "stratus.prop_observer"
    bl_label  = ""

    _timer = None
    _stop = False
    def invoke(self, context, event):
            wm = context.window_manager
            self._timer = wm.event_timer_add(0.016, window=context.window)

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if self._stop:
            globals.EDITING_PROP = False
            globals.DRAW_ENV_IMG = True
            return {'FINISHED'}
        
        if event.value == 'RELEASE':
            self._stop = True

        return {'PASS_THROUGH'}