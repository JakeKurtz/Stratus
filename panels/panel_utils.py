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

def update_prop(self, context):
    if not globals.EDITING_PROP:
        globals.EDITING_PROP = True
        globals.RESET_ENV_IMG = True
        bpy.ops.stratus.prop_observer('INVOKE_DEFAULT')

def update_env_img_size(self, context):
    globals.RESIZE_ENV_IMG = True