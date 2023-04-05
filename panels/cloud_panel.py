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
        description="Display clouds in viewport.",
        default = True,
        update=update_prop
        )
        
    cld_show_render: BoolProperty(
        name="",
        description="Display clouds in render.",
        default = True,
        update=update_prop
        )

    cld_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.5,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "The intensity of ambient light coming from the atmosphere.",
        default = 3.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_G: FloatProperty(
        name = "G",
        description = "A float property",
        default = 0.0,
        max = 1.0,
        min = -1.0,
        update=update_prop
        )           

# ------------------------- Cloud Layer 0 Properties ------------------------- #

    cld_0_enable: BoolProperty(
        name="",
        description="Enable cirro cloud layer.",
        default = True,
        update=update_prop
    )

    cld_0_density: FloatProperty(
        name = "Density",
        description = "Cloud layer density.",
        default = 0.25,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_density_height: FloatProperty(
        name = "Density Height",
        description = "Cloud layer density height.",
        default = 0.45,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_size: FloatProperty(
        name = "Size",
        description="Cloud layer size.",
        default=1.0,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 

    cld_0_height: FloatProperty(
        name = "Height",
        description="Height from sea level.",
        subtype="DISTANCE",
        default=8000,
        min= 7000,
        max = 10000.0,
        update=update_prop
        )  

    cld_0_thickness: FloatProperty(
        name = "Thickness",
        description = "Cloud layer thickness.",
        default = 0.9,
        min = 0.01,
        max = 1.0,
        update=update_prop
        )    
        
    cld_0_powder_intsty: FloatProperty(
        name = "Powder Intensity",
        description = "Intensity of the powder effect.",
        default = 0.5,
        min = 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_0_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.5,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_0_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "The intensity of ambient light coming from the atmosphere.",
        default = 3.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_0_atten: FloatProperty(
        name = "Attenuation",
        description = "",
        default = 0.5,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_0_contr: FloatProperty(
        name = "Contribution",
        description = "",
        default = 0.5,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_eccen: FloatProperty(
        name = "Eccentricity Attenuation",
        description = "",
        default = 0.5,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )

    cld_0_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Intensity of detail noise applied to cloud layer.",
        default=-0.024,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_0_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Intensity of shape noise applied to cloud layer.",
        default=-0.17,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_0_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Intensity of coverage noise applied to cloud layer.",
        default=0.87,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )
    
    cld_0_coverage_shape: FloatProperty(
        name = "Coverage Shape",
        description = "Interpolates between coverage noise maps.",
        default = 0.36,
        max = 1.0,
        min = 0.0,
        update=update_prop
        ) 
        
    cld_0_rotation: FloatProperty(
        name = "Rotation",
        description = "Cloud layer rotation.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    cld_0_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Coverage noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(936,0),
        update=update_prop
        )

    cld_0_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Shape noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        )

    cld_0_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Detail noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        default=(0,0),
        step = 1,
        update=update_prop
        ) 

# ------------------------- Cloud Layer 1 Properties ------------------------- #

    cld_1_enable: BoolProperty(
        name="",
        description="Enable cumulus cloud layer.",
        default = True,
        update=update_prop
    )

    cld_1_density: FloatProperty(
        name = "Density",
        description = "Cloud layer density.",
        default = 0.2,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_density_height: FloatProperty(
        name = "Density Height",
        description = "Cloud layer density height.",
        default = 0.45,
        max = 1.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_size: FloatProperty(
        name = "Size",
        description="Cloud layer size.",
        default=0.45,
        min= 0.0,
        max = 1,
        update=update_prop
        ) 

    cld_1_height: FloatProperty(
        name = "Height",
        description="Height from sea level.",
        subtype="DISTANCE",
        default=2000,
        min= 500.0,
        max = 2000.0,
        update=update_prop
        )  
          
    cld_1_thickness: FloatProperty(
        name = "Thickness",
        description = "Cloud layer thickness.",
        default = 2.5,
        min = 0.01,
        max = 2.5,
        update=update_prop
        )

    cld_1_powder_intsty: FloatProperty(
        name = "Powder Intensity",
        description = "Intensity of the powder effect.",
        default = 1.0,
        min = 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_1_ap_intsty: FloatProperty(
        name = "Atmospheric Perspective Intensity",
        description="The effect the atmosphere has on the appearance of the clouds as viewed from a distance.",
        default=0.5,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_1_ambient_intsty: FloatProperty(
        name = "Ambient Intensity",
        description = "The intensity of ambient light coming from the atmosphere.",
        default = 3.0,
        max = 100.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_1_atten: FloatProperty(
        name = "Attenuation",
        description = "",
        default = 0.5,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )    
        
    cld_1_contr: FloatProperty(
        name = "Contribution",
        description = "",
        default = 0.5,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_eccen: FloatProperty(
        name = "Eccentricity Attenuation",
        description = "",
        default = 0.5,
        max = 10.0,
        min = 0.0,
        update=update_prop
        )

    cld_1_detail_intsty: FloatProperty(
        name = "Detail Noise Intensity",
        description="Intensity of detail noise applied to cloud layer.",
        default=0.05,
        min = -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_1_shape_intsty: FloatProperty(
        name = "Shape Noise Intensity",
        description="Intensity of shape noise applied to cloud layer.",
        default=0.23,
        min= -1.0,
        max = 1.0,
        update=update_prop
        ) 

    cld_1_coverage_intsty: FloatProperty(
        name = "Coverage Noise Intensity",
        description="Intensity of coverage noise applied to cloud layer.",
        default=0.62,
        min= 0.0,
        max = 1.0,
        update=update_prop
        )

    cld_1_coverage_shape: FloatProperty(
        name = "Coverage Shape",
        description = "Interpolates between coverage noise maps.",
        default = 0.1,
        max = 1.0,
        min = 0.0,
        update=update_prop
        ) 

    cld_1_rotation: FloatProperty(
        name = "Rotation",
        description = "Cloud layer rotation.",
        default = 0.0,
        subtype="ANGLE",
        update=update_prop
        )

    cld_1_coverage_offset: FloatVectorProperty(
        name = "Coverage Noise Offset",
        description="Coverage noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(3671,9425),
        update=update_prop
        )

    cld_1_shape_offset: FloatVectorProperty(
        name = "Shape Noise Offset",
        description="Shape noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
        )

    cld_1_detail_offset: FloatVectorProperty(
        name = "Detail Noise Offset",
        description="Detail noise texture offset.",
        subtype='TRANSLATION',
        size = 2,
        step = 1,
        default=(0,0),
        update=update_prop
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
        grid_0.prop(prop, "cld_0_density_height", slider=True)
        grid_0.prop(prop, "cld_0_size", slider=True)
        grid_0.prop(prop, "cld_0_height", slider=True)
        grid_0.prop(prop, "cld_0_thickness", slider=True)

        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Lighting")

        grid_1.prop(prop, "cld_0_powder_intsty", slider=True)
        grid_1.prop(prop, "cld_0_ap_intsty", slider=True)
        grid_1.prop(prop, "cld_0_ambient_intsty")
        grid_1.prop(prop, "cld_0_atten")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.label(text="Noise")

        grid_2.prop(prop, "cld_0_detail_intsty", slider=True)
        grid_2.prop(prop, "cld_0_shape_intsty", slider=True)
        grid_2.prop(prop, "cld_0_coverage_intsty", slider=True)
        grid_2.prop(prop, "cld_0_coverage_shape", slider=True)
        
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
        grid_0.prop(prop, "cld_1_density_height", slider=True)
        grid_0.prop(prop, "cld_1_size", slider=True)
        grid_0.prop(prop, "cld_1_height", slider=True)
        grid_0.prop(prop, "cld_1_thickness", slider=True)

        grid_1 = layout.grid_flow(columns=1, align=True)
        grid_1.label(text="Lighting")

        grid_1.prop(prop, "cld_1_powder_intsty", slider=True)
        grid_1.prop(prop, "cld_1_ap_intsty", slider=True)
        grid_1.prop(prop, "cld_1_ambient_intsty")

        grid_1.prop(prop, "cld_1_atten")

        grid_2 = layout.grid_flow(columns=1, align=True)
        grid_2.label(text="Noise")

        grid_2.prop(prop, "cld_1_detail_intsty", slider=True)
        grid_2.prop(prop, "cld_1_shape_intsty", slider=True)
        grid_2.prop(prop, "cld_1_coverage_intsty", slider=True)
        grid_2.prop(prop, "cld_1_coverage_shape", slider=True)

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
