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

class STRATUS_SunProperties(PropertyGroup):
    sun_show_viewport: BoolProperty(
        name="",
        description="Display Sun in viewport.",
        default = True,
        update=update_prop
        )
        
    sun_show_render: BoolProperty(
        name="",
        description="Display Sun in render.",
        default = True,
        update=update_prop
        )

    sun_enable_light: BoolProperty(
        name="Light Source",
        description="Enable the Sun as a light source.",
        default = True,
        update=update_prop
        )

    sun_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Intensity of the bright outline along the edge of the clouds.",
        default=3.0,
        min= 0.0,
        update=update_prop
        ) 

    sun_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="The spread of the bright outline along the edge of the clouds.",
        default=0.02,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    sun_size: FloatProperty(
        name = "Size",
        description = "Size of Sun.",
        default = radians(0.545),
        subtype="ANGLE",
        min = 0.0,
        max = radians(90.0),
        update=update_prop
        )

    sun_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Sun disk.",
        default = 1.0,
        min = 0.0,
        max = 1000.0,
        update=update_prop
        )
        
    sun_elevation: FloatProperty(
        name = "Elevation",
        description = "Sun Angle from horizon.",
        default = radians(90.0),
        subtype="ANGLE",
        update=update_prop
        )
        
    sun_rotation: FloatProperty(
        name = "Rotation",
        description = "Rotation of Sun around zenith.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

class STRATUS_PT_sun_panel(Panel):
    bl_label = "Sun"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.sun_props

        icon_vp = 'RESTRICT_VIEW_OFF' if prop.sun_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.sun_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Sun")
        render_options.prop(prop, 'sun_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'sun_show_render', icon=icon_r)
        
        layout.separator()
        layout.prop(prop, "sun_size")

        layout.separator()
        layout.prop(prop, "sun_enable_light")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "sun_intsty")
        grid_0.prop(prop, "sun_silver_intsty")
        grid_0.prop(prop, "sun_silver_spread")

        layout.separator()
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "sun_elevation")
        grid_1.prop(prop, "sun_rotation")

        grid_0.enabled = prop.sun_enable_light