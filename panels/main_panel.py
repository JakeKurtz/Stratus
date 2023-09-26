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
from bpy.props import (BoolProperty, EnumProperty)            
from bpy.types import (Panel, PropertyGroup,)
from .. import globals

def enum_panels(self, context):
    blah = [
        ('CIRR','','Cirrus Properties', globals.CIRR_ICON, 0),
        ('CUMU','','Cumulus Properties', globals.CUMU_ICON, 1), 
        ('CELE','','Celestial Properties', globals.CELE_ICON, 2),
        ('REND','','Rendering Properties','SCENE', 3),
        ('PRES','','Presets','SEQ_PREVIEW', 4),
    ]
    return blah

class STRATUS_main_Properties(PropertyGroup):

    panels: EnumProperty(
        name="Stratus",
        items=enum_panels,
        description="",
        default=0
    )

class STRATUS_PT_main(Panel):
    bl_label = "Main Panel"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.main_props

        grid = layout.grid_flow(columns=5, align=True)
        grid.prop(prop, 'panels', expand=True)