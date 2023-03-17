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

class STRATUS_CloudProperties(PropertyGroup):
    cld_show_viewport: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
        )
        
    cld_show_render: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
        )

    cld_ambient_intsty: FloatProperty(
        name = "cld_ambient_intsty",
        description = "A float property",
        default = 1.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )      
        
    cld_horizon_dst: FloatProperty(
        name = "cld_horizon_dst",
        description = "A float property",
        default = 10000.0,
        max = 100000.0,
        step = 1000,
        min = 0.0,
        update=update_prop
        )      
        
    cld_horizon_h: FloatProperty(
        name = "cld_horizon_h",
        description = "A float property",
        default = 6500.0,
        max = 100000.0,
        step = 1000,
        min = 0.0,
        update=update_prop
        )  

    cld_top_roundness: FloatProperty(
        name = "cld_top_roundness",
        description = "A float property",
        default = 0.05,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_btm_roundness: FloatProperty(
        name = "cld_btm_roundness",
        description = "A float property",
        default = 0.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )    

    cld_top_density: FloatProperty(
        name = "cld_top_density",
        description = "A float property",
        default = 1.0,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )  

    cld_btm_density: FloatProperty(
        name = "cld_btm_density",
        description = "A float property",
        default = 0.5,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

# ------------------------- Cloud Layer 0 Properties ------------------------- #

    cld_0_enable: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
    )

    cld_0_density: FloatProperty(
        name = "Density",
        description = "A float property",
        default = 0.1,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_size: FloatProperty(
        name = "Size",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 

    cld_0_height: FloatProperty(
        name = "Height",
        description="Something",
        subtype="DISTANCE",
        default=8000,
        min= 7000,
        max = 10000.0,
        update=update_prop
        )  

    cld_0_thickness: FloatProperty(
        name = "Thickness",
        description = "A float property",
        default = 1.15,
        min = 0.01,
        max = 2.5,
        update=update_prop
        )

    cld_0_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Something",
        default=0.02,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_0_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Something",
        default=-0.55,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_0_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Something",
        default=1.0,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )
        
    cld_0_rotation: FloatProperty(
        name = "Rotation",
        description = "",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
    )

    cld_0_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        step = 100,
        default=(750,0),
        update=update_prop
        )

    cld_0_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        )

    cld_0_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        ) 

# ------------------------- Cloud Layer 1 Properties ------------------------- #

    cld_1_enable: BoolProperty(
        name="",
        description="A bool property",
        default = True,
        update=update_prop
    )

    cld_1_density: FloatProperty(
        name = "Density",
        description = "A float property",
        default = 0.25,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_size: FloatProperty(
        name = "Size",
        description="Something",
        default=0.5,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 

    cld_1_height: FloatProperty(
        name = "Height",
        description="Something",
        subtype="DISTANCE",
        default=2000,
        min= 500.0,
        max = 2000.0,
        update=update_prop
        )  
          
    cld_1_thickness: FloatProperty(
        name = "Thickness",
        description = "A float property",
        default = 1.3,
        min = 0.01,
        max = 2.5,
        update=update_prop
        )

    cld_1_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Something",
        default=0.1,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_1_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Something",
        default=0.3,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_1_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Something",
        default=0.55,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_1_rotation: FloatProperty(
        name = "Rotation",
        description = "",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
    )

    cld_1_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        step = 100,
        default=(0,0),
        update=update_prop
        )

    cld_1_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        )

    cld_1_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Something",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        update=update_prop
        ) 

    cld_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.2,
        update=update_prop,
        min= 0.0,
        max = 100.0
        )

    cld_coverage_map: PointerProperty(
        name="Image", 
        type=bpy.types.Image,
        #update=update_cld_coverage_map
        )

class STRATUS_PT_cloud_panel(Panel):
    bl_label = "Clouds"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props
        
        icon_vp = 'RESTRICT_VIEW_OFF' if prop.cld_show_viewport else "RESTRICT_VIEW_ON"
        icon_r = 'RESTRICT_RENDER_OFF' if prop.cld_show_render else "RESTRICT_RENDER_ON"

        render_options = layout.row(align=True)
        render_options.label(text="Clouds")
        render_options.prop(prop, 'cld_show_viewport', icon=icon_vp)
        render_options.prop(prop, 'cld_show_render', icon=icon_r)

        col = layout.column()
        col.label(text="Lighting")
        col.prop(prop, "cld_ap_intsty")
        col.prop(prop, "cld_top_roundness")
        col.prop(prop, "cld_btm_roundness")
        col.prop(prop, "cld_top_density")
        col.prop(prop, "cld_btm_density")
        col.prop(prop, "cld_ambient_intsty")
        col.prop(prop, "cld_horizon_dst")
        col.prop(prop, "cld_horizon_h")

class STRATUS_PT_sub_cloud_layer_0_panel(Panel):
    bl_parent_id = "STRATUS_PT_cloud_panel"
    bl_label = "Cirro Layer"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.cloud_props, "cld_0_enable")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props

        layout.enabled = prop.cld_0_enable

        layout.prop(prop, "cld_0_rotation")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.label(text="Basic")

        grid_0.prop(prop, "cld_0_density", slider=True)
        grid_0.prop(prop, "cld_0_size", slider=True)
        grid_0.prop(prop, "cld_0_height", slider=True)
        grid_0.prop(prop, "cld_0_thickness", slider=True)
        
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Noise")

        grid_1.prop(prop, "cld_0_detail_intsty", slider=True)
        grid_1.prop(prop, "cld_0_shape_intsty", slider=True)
        grid_1.prop(prop, "cld_0_coverage_intsty", slider=True)
        
class STRATUS_PT_sub_cloud_layer_1_panel(Panel):
    bl_parent_id = "STRATUS_PT_cloud_panel"
    bl_label = "Cumulus Layer"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.prop(context.scene.cloud_props, "cld_1_enable")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props

        layout.enabled = prop.cld_1_enable

        layout.prop(prop, "cld_1_rotation")

        grid_0 = layout.grid_flow(columns=1, align=True)
        grid_0.label(text="Basic")

        grid_0.prop(prop, "cld_1_density", slider=True)
        grid_0.prop(prop, "cld_1_size", slider=True)
        grid_0.prop(prop, "cld_1_height", slider=True)
        grid_0.prop(prop, "cld_1_thickness", slider=True)
        
        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Noise")

        grid_1.prop(prop, "cld_1_detail_intsty", slider=True)
        grid_1.prop(prop, "cld_1_shape_intsty", slider=True)
        grid_1.prop(prop, "cld_1_coverage_intsty", slider=True)

class STRATUS_PT_sub_cloud_layer_0_noise_offsets_panel(Panel):
    bl_parent_id = "STRATUS_PT_sub_cloud_layer_0_panel"
    bl_label = "Noise Offsets"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props

        layout.enabled = prop.cld_0_enable

        grid = layout.grid_flow(columns=1, align=True)
        grid.prop(prop, "cld_0_coverage_offset")
        grid.prop(prop, "cld_0_shape_offset")
        grid.prop(prop, "cld_0_detail_offset")

class STRATUS_PT_sub_cloud_layer_1_noise_offsets_panel(Panel):
    bl_parent_id = "STRATUS_PT_sub_cloud_layer_1_panel"
    bl_label = "Noise Offsets"
    bl_category = "Stratus"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        prop = scene.cloud_props

        layout.enabled = prop.cld_1_enable

        grid = layout.grid_flow(columns=1, align=True)
        grid.prop(prop, "cld_1_coverage_offset")
        grid.prop(prop, "cld_1_shape_offset")
        grid.prop(prop, "cld_1_detail_offset")
