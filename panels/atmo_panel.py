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
                       
class STRATUS_AtmoProperties(PropertyGroup):
    prop_sky_altitude: FloatProperty(
        name = "Altitude",
        description = "Height from sea level.",
        default = 2000.0,
        subtype="DISTANCE",
        min = 0.0,
        update=update_prop
        )

    prop_air: FloatProperty(
        name = "Air",
        description="Density of air molecules.",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    prop_dust: FloatProperty(
        name = "Dust",
        description="Density of dust molecules and water droplets.",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    prop_ozone: FloatProperty(
        name = "Ozone",
        description="Density of ozone layer.",
        default=1.0,
        min= 0.0,
        max = 10.0,
        update=update_prop
        ) 
    
    atm_show_viewport: BoolProperty(
        name="",
        description="Display atmosphere in viewport.",
        default = True,
        update=update_prop
        )
        
    atm_show_render: BoolProperty(
        name="",
        description="Display atmosphere in render.",
        default = True,
        update=update_prop
        )

class STRATUS_PT_atmo_panel(Panel):
    bl_label = "Atmosphere"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.atmo_props
        
        icon_vp = 'RESTRICT_VIEW_OFF' if prop.atm_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.atm_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Atmosphere")
        render_options.prop(prop, 'atm_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'atm_show_render', icon=icon_r)
        
        layout.prop(prop, "prop_sky_altitude")
        layout.separator()
        grid = layout.grid_flow(columns=1, align=True)
        grid.prop(prop, "prop_air", slider=True)
        grid.prop(prop, "prop_dust", slider=True)
        grid.prop(prop, "prop_ozone", slider=True)