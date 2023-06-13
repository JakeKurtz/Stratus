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

class STRATUS_main_Properties(PropertyGroup):
    enum_panels = [
        ('CIRR','','Cirrus Properties','COLORSET_02_VEC', 0),
        ('CUMU','','Cumulus Properties','COLORSET_04_VEC', 1), 
        ('CELE','','Celestial Properties','COLORSET_05_VEC', 2),
        ('REND','','Rendering Properties','SCENE', 3),
    ]

    panels: EnumProperty(
        name="Stuff",
        items=enum_panels,
        description="",
        default="CIRR"
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