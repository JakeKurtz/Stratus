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
from bpy.types import (Panel, PropertyGroup,)
from ..operators.presets import *

class STRATUS_PT_presets(Panel):
    bl_label = "Preset Panel"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        main_prop = scene.main_props
        return main_prop.panels == "PRES"

    def draw(self, context):
        layout = self.layout

        layout.operator(STRATUS_OT_daytime_1.bl_idname, text=STRATUS_OT_daytime_1.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_daytime_2.bl_idname, text=STRATUS_OT_daytime_2.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_daytime_3.bl_idname, text=STRATUS_OT_daytime_3.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_sunset_1.bl_idname, text=STRATUS_OT_sunset_1.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_sunset_2.bl_idname, text=STRATUS_OT_sunset_2.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_sunset_3.bl_idname, text=STRATUS_OT_sunset_3.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_storm.bl_idname, text=STRATUS_OT_storm.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_alien.bl_idname, text=STRATUS_OT_alien.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_hell.bl_idname, text=STRATUS_OT_hell.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_full_moon.bl_idname, text=STRATUS_OT_full_moon.bl_label, icon="NONE")
        layout.operator(STRATUS_OT_blood_moon.bl_idname, text=STRATUS_OT_blood_moon.bl_label, icon="NONE")