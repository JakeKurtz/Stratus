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

class STRATUS_MoonProperties(PropertyGroup):
    moon_show_viewport: BoolProperty(
        name="",
        description="Display Moon in viewport.",
        default = True,
        update=update_prop
        )
        
    moon_show_render: BoolProperty(
        name="",
        description="Display Moon in render.",
        default = True,
        update=update_prop
        )

    moon_enable_light: BoolProperty(
        name="Light Source",
        description="Enable the Moon as a light source.",
        default = True,
        update=update_prop
        )

    moon_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Intensity of the bright outline along the edge of the clouds.",
        default=1.13,
        min= 0.0,
        update=update_prop
        ) 

    moon_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="The spread of the bright outline along the edge of the clouds.",
        default=0.12,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    moon_size: FloatProperty(
        name = "Size",
        description = "Size of Moon.",
        default = 0.545,
        subtype="ANGLE",
        min = 0.0,
        max = 90.0,
        update=update_prop
        )
        
    moon_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Moon light.",
        default = 1.0,
        min = 0.0,
        update=update_prop
        )    
        
    moon_disk_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Moon Disk.",
        default = 1.0,
        min = 0.0,
        update=update_prop
        )

    moon_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "Strength of Moon Face light.",
        default = 1.0,
        min = 0.0,
        max = 0.01,
        update=update_prop
        )
        
    moon_elevation: FloatProperty(
        name = "Elevation",
        description = "Moon Angle from horizon.",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    moon_rotation: FloatProperty(
        name = "Rotation",
        description = "Rotation of Moon around zenith.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    moon_use_sun_dir: BoolProperty(
        name="Use Sun",
        description="Phase is based on direction of the Sun.",
        default = False,
        update=update_prop
        )

    moon_phase_rotation: FloatProperty(
        name = "Phase Rotation",
        description = "A float property",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )    
        
    moon_face_rotation: FloatProperty(
        name = "Face Rotation",
        description = "A float property",
        default = 15.0,
        subtype="ANGLE",
        update=update_prop
        )
        
    moon_phase: FloatProperty(
        name = "Phase",
        description = "A float property",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

class STRATUS_PT_moon_panel(Panel):
    bl_label = "Moon"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.moon_props

        icon_vp = 'RESTRICT_VIEW_OFF' if prop.moon_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.moon_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Moon")
        render_options.prop(prop, 'moon_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'moon_show_render', icon=icon_r)
        
        layout.separator()
        layout.prop(prop, "moon_size")

        layout.separator()
        layout.prop(prop, "moon_enable_light")
        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "moon_disk_intsty")
        grid_0.prop(prop, "moon_ambient_intsty", slider=True)
        grid_0.prop(prop, "moon_silver_intsty")
        grid_0.prop(prop, "moon_silver_spread")

        layout.separator()
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "moon_elevation")
        grid_1.prop(prop, "moon_rotation")
        
        layout.separator()
        layout.prop(prop, "moon_use_sun_dir")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.prop(prop, "moon_phase")
        grid_2.prop(prop, "moon_phase_rotation")
        grid_2.prop(prop, "moon_face_rotation")

        #grid_0.enabled = prop.moon_enable_light
        #grid_2.enabled = not prop.moon_use_sun_dir