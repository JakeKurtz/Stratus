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
from .main_panel import (STRATUS_PT_main, STRATUS_main_Properties)

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
        default = False,
        update=update_prop
        )

    moon_silver_intsty: FloatProperty(
        name = "Silverline Intensity",
        description="Intensity of the bright outline along the edge of the clouds.",
        default=3.0,
        min= 0.0,
        update=update_prop
        ) 

    moon_silver_spread: FloatProperty(
        name = "Silverline Spread",
        description="The spread of the bright outline along the edge of the clouds.",
        default=0.02,
        min= 0.0,
        max = 1.0,
        update=update_prop
        ) 

    moon_size: FloatProperty(
        name = "Size",
        description = "Size of Moon.",
        default = radians(6.3),
        subtype="ANGLE",
        min = 0.0,
        max = radians(90.0),
        update=update_prop
        )
        
    moon_intsty: FloatProperty(
        name = "Intensity",
        description = "Strength of Moon disk.",
        default = 1.0,
        min = 0.0,
        max = 1000.0,
        update=update_prop
        )    

    moon_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "Strength of Moon ambient light.",
        default = 0.0,
        min = 0.0,
        max = 0.01,
        update=update_prop
        )
        
    moon_elevation: FloatProperty(
        name = "Elevation",
        description = "Moon Angle from horizon.",
        default = radians(13.0),
        subtype="ANGLE",
        update=update_prop
        )
        
    moon_rotation: FloatProperty(
        name = "Rotation",
        description = "Rotation of Moon around zenith.",
        default = radians(182.0),
        subtype="ANGLE",
        update=update_prop
        )

    moon_use_sun_dir: BoolProperty(
        name="Use Sun",
        description="Phase is based on tthe direction of the Sun.",
        default = False,
        update=update_prop
        )

    moon_phase_rotation: FloatProperty(
        name = "Rotation",
        description = "A float property",
        default = radians(130.0),
        subtype="ANGLE",
        update=update_prop
        )    
        
    moon_face_rotation: FloatProperty(
        name = "Face Rotation",
        description = "A float property",
        default = radians(60.0),
        subtype="ANGLE",
        update=update_prop
        )
        
    moon_phase: FloatProperty(
        name = "Phase",
        description = "A float property",
        default = radians(-125.0),
        subtype="ANGLE",
        update=update_prop
        )

    moon_pinned: BoolProperty(
        default=False
    )

class STRATUS_PT_moon(Panel):
    bl_label = "Moon"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        scene = context.scene
        main_prop = scene.main_props
        prop = scene.moon_props
        return (main_prop.panels == "CELE" or prop.moon_pinned)

    def draw_header(self, context):
        scene = context.scene
        prop = scene.moon_props
        
        the_icon = 'PINNED' if prop.moon_pinned else 'UNPINNED'
        self.layout.prop(prop, "moon_pinned", text="", icon=the_icon)

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
        
        layout.prop(prop, "moon_size")

        layout.separator()
        layout.prop(prop, "moon_enable_light")
        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.prop(prop, "moon_intsty")
        grid_0.prop(prop, "moon_ambient_intsty", slider=True)

        layout.separator()
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.prop(prop, "moon_elevation")
        grid_1.prop(prop, "moon_rotation")
        grid_1.prop(prop, "moon_face_rotation")

class STRATUS_PT_moon_phase(Panel):
    bl_parent_id = "STRATUS_PT_moon"
    bl_label = "Phase"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.moon_props

        layout.prop(prop, "moon_use_sun_dir")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.prop(prop, "moon_phase")
        grid_2.prop(prop, "moon_phase_rotation")

        grid_2.enabled = not prop.moon_use_sun_dir