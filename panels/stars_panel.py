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
from math import radians
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )                
from bpy.types import (Panel,
                       PropertyGroup,
                       )
                       
from .panel_utils import update_prop

class STRATUS_StarsProperties(PropertyGroup):
    stars_show_viewport: BoolProperty(
        name="",
        description="Display stars in viewport.",
        default = True,
        update=update_prop
        )
        
    stars_show_render: BoolProperty(
        name="",
        description="Display stars in render.",
        default = True,
        update=update_prop
        )

    stars_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of stars.",
        default = 1.0,
        min = 0.0,
        max = 1000.0,
        update=update_prop
        )
        
    stars_elevation: FloatProperty(
        name = "Elevation",
        description = "Stars angle from horizon.",
        default = radians(90.0),
        subtype="ANGLE",
        update=update_prop
        )
        
    stars_rotation: FloatProperty(
        name = "Rotation",
        description = "Rotation of stars around zenith.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    stars_pole_elevation: FloatProperty(
        name = "Celestial Pole Elevation",
        description = "Celestial pole angle from horizon.",
        default = radians(90.0),
        subtype="ANGLE",
        update=update_prop
        )
        
    stars_pole_rotation: FloatProperty(
        name = "Celestial Pole Rotation",
        description = "Rotation of celestial pole around zenith.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    stars_show_pole: BoolProperty(
        name="Celestial Poles Visualizer",
        description="Display celestial pole visualizer.",
        default = False,
        update=update_prop
        )

class STRATUS_PT_stars_panel(Panel):
    bl_label = "Stars"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.stars_props

        icon_vp = 'RESTRICT_VIEW_OFF' if prop.stars_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.stars_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Stars")
        render_options.prop(prop, 'stars_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'stars_show_render', icon=icon_r)

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "stars_intsty")

        layout.separator()
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "stars_rotation")

        layout.separator()
        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.prop(prop, "stars_show_pole")
        grid_2.prop(prop, "stars_pole_elevation")
        grid_2.prop(prop, "stars_pole_rotation")